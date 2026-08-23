---
name: ios-app-workflow
description: "Plan, build, refactor, and verify a complete iOS app or substantial end-to-end feature. Use when work spans project structure, SwiftUI implementation, persistence, testing, and Simulator delivery; do not use for a narrow framework question or isolated compiler error."
---

# iOS App Workflow

Coordinate an end-to-end iOS delivery without loading unrelated framework guidance or silently changing the product contract.

## Trigger Boundary

Use this skill for a new app, a substantial multi-file feature, a broad refactor, or a request to finish and verify an iOS experience. For a focused issue, use only the relevant specialist skill—for example `swift-concurrency` for one isolation diagnostic or `swiftdata` for one migration problem.

Do not load all installed iOS skills. Select the smallest set that covers the requested behavior and actual project stack.

If a routed specialist skill is unavailable, continue from project evidence and primary documentation rather than blocking the delivery.

## Project Preflight

Before implementation, inspect what is locally discoverable:

- workspace/project, schemes, targets, supported platforms, and bundle identifier
- deployment target, Xcode/SDK, Swift language and concurrency settings
- existing architecture, folder conventions, naming, dependencies, and persistence
- test targets, previews, accessibility conventions, assets, and local agent instructions
- Git status and user-owned changes that must be preserved

Keep the existing platform and deployment settings unless the user requested a change. When adopting a newer API, provide an availability path appropriate to the current target. Verify version claims against SDK headers, Swift Evolution/release notes, or primary Apple documentation.

## Select Specialist Skills

Load only skills needed for the current slice:

| Concern | Route to |
|---|---|
| State ownership, view composition, previews, file boundaries | `swiftui-patterns` |
| Layout, lists, forms, search, overlays | `swiftui-layout-components` |
| Cross-size adaptation, clipping, overlap, safe areas, keyboard layout | `swiftui-responsive-layout` |
| Navigation, sheets, tabs, deep links | `swiftui-navigation` |
| Motion and transitions | `swiftui-animation` |
| Liquid Glass and iOS 26 visual APIs | `swiftui-liquid-glass` |
| Architecture choice or migration | `swift-architecture` |
| Isolation and async mechanics | `swift-concurrency` |
| Persistence | `swiftdata` or `core-data`, according to the existing stack |
| Accessibility | `ios-accessibility` |
| Unit tests | `swift-testing` |
| Build, launch, screenshots, and runtime verification | `ios-simulator` |

Add framework-specific skills only when the feature actually uses those frameworks.

## Delivery Contract

Write down or infer conservatively:

- required user flows and data behavior
- visual direction and supported appearances/sizes
- persistence and migration expectations
- accessibility and motion requirements
- offline/network/error behavior where relevant
- minimum verification needed to call the work complete

If the request is a refactor, preserve layout, navigation, state ownership semantics, identity, accessibility, animation/side-effect timing, persistence, and public API unless a change is explicitly requested.

## Structure and Naming

Follow coherent existing conventions. For a growing SwiftUI app, prefer feature-first folders with small shared layers such as `App`, `DesignSystem`, `Models`, `Services`, and `Features/<Feature>`.

The app entry point should use the product name; screens and components should use domain-plus-role names. Match each file to its primary type. Avoid generic names like `ContentView`, `MainView`, `Helper`, or `Manager` when a concrete role is known.

Extract a dedicated view for meaningful branching/layout, local lifecycle or gesture state, narrow dependencies, or independent preview value. Do not split every tiny fragment, and do not treat extensions or `// MARK:` headings as actual boundaries.

## Implementation

Work in vertical slices that leave the target buildable after meaningful boundaries:

1. establish app/feature wiring and model boundaries
2. implement the primary happy path
3. add persistence, errors, empty/loading states, and secondary actions in scope
4. add accessibility and motion adaptations with the UI, not as an afterthought
5. add tests and deterministic previews for behavior that can regress

Keep business rules and reusable effects out of layout code. Preserve user changes in a dirty worktree and avoid unrelated cleanup.

## Verification

Use the smallest evidence set that proves the requested outcome:

- build the affected target with the actual scheme/destination
- run relevant unit tests
- render deterministic previews where useful
- install and launch on an explicit Simulator UDID
- exercise primary actions, failure/empty states, and persistence across relaunch when applicable
- verify important accessibility labels/actions, Dynamic Type, and Reduce Motion behavior
- capture screenshots or focused logs when visual/runtime proof matters

Simulator verification is not proof for device-only hardware or production APNs behavior. Read [Delivery Checklist](references/delivery-checklist.md) for mode-specific proof.

## Completion

Report the result first, then changed structure, verification performed, and any real limitation. Do not commit, push, publish, change signing, or mutate external systems unless the user authorized that action.

## Review Checklist

- [ ] Only relevant specialist skills were loaded
- [ ] Existing deployment target, architecture, and user changes were preserved
- [ ] Names and file boundaries reflect product/domain roles
- [ ] Primary flow plus in-scope empty/error/persistence behavior is implemented
- [ ] Accessibility and Reduce Motion are handled proportionally
- [ ] A real target builds and relevant tests pass
- [ ] Simulator/device claims match the evidence collected
- [ ] No external mutation exceeded user authorization

## Reference

- [Mode-specific delivery and verification checklist](references/delivery-checklist.md)
