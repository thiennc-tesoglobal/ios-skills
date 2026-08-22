---
name: swiftui-patterns
description: "Structure and refactor SwiftUI views using Observation, clear state ownership, composition, and deterministic previews. Use for view architecture and data flow; route detailed layout, navigation, animation, performance, and visual effects to their dedicated skills."
---

# SwiftUI Patterns

Build SwiftUI features whose state ownership, dependencies, lifecycle work, and view boundaries are easy to understand and verify.

## Scope

This skill owns:

- Observation ownership and SwiftUI property-wrapper wiring
- view composition and feature boundaries
- environment dependency injection
- view-scoped async lifecycle work
- deterministic previews
- behavior-preserving view refactors

Route detailed containers and controls to `swiftui-layout-components`, navigation to `swiftui-navigation`, motion to `swiftui-animation`, runtime diagnosis to `swiftui-performance`, Liquid Glass to `swiftui-liquid-glass`, concurrency mechanics to `swift-concurrency`, and architecture selection beyond a single feature to `swift-architecture`.

## Compatibility Preflight

Inspect the project's deployment target, Swift language mode, and available SDK before recommending versioned APIs. Preserve those settings unless the user requests a change; gate newer APIs and verify availability against SDK headers or primary Apple/Swift documentation.

## Workflow

1. Record state owners, inputs, actions, side effects, navigation handoffs, identity, accessibility, and lifecycle behavior.
2. Choose the smallest structural change that preserves that contract.
3. Keep `body` declarative; move meaningful sections into dedicated views and non-trivial actions into thin named methods.
4. Build after a meaningful extraction or risky change, then render useful previews and exercise affected interactions.
5. If the request is structure-only, restore any changed behavior before continuing.

For an existing large view, read [Behavior-Preserving View Refactoring](references/view-refactoring.md). For project layout or naming work, read [Project Structure and File Naming](references/project-structure.md).

## State Ownership

| Tool | Use when |
|---|---|
| `@State` | The view owns a local value or `@Observable` instance. Keep it private unless an API genuinely requires broader access. |
| `let` | A child receives observable state but does not need bindings. |
| `@Bindable` | A child receives an `@Observable` value and needs `$property` bindings. |
| `@Binding` | A child edits state owned by its parent. |
| `@Environment(Type.self)` | A cohesive dependency or shared observable model is needed deeply in a subtree. |
| `@Query` | A SwiftData-backed view owns a live query. Route persistence details to `swiftdata`. |

UI-bound observable stores should normally be `@MainActor`. Domain values that cross isolation boundaries need an appropriate isolation strategy and, where correct, `Sendable`; do not mark every observable type `@MainActor` by habit.

Prefer lightweight MV for straightforward SwiftUI features. Introduce MVVM, MVI, TCA, or another boundary when concrete complexity justifies it, or preserve the architecture already established by the project. Use `swift-architecture` to make that choice.

## Composition

Keep a small stateless fragment as a computed `some View`. Extract a dedicated `View` when a section has one or more of these signals:

- meaningful branching or substantial layout
- its own state, focus, gesture, task, or lifecycle
- narrower dependencies than the parent
- useful independent preview states
- enough complexity to hide the parent's data flow

Pass only the values, bindings, and actions the child needs. A cohesive feature-scoped observable model is appropriate when many related inputs would otherwise travel together. Reuse is helpful but is not required for extraction.

Extensions and `// MARK:` headings organize source; they do not create runtime or ownership boundaries. Avoid replacing one oversized `body` with screen-sized computed properties.

## Environment and Lifecycle

Use environment injection for genuinely shared dependencies, not as a shortcut for every value. Required dependencies should remain required; install deterministic preview/test substitutes instead of making production types optional.

Prefer `.task` or `.task(id:)` for async work tied to view lifetime because SwiftUI cancels it with the view. A manually stored `Task` is appropriate when work must outlive a modifier scope or requires explicit cancellation. Route debounce, clocks, cancellation handlers, actors, and `AsyncSequence` to `swift-concurrency`.

## Previews

Create deterministic previews for meaningful loaded, loading, empty, and error states as applicable. Install every required environment value and use in-memory or temporary persistence. Do not call live APIs, production authentication, Keychain state, or global databases from previews.

Read [Isolated Preview Construction](references/preview-isolation.md) when a preview needs fixtures, persistence, or environment setup.

## Review Checklist

- [ ] State has one clear owner and mutation path
- [ ] Property wrappers reflect ownership rather than convenience
- [ ] Feature architecture matches existing conventions and actual complexity
- [ ] Significant sections are dedicated views with narrow dependencies
- [ ] Primary type names and filenames explain their role
- [ ] Business rules and reusable effects live outside view layout code
- [ ] Async work follows view lifetime or has explicit cancellation ownership
- [ ] Identity is stable for dynamic collections; index identity is used only when the collection is truly fixed and position is the identity
- [ ] Required preview dependencies are installed with deterministic fixtures
- [ ] Structure-only changes preserve layout, navigation, accessibility, timing, and side effects
- [ ] The affected target builds and important interactions are exercised

## References

- Architecture, app wiring, and lightweight clients: [references/architecture-patterns.md](references/architecture-patterns.md)
- Project folders, filenames, and view boundaries: [references/project-structure.md](references/project-structure.md)
- Existing-view restructuring: [references/view-refactoring.md](references/view-refactoring.md)
- Isolated previews and fixtures: [references/preview-isolation.md](references/preview-isolation.md)
- Design polish, theming, haptics, loading, and focus: [references/design-polish.md](references/design-polish.md)
- Deprecated or fragile API migration: [references/deprecated-migration.md](references/deprecated-migration.md)
- Platform and sharing patterns: [references/platform-and-sharing.md](references/platform-and-sharing.md)
