---
name: swiftui-gestures
description: "Builds or reviews SwiftUI tap, press, drag, magnify, and rotate interactions, including gesture composition, transient GestureState, custom gestures, and parent/child conflict resolution. Use for gesture recognition, arbitration, state, migration, or interaction bugs."
---

# SwiftUI Gestures (iOS 26+)

Review, write, and fix SwiftUI gesture interactions. Apply modern gesture APIs with correct composition, state management, and conflict resolution using Swift 6.3 patterns.

**Scope boundary:** This skill owns SwiftUI gesture recognition, composition, gesture state, and gesture-specific accessibility alternatives. Broader SwiftUI architecture/state ownership belongs in `swiftui-patterns`; list, scroll, form, and control layout belongs in `swiftui-layout-components`; broad UIKit bridging belongs in `swiftui-uikit-interop`.

When correcting Apple API availability, deprecation, or behavior claims, cite the relevant Sosumi or official Apple documentation URL in the response.

## Contents

- [Gesture Overview](#gesture-overview)
- [Core Gestures](#core-gestures)
- [Gesture Composition](#gesture-composition)
- [Transient vs Persisted State](#transient-vs-persisted-state)
- [Hierarchy and Precedence](#hierarchy-and-precedence)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Gesture Overview

| Gesture | Type | Value | Since |
|---|---|---|---|
| `TapGesture` | Discrete | `Void` | iOS 13 |
| `SpatialTapGesture` | Discrete | `SpatialTapGesture.Value` | iOS 16 |
| `LongPressGesture` | Discrete | `Bool` | iOS 13 |
| `DragGesture` | Continuous | `DragGesture.Value` | iOS 13 |
| `MagnifyGesture` | Continuous | `MagnifyGesture.Value` | iOS 17 |
| `RotateGesture` | Continuous | `RotateGesture.Value` | iOS 17 |

**Discrete** gestures fire once (`.onEnded`). **Continuous** gestures stream updates (`.onChanged`, `.onEnded`, `.updating`).

## Core Gestures

```swift
// Tap: Use Button for standard actions; reserve TapGesture for multi-tap or location tracking
Text("Double tap").onTapGesture(count: 2) { handleDoubleTap() }

// Long press with transient pressing feedback
@GestureState private var isPressing = false
Circle()
    .fill(isPressing ? .red : .blue)
    .gesture(
        LongPressGesture(minimumDuration: 0.8)
            .updating($isPressing) { current, state, _ in state = current }
            .onEnded { _ in triggerAction() }
    )

// Drag with translation tracking
@State private var offset: CGSize = .zero
RoundedRectangle(cornerRadius: 16)
    .offset(offset)
    .gesture(
        DragGesture(minimumDistance: 10, coordinateSpace: .local)
            .onChanged { value in offset = value.translation }
            .onEnded { _ in withAnimation(.spring) { offset = .zero } }
    )

// Magnify and Rotate (iOS 17+; replaces deprecated MagnificationGesture / RotationGesture)
MagnifyGesture().onChanged { value in currentScale = value.magnification }
RotateGesture().onChanged { value in currentAngle = value.rotation }
```

## Gesture Composition

Combine gestures using the three composition operators:

- **`.simultaneously(with:)`**: Both gestures evaluate together (e.g. pinch-to-zoom + rotate).
- **`.sequenced(before:)`**: First gesture must succeed before second starts (e.g. long press before drag).
- **`.exclusively(before:)`**: Only one succeeds; first has precedence (e.g. double tap before long press).

```swift
let combined = MagnifyGesture()
    .simultaneously(with: RotateGesture())
    .onChanged { value in
        if let mag = value.first { currentScale = mag.magnification }
        if let rot = value.second { currentAngle = rot.rotation }
    }
```

## Transient vs Persisted State

- **`@GestureState`**: Automatically resets to initial value when gesture ends or cancels. Always use with `.updating(&$state)`.
- **`@State`**: Persists values between interactions. Update in `.onChanged` (keep lightweight) and `.onEnded`.

```swift
@GestureState private var dragOffset = CGSize.zero // resets on release
@State private var accumulatedOffset = CGSize.zero // persists across gestures
```

## Hierarchy and Precedence

Control gesture arbitration across view hierarchy layers:

- **`.gesture(_:)`**: Lower precedence than child gestures.
- **`.highPriorityGesture(_:)`**: Parent gesture takes precedence over child gestures.
- **`.simultaneousGesture(_:)`**: Runs alongside child gestures without blocking them.
- **`GestureMask`**: Pass to `.gesture(g, including: mask)` (`.all`, `.gesture`, `.subviews`, `.none`).

## Common Mistakes

- **Using `onTapGesture` instead of `Button`**: `onTapGesture` lacks VoiceOver accessibility traits, focus, and keyboard activation. Use `Button` with `.buttonStyle(.plain)` for custom visuals.
- **Using deprecated gesture names**: Use `MagnifyGesture` and `RotateGesture` on iOS 17+, not `MagnificationGesture` or `RotationGesture`.
- **Heavy computation in `onChanged`**: Keep `onChanged` closures frame-rate lightweight (60-120Hz). Defer heavy work or hit testing to `.onEnded`.
- **Missing visual feedback for `LongPressGesture`**: Always pair long-press with `@GestureState` and `.updating()` to provide visual indication of press progress.
- **Assuming parent gestures override child gestures by default**: Use `.highPriorityGesture()` explicitly when parent gestures should win.

## Review Checklist

- [ ] Correct modern gesture types used (`MagnifyGesture` / `RotateGesture` on iOS 17+)
- [ ] Accessible `Button` preferred over `onTapGesture` for single-tap actionable controls
- [ ] `@GestureState` used for transient offset/scale that resets automatically
- [ ] Continuous `onChanged` updates are lightweight without allocations or heavy queries
- [ ] Parent/child gesture conflicts resolved using `.highPriorityGesture` or `.simultaneousGesture`
- [ ] Composed gestures correctly handle enum results (`.first`, `.second`)
- [ ] Bounds clamped on persisted pinch/rotation values in `.onEnded`

## References

- Full recipes, pinch-zoom-pan, drag-to-reorder, and UIKit interop: [references/gesture-patterns.md](references/gesture-patterns.md)
- [Gesture protocol](https://sosumi.ai/documentation/swiftui/gesture)
- [TapGesture](https://sosumi.ai/documentation/swiftui/tapgesture)
- [LongPressGesture](https://sosumi.ai/documentation/swiftui/longpressgesture)
- [DragGesture](https://sosumi.ai/documentation/swiftui/draggesture)
- [DragGesture.Value.velocity](https://sosumi.ai/documentation/swiftui/draggesture/value/velocity)
- [MagnifyGesture](https://sosumi.ai/documentation/swiftui/magnifygesture)
- [RotateGesture](https://sosumi.ai/documentation/swiftui/rotategesture)
- [GestureState](https://sosumi.ai/documentation/swiftui/gesturestate)
- [Composing SwiftUI gestures](https://sosumi.ai/documentation/swiftui/composing-swiftui-gestures)
- [Adding interactivity with gestures](https://sosumi.ai/documentation/swiftui/adding-interactivity-with-gestures)
