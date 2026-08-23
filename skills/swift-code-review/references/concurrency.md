# Swift Concurrency Review Checks

> Adapted and rewritten for this collection; see [../NOTICE.md](../NOTICE.md).

Review the dependency graph and lifetime, not just the presence of `async`.
Swift actors are reentrant at suspension points, and a task's ownership is part
of its correctness.

## Independent work

Use `async let` only after confirming that operations do not depend on one
another and that partial failure semantics are acceptable:

```swift
async let profileTask = fetchProfile()
async let flagsTask = fetchFeatureFlags()
let profile = try await profileTask
let flags = try await flagsTask
let result = ScreenData(profile: profile, flags: flags)
```

Sequential awaits are correct when the second request needs the first result, or
when ordering/rate limits are part of the contract. Use a task group when the
number of child tasks is dynamic; check whether unbounded fan-out needs a limit.

## Task lifetime, cancellation, and errors

An unstructured task should have an explicit owner, cancellation path, and error
policy. A stored task commonly gets cancelled before replacement and in
`deinit`; a SwiftUI view-owned operation usually belongs in `.task(id:)` so the
framework controls its lifetime. `Task {}` in `onAppear` is not automatically
wrong, but it is easy to leak or duplicate without a stored handle.

```swift
private var refreshTask: Task<Void, Never>?

func refresh() {
    refreshTask?.cancel()
    refreshTask = Task { [loader] in
        do {
            try Task.checkCancellation()
            let value = try await loader.load()
            try Task.checkCancellation()
            await apply(value)
        } catch is CancellationError {
            // Expected when a newer refresh replaces this one.
        } catch {
            await record(error)
        }
    }
}

deinit { refreshTask?.cancel() }
```

Do not require `[weak self]` by rote. If `self` owns the task, a strong capture
can keep the owner alive until the task finishes; that may be a leak for an
infinite sequence or the intended lifetime for a finite operation. Verify the
actual cycle and cancellation path. Likewise, a fire-and-forget task may
intentionally collapse errors, but the code should make that policy observable.

Long CPU loops and custom async sequences should check cancellation. An awaited
API may already do so; inspect its contract before reporting a missing check.

## Actor reentrancy

Every `await` inside an actor can allow another actor-isolated call to run before
the function resumes. Do not claim that “mutate before await” is always correct:
reserve state before suspension only when the operation has a rollback/failure
policy, or re-check the invariant after the await.

```swift
actor Inventory {
    private var available = 1

    func reserve() async throws {
        guard available > 0 else { throw StockError.empty }
        available -= 1                 // reserve the invariant
        do {
            try await persistReservation()
        } catch {
            available += 1              // compensate failed persistence
            throw error
        }
    }
}
```

Inspect all actor state read before an await and used after it, including cache
entries, authentication state, counters, and “check then mutate” sequences.

## Isolation and `Sendable`

Values crossing actor/task boundaries must be safe to share. Prefer immutable
value types that conform to `Sendable`, actor isolation, or a reference type with
auditable synchronization. `@unchecked Sendable` is a promise to the compiler;
flag it when the code does not show a lock, serial executor, immutable storage,
or another complete synchronization argument.

```swift
struct Session: Sendable {
    let token: String
}
```

A stateless actor is not automatically a bug. It may intentionally provide an
isolation boundary, but if it only adds needless actor hops, a value type or
free function can be considered as a measured cleanup. Do not report this as a
correctness issue without an observable cost or a violated isolation contract.

## Questions before reporting

1. Which operations are actually independent, and can they fail independently?
2. What happens if the task is cancelled or replaced while suspended?
3. Which actor state is read before and after each `await`?
4. Is `@unchecked Sendable` backed by complete synchronization?
5. Does the caller observe, recover, or intentionally ignore task errors?

## Primary references

- [Swift concurrency](https://sosumi.ai/documentation/swift/concurrency)
- [Task](https://sosumi.ai/documentation/swift/task)
- [Swift Evolution: Sendable closures](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0302-concurrent-value-and-concurrent-closures.md)
