---
name: swiftui-animation
description: "Implement or diagnose SwiftUI motion, including state animations, transitions, springs, keyframes, matched geometry, navigation zoom, and symbol effects. Use when motion behavior is part of the request; route layout, navigation state, and performance profiling elsewhere."
---

# SwiftUI Animation

Choose the narrowest animation mechanism that communicates state change without obscuring ownership, accessibility, or performance.

## Scope and Compatibility

This skill owns SwiftUI timing, transitions, phase/keyframe choreography, matched geometry, navigation zoom visuals, symbol effects, and animation accessibility. Route layout to `swiftui-layout-components`, route/path ownership to `swiftui-navigation`, state ownership to `swiftui-patterns`, and evidence-based profiling to `swiftui-performance`.

Inspect deployment target, Swift mode, and SDK before selecting APIs. Preserve project settings unless the user requests a change; gate newer APIs and verify availability in SDK headers or primary Apple documentation.

## Triage

1. Identify the state change and which owner mutates it.
2. Decide whether the view is changing modifiers, entering/leaving the tree, changing content in place, or moving between related layouts.
3. Select one mechanism and scope it to the smallest affected subtree.
4. Test normal interaction, interruption, repeated triggers, and Reduce Motion.
5. If motion hitches, measure before changing architecture or adding `Equatable`/drawing workarounds.

## Mechanism Selection

| Need | Prefer |
|---|---|
| Animate a mutation owned by an action | `withAnimation` |
| Animate selected modifiers | scoped `.animation(_:body:)` |
| Simple value-bound implicit animation | `.animation(_:value:)` |
| Insert or remove a view | `.transition` paired with an animation |
| Change text, number, or symbol in place | `.contentTransition` |
| Discrete multi-step sequence | `PhaseAnimator` |
| Multi-property timeline | `KeyframeAnimator` |
| Related layouts in one hierarchy | `matchedGeometryEffect` |
| Push/pop hero effect | matched transition source plus navigation zoom when available |
| Semantic SF Symbol motion | `.symbolEffect` |
| Custom interpolated shape/value | `Animatable` or a custom animation when synthesis is insufficient |
| Layer-level or display-link work | Read [Core Animation Bridge](references/core-animation-bridge.md) |

Use [Advanced Animation Patterns](references/animation-advanced.md) for spring parameter variants, custom transitions, transactions, keyframes, symbol catalogs, and advanced performance guidance.

## Core Rules

- Animate state changes or visual properties, not expensive computation.
- Value-bound implicit animation must name the value that drives it.
- A transition only runs when insertion/removal occurs and an animation participates in that transaction.
- `contentTransition` changes rendering of in-place content; it still needs an animation.
- Matched geometry needs stable IDs and one intended source for each ID.
- Apply navigation transitions to the destination boundary required by the API, while navigation ownership remains outside this skill.
- Capture values before per-frame `@Sendable` closures when actor isolation would otherwise be crossed.
- Treat frame-rate ranges as hints and adapt work to the actual refresh rate.

## Accessibility

Read `accessibilityReduceMotion` for motion that translates, scales, zooms, loops, or creates spatial disorientation. Replace large movement with a fade, content change, or no animation while preserving the state transition. Do not disable every subtle opacity or color change automatically; match the alternative to the user impact.

Indefinite symbol and timeline effects need a clear active condition and must stop when no longer visible or relevant.

## Review Checklist

- [ ] The state owner and animation trigger are explicit
- [ ] Animation scope is limited to intended modifiers or subtree
- [ ] Transition and content-transition semantics are correct
- [ ] Stable identity and namespace pairing are preserved
- [ ] Repeated and interrupted interactions produce valid state
- [ ] Reduce Motion has an appropriate alternative
- [ ] Per-frame closures avoid expensive work and unsafe actor reads
- [ ] Versioned APIs match the project target
- [ ] Core Animation bridges clean up delegates, display links, and resources

## References

- Advanced SwiftUI animations and transitions: [references/animation-advanced.md](references/animation-advanced.md)
- Core Animation and display-link bridging: [references/core-animation-bridge.md](references/core-animation-bridge.md)
