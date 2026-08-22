---
name: swiftui-layout-components
description: "Build SwiftUI stacks, grids, lists, scroll views, forms, controls, search interfaces, and overlays. Use for layout and container decisions; route state architecture, navigation policy, animation choreography, and runtime profiling to dedicated skills."
---

# SwiftUI Layout and Components

Choose containers and controls that preserve identity, adapt across sizes, and remain accessible without unnecessary custom layout code.

## Scope and Compatibility

This skill owns stacks, grids, lists, scroll views, forms, controls, search UI, and overlays. Route state ownership to `swiftui-patterns`, navigation and modal policy to `swiftui-navigation`, gestures to `swiftui-gestures`, motion to `swiftui-animation`, and measured performance problems to `swiftui-performance`.

Inspect deployment target, Swift mode, and SDK before using versioned modifiers. Preserve project settings unless the user requests a change; gate newer APIs and verify them in SDK headers or primary Apple documentation.

## Container Selection

| Need | Start with |
|---|---|
| Small fixed arrangement | `VStack`, `HStack`, or `ZStack` |
| Large one-axis collection | `ScrollView` with `LazyVStack` or `LazyHStack` |
| Adaptive two-dimensional collection | `LazyVGrid` or `LazyHGrid` |
| Platform list behavior, sections, editing, swipe actions | `List` |
| Structured settings or data entry | `Form` |
| Custom geometry-based layout | `Layout` protocol or focused geometry APIs after standard containers are insufficient |

Do not choose a container from row count alone. Consider editing behavior, selection, section semantics, separators, custom backgrounds, nested interaction, and whether cells need platform list behavior.

Read the relevant reference before implementing a substantial container:

- grids: [references/grids.md](references/grids.md)
- lists and sections: [references/list.md](references/list.md)
- scroll views and lazy stacks: [references/scrollview.md](references/scrollview.md)
- forms and validation: [references/form.md](references/form.md)

## Identity and Laziness

Dynamic items need identity that survives insertion, deletion, sorting, and filtering. Prefer model identity. Index identity is acceptable only when position is intentionally the identity of a fixed collection.

Use lazy containers for collections large enough that eager construction is material. Do not wrap every small stack in a lazy container. Keep expensive filtering, sorting, formatting, and image work outside per-frame layout closures.

Avoid `GeometryReader` inside repeated lazy cells when a focused API such as `containerRelativeFrame`, `onGeometryChange`, preferences, or a custom `Layout` expresses the requirement more narrowly.

## Lists, Forms, and Controls

Use `List` when system editing, selection, swipe actions, sections, or platform row behavior are desired. Use `ScrollView` plus a lazy stack when the visual treatment or interaction model substantially diverges from `List`.

Use `Form` for structured input and settings, but keep validation and persistence policy outside layout code. Choose control styles based on option count and context; segmented controls are poor fits for many or long options.

Interactive rows need an adequate hit target and a meaningful `contentShape`. Preserve Dynamic Type and allow layouts to reflow instead of truncating essential content.

## Search and Overlays

Use `.searchable` for platform search presentation. Keep query state with the feature owner and use `.task(id:)` only when search work is tied to view lifetime; route debounce, clocks, and cancellation mechanics to `swift-concurrency`.

Use overlays for transient UI that should not affect layout. Give banners and toasts a clear alignment, transition, accessibility announcement, and dismissal owner. Route sheets, full-screen covers, detents, and route-driven presentation to `swiftui-navigation`.

## Scroll-Driven Effects

Drive continuous effects from one normalized progress value and keep geometry observation in the narrowest subtree possible. Avoid parallel booleans that can disagree. Do not combine competing same-axis scroll and drag gestures without an explicit interaction policy.

Route Liquid Glass scroll-edge styling to `swiftui-liquid-glass` and detailed animation curves/transitions to `swiftui-animation`.

## Review Checklist

- [ ] Container choice matches behavior, not just appearance
- [ ] Dynamic collections use stable semantic identity
- [ ] Laziness is used where collection size justifies it
- [ ] No expensive work runs in repeated layout or geometry callbacks
- [ ] Forms and controls remain usable at accessibility text sizes
- [ ] Search work has clear cancellation and empty-query behavior
- [ ] Overlays have one presentation/dismissal owner and do not unintentionally block interaction
- [ ] Scroll-driven state has one source of truth
- [ ] Layout adapts to size class, orientation, and localization where required
- [ ] Versioned APIs match the project deployment target

## References

- [Grid patterns](references/grids.md)
- [List and section patterns](references/list.md)
- [ScrollView and lazy stack patterns](references/scrollview.md)
- [Form patterns](references/form.md)
