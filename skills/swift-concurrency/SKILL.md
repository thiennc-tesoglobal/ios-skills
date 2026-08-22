---
name: swift-concurrency
description: "Diagnose Swift concurrency errors and design data-race-safe async code using actor isolation, Sendable, structured tasks, cancellation, and synchronization primitives. Use for compiler isolation diagnostics or concurrency behavior, not routine SwiftUI lifecycle wiring."
---

# Swift Concurrency

Apply the smallest change that makes isolation and ownership correct while preserving observable behavior.

## Scope and Toolchain Preflight

This skill owns compiler concurrency diagnostics, actor isolation, `Sendable`, task structure, cancellation, reentrancy, async sequences, continuations, and synchronization. Route routine SwiftUI `.task` ownership to `swiftui-patterns`, app architecture to `swift-architecture`, and test syntax to `swift-testing`.

Before recommending versioned language features, inspect:

- Xcode and Swift toolchain version
- Swift language mode and strict-concurrency setting
- Approachable Concurrency setting
- Default Actor Isolation setting
- deployment target when a runtime API is involved

Do not change project-wide isolation or language settings unless the request includes migration or build configuration. Verify new language/API claims against Swift Evolution, release notes, SDK headers, or primary Apple/Swift documentation.

## Diagnostic Workflow

1. Capture the exact diagnostic and declaration involved.
2. Identify current isolation, mutation owner, call direction, and values crossing the boundary.
3. Decide whether the operation is UI-bound, stateful background work, stateless work, or legacy interop.
4. Apply the narrowest safe fix and avoid broad escape hatches.
5. Rebuild, inspect new diagnostics, and test cancellation/failure behavior affected by the change.

Use [Diagnostics](references/diagnostics.md) for compiler-message-specific remedies and [Approachable Concurrency](references/approachable-concurrency.md) for build-setting semantics.

## Isolation Decisions

| Situation | Prefer |
|---|---|
| UI-bound mutable state | Type or relevant member isolated to `@MainActor` |
| Cohesive mutable background state | A dedicated actor |
| Immutable value crossing tasks | A genuinely `Sendable` value type |
| Stateless CPU-heavy async operation | An appropriately isolated/nonisolated concurrent function supported by the toolchain |
| Synchronous shared state | A suitable lock or synchronization primitive with a documented invariant |
| Callback/delegate API | A checked continuation or stream with exactly-once completion and cancellation cleanup |

Default MainActor isolation does not make every operation appropriate for the main actor. Keep CPU-heavy work, blocking I/O, and non-UI services off it. Conversely, do not remove isolation merely to silence a compiler error.

## Safety Rules

- Prefer structured child tasks over detached tasks so priority, task-local values, and cancellation propagate.
- Treat cancellation as cooperative: check it at meaningful boundaries and clean up resources.
- Revalidate actor state after every suspension point when intervening work could change it.
- Add `Sendable` only when the stored graph and mutation model make the conformance true.
- Use `@unchecked Sendable` or `nonisolated(unsafe)` only with a local, documented invariant and targeted verification.
- Never hold a synchronous lock across `await`.
- Do not place locks inside an actor to protect the actor's own state.
- Avoid semaphores and blocking waits on cooperative executor threads.
- A manual task needs a clear owner, cancellation point, and lifetime.

Read [Synchronization Primitives](references/synchronization-primitives.md) for locks versus actors, and [Concurrency Patterns](references/concurrency-patterns.md) for task groups, actors, cancellation, and reentrancy examples.

## Interop and Streams

Use checked continuations for one-shot callbacks and resume exactly once on every terminal path. Use `AsyncStream`/`AsyncThrowingStream` for multiple values and install termination cleanup for delegates, observers, or underlying operations.

Read [Bridging and Interop](references/bridging-interop.md) before adapting delegates, GCD, unsafe buffers, or synchronous parallel loops. Read [Async Algorithms](references/async-algorithms.md) for debounce, throttle, merge, and related sequence operations.

## Review Checklist

- [ ] Exact toolchain and concurrency settings are known when they matter
- [ ] Every mutable state graph has a clear isolation owner
- [ ] Cross-isolation values are safely transferable
- [ ] No blocking work runs on the main actor or cooperative pool
- [ ] Structured tasks are preferred; detached/manual tasks are justified
- [ ] Cancellation, failure, and resource cleanup are tested
- [ ] Actor state assumptions are reconsidered after `await`
- [ ] No unjustified `@unchecked Sendable`, `nonisolated(unsafe)`, or `@preconcurrency` remains
- [ ] Locks are synchronous, local, and never held across suspension
- [ ] The compiler diagnostic is gone without changing unrelated behavior

## References

- [Concurrency patterns and migration](references/concurrency-patterns.md)
- [Approachable Concurrency](references/approachable-concurrency.md)
- [SwiftUI-specific concurrency](references/swiftui-concurrency.md)
- [Synchronization primitives](references/synchronization-primitives.md)
- [Callbacks, GCD, and unsafe interop](references/bridging-interop.md)
- [Compiler diagnostics](references/diagnostics.md)
- [Async algorithms](references/async-algorithms.md)
