---
name: swift-testing
description: "Write, review, or migrate Swift unit tests using Swift Testing, while preserving XCTest/XCUITest where their APIs are still required. Use for test design, async behavior, traits, parameterization, migration boundaries, and version-gated testing APIs."
---

# Swift Testing

Write deterministic tests around observable behavior and keep the framework choice proportional to the target and API under test.

## Scope and Preflight

This skill owns Swift Testing syntax, suite organization, traits, parameterization, async tests, known issues, attachments, exit tests, and XCTest migration boundaries. Route UI implementation to UI skills and concurrency design—not merely async test syntax—to `swift-concurrency`.

Inspect the Xcode/Swift toolchain, target platform, test target type, current framework, and CI invocation before recommending APIs. Preserve a mixed XCTest/Swift Testing suite when migration offers no concrete benefit. Verify versioned test APIs against Swift Evolution, release notes, SDK interfaces, or primary documentation.

## Framework Choice

| Need | Prefer |
|---|---|
| New unit or integration tests in a supported Swift target | Swift Testing |
| Existing XCTest suite with no migration pressure | Keep XCTest and migrate incrementally |
| UI automation | XCUITest/XCTest |
| XCTest performance measurement APIs | XCTest |
| Objective-C exception testing or tooling that requires XCTestCase | XCTest |
| Common snapshot frameworks tied to XCTest | Keep the supported XCTest integration |

Do not turn migration into an all-or-nothing rewrite.

## Core Patterns

- Use `@Test` and `@Suite` to express behavior and organization.
- Use `#expect` for independent checks and `try #require` when later assertions depend on an unwrapped or validated value.
- Use parameterized tests for the same behavior across inputs.
- Apply traits for tags, conditions, time limits, known bugs, and serialization only when their semantics match the test.
- Tests run in parallel by default; isolate mutable fixtures instead of depending on declaration order.
- Name tests by behavior and outcome, not implementation details.

Read [Testing Patterns](references/testing-patterns.md) for suite organization, traits, confirmation, mocks, parameterization, execution behavior, and migration examples.

## Async and Failure Behavior

Prefer deterministic signals, injected clocks, and `confirmation` over sleeps or polling. Test error, cancellation, and cleanup paths explicitly when production behavior supports them. Keep UI-bound test code on `@MainActor`; do not annotate an entire test suite merely to silence unrelated isolation errors.

Use protocol- or closure-based dependencies when they provide a real seam. Avoid mocks that reproduce implementation details instead of controlling observable inputs and outputs.

## Advanced and Version-Gated APIs

Attachments, warning severity, test cancellation, and exit-test capture behavior vary by toolchain and platform. Read [Advanced Testing](references/testing-advanced.md) and state the exact gate beside any correction.

Exit testing is not available on every Apple runtime target. For an iOS app target, isolate fatal-path logic into a testable non-exiting unit or use a supported host/tool target rather than claiming an unavailable API works on-device.

## Migration

Map behavior, not assertion spelling:

- `XCTAssert*` usually maps to `#expect`
- `XCTUnwrap` maps to `try #require`
- fulfillment-based async tests may map to `confirmation`
- `setUp`/`tearDown` state usually becomes suite initialization and scoped cleanup

Keep XCTest cases that rely on APIs without a Swift Testing equivalent. Run both frameworks in the same test plan during incremental migration.

## Review Checklist

- [ ] Framework choice matches target and required APIs
- [ ] Test names describe behavior and meaningful failures
- [ ] Required values use `#require`; independent checks use `#expect`
- [ ] Repetitive cases are parameterized where clearer
- [ ] Async tests use deterministic signaling rather than sleeps
- [ ] Error, cancellation, and cleanup paths are covered
- [ ] Fixtures do not leak shared mutable state across parallel tests
- [ ] Serialization protects an exclusive resource, not workflow ordering
- [ ] Version-gated APIs match the installed toolchain and runtime
- [ ] Migration preserves test intent and CI execution

## References

- [Core patterns, organization, mocks, and migration](references/testing-patterns.md)
- [Advanced and version-gated APIs](references/testing-advanced.md)
