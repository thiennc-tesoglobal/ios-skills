---
name: swiftui-responsive-layout
description: "Diagnose and implement adaptive SwiftUI layouts across iPhone and iPad window sizes, orientation, Dynamic Type, localization, safe areas, keyboard, and multitasking. Use when views clip, overlap, truncate, move off-screen, or depend on brittle fixed frames; route ordinary container selection to swiftui-layout-components and measured runtime profiling to swiftui-performance."
---

# SwiftUI Responsive Layout

Make the interface respond to the space and content it actually receives, then verify the failing configurations instead of inferring behavior from a device name.

## Scope and Boundaries

This skill owns cross-size adaptation and layout-failure diagnosis: clipping, unintended overlap, truncation, off-screen controls, unstable resizing, keyboard obstruction, safe-area mistakes, and layouts that fail under Dynamic Type or localization.

Route ordinary `List`, `Form`, grid, scroll-view, control, search, and overlay selection to `swiftui-layout-components`. Route semantic accessibility behavior to `ios-accessibility`, localized content to `ios-localization`, navigation structure to `swiftui-navigation`, and measured layout cost or update storms to `swiftui-performance`.

Inspect the deployment target and SDK before using versioned APIs. Preserve the product hierarchy, state ownership, navigation behavior, and accessibility contract unless the requested fix requires a deliberate change.

## Diagnostic Workflow

1. Reproduce the smallest failing configuration: available width and height, orientation or window state, Dynamic Type size, locale, keyboard visibility, and enclosing navigation or presentation container.
2. Inspect the view hierarchy from the nearest stable container outward. Identify who proposes size, which child reports an inflexible ideal size, and whether an overlay or ignored safe area bypasses normal layout.
3. Classify the cause before editing: rigid sizing, compression competition, structural layering, safe-area or keyboard handling, content growth, geometry feedback, or incorrect adaptation signal.
4. Apply the narrowest fix using the pattern ladder below. Avoid device-specific coordinate branches and broad rewrites.
5. Verify the original failure plus neighboring configurations. Rotate or resize while stateful content is active to catch identity loss and transition-only failures.

Read [Layout Diagnosis and Verification](references/layout-diagnosis.md) when investigating an existing failure. Read [Adaptive Layout Patterns](references/adaptive-patterns.md) before implementing a responsive variant or replacing fixed geometry.

## Choose the Adaptation Signal

Prefer the most local signal that expresses the requirement:

| Requirement | Preferred signal |
|---|---|
| The content either fits or needs a compact variant | `ViewThatFits` |
| The same children need horizontal or vertical arrangement | `AnyLayout` with stack layouts |
| A broad region changes structure in compact versus regular space | horizontal or vertical size class |
| A component responds to its actual container dimensions | container-relative APIs, focused geometry observation, or a custom `Layout` |
| Text or controls grow at accessibility sizes | `dynamicTypeSize`, intrinsic content size, wrapping, and axis change |

Size class is an environment category, not a device detector or an exact width. iPad windows can change size while the app runs. Use actual fit or container space when the breakpoint belongs to a component rather than the whole scene.

## Pattern Ladder

Start with flexible intrinsic layout and escalate only when the simpler level cannot express the design:

1. Remove unjustified fixed width or height. Use intrinsic size, flexible frames, wrapping text, standard spacing, and adaptive grid items.
2. Use `ViewThatFits` for a small ordered set of meaningful variants.
3. Use `AnyLayout` when the same stateful children change arrangement and should retain identity.
4. Use size classes for broad structural changes such as a compact single-column versus regular supporting panel.
5. Use focused geometry observation or a custom `Layout` only when behavior depends on real container measurements.

Do not hide overflow with clipping, scaling, or a smaller font before fixing the layout contract. `layoutPriority` can resolve a known compression preference, but it is not a substitute for an adaptive structure.

## Text, Localization, and Controls

- Let essential text wrap and grow vertically. Treat `lineLimit`, `fixedSize`, `minimumScaleFactor`, and truncation as explicit product decisions.
- Change axis or presentation when a horizontal row cannot remain usable at larger Dynamic Type sizes.
- Use `@ScaledMetric` for non-text dimensions that should follow text scaling; use semantic text styles for text.
- Expect translated labels to expand and right-to-left layout to reverse reading order. Avoid width assumptions derived from English copy.
- Keep controls reachable and at usable sizes after reflow; do not overlay a compact control on top of content merely to preserve a screenshot composition.

## Safe Areas, Keyboard, and Layering

- Extend decorative backgrounds beyond safe areas separately from interactive content.
- Use `safeAreaInset` for persistent bars or actions that must reserve layout space. An `overlay` does not reserve space and can cover the final scroll content.
- Avoid broad `ignoresSafeArea` on the root interaction surface. Apply it to the intended background and edges only.
- Verify text entry with the software keyboard visible. Prefer scrollable form content and system keyboard-safe-area behavior over hard-coded keyboard heights.
- Treat `ZStack`, `overlay`, and absolute offsets as intentional layering tools, not general layout escape hatches.

## Geometry and Stability

Avoid `GeometryReader` as the default responsive container, especially inside repeated lazy cells. Prefer `ViewThatFits`, `containerRelativeFrame`, focused `onGeometryChange`, preferences, or `Layout` according to the requirement.

When geometry must enter state, transform it to the smallest `Equatable` value needed and keep that state in the narrowest subtree. A geometry-derived state change must not alter the same geometry used to derive it, or the view can oscillate and relayout continuously.

Preserve child identity across adaptation. Prefer a layout container change over duplicate conditional branches when both branches represent the same stateful controls.

## Common Mistakes

- Branching on `UIDevice` model, screen bounds, or portrait assumptions instead of current container space
- Combining fixed frames, offsets, and negative padding until one screenshot aligns
- Putting a bottom action in an overlay without reserving scroll content space
- Applying `ignoresSafeArea` to the entire interactive hierarchy
- Forcing one-line labels at accessibility text sizes
- Reading geometry at the root and publishing every change through shared app state
- Creating separate compact and regular trees that reset focus, scroll position, or control state during resize
- Testing one iPhone preview and calling the layout responsive

## Review Checklist

- [ ] The original failing size, content, and presentation state is documented and reproduced
- [ ] Fixed dimensions and offsets have a demonstrated content or platform reason
- [ ] The adaptation signal matches the local requirement rather than a device model
- [ ] Essential content neither clips nor becomes unreachable at supported Dynamic Type sizes
- [ ] Long localized and right-to-left content preserves hierarchy and actions
- [ ] Persistent bars reserve space and respect safe areas, navigation chrome, and the keyboard
- [ ] Rotation and live iPad window resizing preserve state and avoid transient overlap
- [ ] Geometry observation is narrow, stable, and free of feedback loops
- [ ] The relevant Simulator or preview matrix has evidence, not just a successful build
- [ ] Unrelated state, navigation, animation, and architecture were left with their owners

## References

- [Layout diagnosis and verification](references/layout-diagnosis.md)
- [Adaptive SwiftUI patterns](references/adaptive-patterns.md)
- [Apple: Layout fundamentals](https://sosumi.ai/documentation/swiftui/layout-fundamentals)
- [Apple: Human Interface Guidelines — Layout](https://sosumi.ai/design/human-interface-guidelines/layout)
- [Apple: ViewThatFits](https://sosumi.ai/documentation/swiftui/viewthatfits)
- [Apple: AnyLayout](https://sosumi.ai/documentation/swiftui/anylayout)
- [Apple: UserInterfaceSizeClass](https://sosumi.ai/documentation/swiftui/userinterfacesizeclass)
