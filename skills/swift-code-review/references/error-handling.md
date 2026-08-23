# Swift Error-Handling Review Checks

> Adapted and rewritten for this collection; see [../NOTICE.md](../NOTICE.md).

Follow the error to its handling boundary. A throwing function does not need a
local `do/catch` when a caller intentionally propagates it, and a `try?` is not a
bug when collapsing a failure is part of the contract.

## `try!`, `try?`, and empty catches

```swift
let config = try! JSONDecoder().decode(Config.self, from: data) // runtime crash
```

Flag `try!` when the input can vary at runtime and the failure would crash a
supported path. A literal URL or a checked bundle invariant can justify a force
operation, but verify the invariant in the source rather than accepting a
comment as proof. `try?` is reasonable for optional cache reads, best-effort
cleanup, or feature detection when the lost error is deliberately unimportant.
Flag it when it hides a user-visible failure, prevents retry/recovery, or erases
diagnostic context without a replacement log/metric.

An empty `catch` is usually suspicious, but it can be correct for expected
cancellation or idempotent cleanup. Require a comment or surrounding contract
that explains why the error is intentionally ignored.

## Error boundaries and user messaging

Keep domain errors useful to callers and map them to localized, safe UI copy at
the presentation boundary. Do not require every internal error to conform to
`LocalizedError`, and do not expose raw server strings, file paths, tokens, or
debug details through `localizedDescription`.

```swift
enum ProfileError: Error {
    case network(underlying: any Error)
}

func message(for error: ProfileError) -> String {
    switch error {
    case .network:
        return String(localized: "profile.load_failed")
    }
}
```

When wrapping an error, preserve the underlying error for logging or recovery
unless the boundary intentionally redacts it. Check whether a higher-level
coordinator, view model, task, or delegate already owns the user-facing path
before reporting “missing handling.”

## Completion handlers

Legacy callback APIs must complete every path, including invalid input and early
returns, and should document the queue on which completion runs. Prefer an async
API when the deployment target and framework support it; do not ask a review to
add a new abstraction merely to satisfy this preference.

```swift
func fetchData(completion: @escaping (Result<Data, any Error>) -> Void) {
    guard let url = buildURL() else {
        completion(.failure(NetworkError.invalidURL))
        return
    }
    // Complete success and failure exactly once.
    load(url, completion: completion)
}
```

Inspect retries, cancellation, and callback ownership before calling a path
“never completes.” A completion can be fulfilled by a framework delegate or a
shared error boundary outside the function.

## Typed throws

Typed throws are available in current Swift language modes, but the project’s
toolchain and public API evolution policy decide whether to use them:

```swift
func readFile(at path: String) throws(FileError) -> Data {
    guard fileExists(path) else { throw .notFound }
    return try loadData(path)
}
```

Use typed throws when the concrete error contract improves composition and the
target supports it. Do not blanket-ban it from public APIs; instead consider
whether locking an API to a concrete failure type is intentional. Verify syntax
against the project’s Swift version and the [typed throws proposal](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md).

## Questions before reporting

1. Can this failure reach a supported runtime path, or is the invariant proven?
2. Is the error propagated, recovered, surfaced, or intentionally collapsed?
3. Did you inspect the caller and the framework/delegate error path first?
4. Does the user-facing boundary localize and redact the message appropriately?
5. Is callback completion exactly once on success, failure, cancellation, and
   early return?

## Primary references

- [Swift concurrency error propagation](https://sosumi.ai/documentation/swift/concurrency)
- [Swift Evolution: Typed throws](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md)
- [LocalizedError](https://sosumi.ai/documentation/foundation/localizederror)
