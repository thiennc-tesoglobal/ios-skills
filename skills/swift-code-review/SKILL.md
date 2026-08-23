---
name: swift-code-review
description: "Review changed Swift and SwiftUI code for correctness, concurrency, ownership, error propagation, Observation state, and API/lifecycle risks. Use for pull requests, diffs, or focused code reviews; route framework-specific work to the collection's specialist skills instead of duplicating it."
license: Apache-2.0
---

# Swift Code Review

> Adapted and rewritten for this collection; see [NOTICE.md](NOTICE.md) and [LICENSE-APACHE-2.0.txt](LICENSE-APACHE-2.0.txt).

Review code as an evidence-backed diff review, not as a style sweep. Report only
issues that can change correctness, safety, user-visible behavior, or maintenance
cost. Keep the review self-contained and use the references below only when their
topics appear in the code.

## Scope and boundaries

- Review changed `.swift` files and the directly related callers, parents, and
  tests. If no diff is supplied, ask for or identify an explicit file list before
  reporting issues.
- Record the concrete Swift language mode, deployment target, and relevant build
  settings from `Package.swift`, the project, or the target. Do not give
  version-specific advice from memory.
- Treat SwiftLint as the authority for configured style rules. Do not duplicate a
  passing linter rule as a semantic finding.
- This skill owns cross-cutting Swift correctness. Route focused work to
  `swift-concurrency`, `swiftui-patterns`, `swiftui-responsive-layout`,
  `swiftui-performance`, `ios-accessibility`, `swift-security`,
  `ios-networking`, `swiftdata`, `storekit`, `push-notifications`, or another
  matching specialist when that framework or symptom is the primary concern.

## Review workflow

Follow this order so that a plausible-looking hunch does not become a false
positive:

1. **Capture scope.** List changed Swift paths (or state that none are in scope),
   read repository instructions, inspect SwiftLint configuration, and note the
   toolchain/deployment baseline. If a SwiftLint config exists and the binary is
   available, run `swiftlint lint --quiet` on the scoped paths and record the
   result before reporting style-related issues.
2. **Read context.** Read the full enclosing type/function/property for every
   candidate finding, then inspect the immediate caller, parent view, coordinator,
   or error boundary. Read comments and tests that explain intentional behavior.
3. **Select checks.** Apply only relevant checklist rows and load the matching
   reference: concurrency, Observation, error handling, or common Swift mistakes.
4. **Check usages and framework contracts.** Search before calling a symbol
   unused; check upstream validation and framework callbacks before calling
   handling missing. Verify syntax and availability against current primary docs
   when an API claim matters.
5. **Verify each finding.** Re-read the exact line and surrounding control flow.
   Separate confirmed defects from code-only hypotheses (especially performance),
   and remove style preferences or unlikely hypothetical issues.
6. **Calibrate severity.** Use Critical only for security, data corruption,
   happy-path crashes, or breaking public API changes. Use Major for material
   behavior, error, accessibility, or measurable performance problems. Use Minor
   for clarity, docs, and bounded test gaps. Use Informational for future
   architecture or net-new infrastructure.

## Output contract

Use this compact, actionable format:

```markdown
## Review Summary

Scope: <files or no Swift files>
Baseline: <Swift/language mode/deployment target, or unknown>
Checks: <references and specialist boundaries applied>

## Issues

### Critical (Blocking)

1. [Sources/File.swift:42] ISSUE_TITLE
   - Issue: <what the code does>
   - Why: <observable impact>
   - Fix: <smallest safe correction>

### Major (Should Fix)

### Minor (Consider Fixing)

### Informational (For Awareness)

## Good Patterns

- [Sources/File.swift:18] <specific behavior worth preserving>

## Verdict

Ready: Yes | No | With fixes 1-N
Rationale: <one or two sentences>
```

Every issue needs an exact `[FILE:LINE]` proof and a severity. If there are no
issues, say `Protocol applied; no issues` and explain the scope checked. Do not
invent findings to fill a section.

## Cross-cutting checklist

- [ ] Runtime optionals, indexing, casts, and `try!`/force unwraps have a proven
      invariant or an explicit failure path.
- [ ] Stored closures, delegates, tasks, and subscriptions have an intentional
      ownership and cancellation story; do not demand `[weak self]` mechanically.
- [ ] Actor state remains valid across every suspension point; independent work is
      concurrent only when dependencies allow it; long work observes cancellation.
- [ ] `Sendable` and `@unchecked Sendable` claims match the actual synchronization
      and value semantics.
- [ ] Errors are either recovered, surfaced at the right boundary, or intentionally
      collapsed with the reason documented; no empty catch silently hides failure.
- [ ] Observation wrappers express ownership: `@State` owns view-local observable
      identity, `@Bindable` supplies two-way bindings, and non-observed dependencies
      are excluded deliberately.
- [ ] Findings do not duplicate specialist concerns. Route layout clipping/overlap,
      accessibility, security, networking, persistence, purchases, notifications,
      and measured performance to the relevant skill while preserving the review
      evidence and severity.

## References

- Concurrency, actors, cancellation, tasks, and `Sendable`: [references/concurrency.md](references/concurrency.md)
- Observation, `@State`, `@Bindable`, and environment ownership: [references/observation.md](references/observation.md)
- `throws`, `Result`, `try?`, typed throws, and error boundaries: [references/error-handling.md](references/error-handling.md)
- Optionals, ownership, IUOs, collection access, and naming: [references/common-mistakes.md](references/common-mistakes.md)
- For the verification gates used by this skill: [references/verification-protocol.md](references/verification-protocol.md)
