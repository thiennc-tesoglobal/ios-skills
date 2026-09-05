# Symbol Effects and Accessible Motion

Use this reference when implementing SF Symbol animated effects, respecting Reduce Motion system preferences, and tuning animation performance in SwiftUI.

## Contents

- [All Symbol Effect Types](#all-symbol-effect-types)
- [Reduce Motion Implementation Patterns](#reduce-motion-implementation-patterns)
- [Animation Performance Tips](#animation-performance-tips)

---

## All Symbol Effect Types

Availability: `.bounce`, `.pulse`, `.variableColor`, `.scale`, `.appear`,
`.disappear`, and `.replace` are iOS 17+. `.wiggle`, `.breathe`, and `.rotate`
are iOS 18+.

### Discrete Effects (trigger with `value:`)

| Effect | Availability | Scope | Direction |
|---|---|---|---|
| `.bounce` | iOS 17+ | `.byLayer`, `.wholeSymbol` | -- |
| `.wiggle` | iOS 18+ | `.byLayer`, `.wholeSymbol` | `.up`, `.down`, `.left`, `.right`, `.forward`, `.backward`, `.clockwise`, `.counterClockwise`, `.custom(angle:)` |

```swift
Image(systemName: "bell.fill")
    .symbolEffect(.bounce.byLayer, value: count)

// iOS 18+
Image(systemName: "arrow.left.arrow.right")
    .symbolEffect(.wiggle.left, value: swapCount)
```

### Indefinite Effects (toggle with `isActive:`)

| Effect | Availability | Scope | Direction |
|---|---|---|---|
| `.pulse` | iOS 17+ | `.byLayer`, `.wholeSymbol` | -- |
| `.variableColor` | iOS 17+ | `.byLayer`, `.wholeSymbol` | Chaining: `.cumulative`/`.iterative`, `.reversing`/`.nonReversing`, `.dimInactiveLayers`/`.hideInactiveLayers` |
| `.scale` | iOS 17+ | `.byLayer`, `.wholeSymbol` | `.up`, `.down` |
| `.breathe` | iOS 18+ | `.byLayer`, `.wholeSymbol` | -- |
| `.rotate` | iOS 18+ | `.byLayer`, `.wholeSymbol` | `.clockwise`, `.counterClockwise` |

```swift
Image(systemName: "wifi")
    .symbolEffect(.pulse.byLayer, isActive: isConnecting)

// iOS 18+
Image(systemName: "gear")
    .symbolEffect(.rotate.clockwise, isActive: isProcessing)

Image(systemName: "speaker.wave.3.fill")
    .symbolEffect(
        .variableColor.cumulative.nonReversing.dimInactiveLayers,
        options: .repeating,
        isActive: isPlaying
    )

Image(systemName: "magnifyingglass")
    .symbolEffect(.scale.up, isActive: isHighlighted)

// iOS 18+
Image(systemName: "heart.fill")
    .symbolEffect(.breathe, isActive: isFavorite)
```

### Transition Effects (appear/disappear)

```swift
Image(systemName: "checkmark.circle.fill")
    .symbolEffect(.appear, isActive: showCheck)

Image(systemName: "xmark.circle")
    .symbolEffect(.disappear, isActive: shouldHide)
```

### Content Transition Effects (replace)

```swift
Image(systemName: isMuted ? "speaker.slash" : "speaker.wave.3")
    .contentTransition(.symbolEffect(.replace.downUp))

// Magic replace (iOS 18+, morphs between symbols)
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
    .contentTransition(.symbolEffect(.replace.magic(fallback: .downUp)))
```

Replace directions: `.downUp`, `.offUp`, `.upUp`.

### SymbolEffectOptions

```swift
.symbolEffect(.pulse, options: .default, isActive: true)
.symbolEffect(.bounce, options: .repeating, value: count)
.symbolEffect(.pulse, options: .nonRepeating, isActive: true)
.symbolEffect(.bounce, options: .repeat(3), value: count)
.symbolEffect(.pulse, options: .speed(2.0), isActive: true)

// RepeatBehavior
.symbolEffect(.bounce, options: .repeat(.periodic(3, delay: 0.5)), value: count)
.symbolEffect(.pulse, options: .repeat(.continuous), isActive: true)
```

### Removing Effects

```swift
Image(systemName: "star.fill")
    .symbolEffect(.pulse, isActive: true)
    .symbolEffectsRemoved(reduceMotion)
```

## Reduce Motion Implementation Patterns

### Environment Variable

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion
```

### Pattern 1: Conditional Animation

```swift
withAnimation(reduceMotion ? .none : .bouncy) {
    isExpanded.toggle()
}
```

### Pattern 2: Simplified Animation

Replace bouncy/spring with crossfade when reduce motion is on.

```swift
withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(duration: 0.4, bounce: 0.3)) {
    selectedTab = newTab
}
```

### Pattern 3: Disable Repeating Animations

```swift
// WRONG: Ignores reduce motion
PhaseAnimator(phases) { phase in /* ... */ }

// CORRECT: Use trigger-based or skip entirely
if !reduceMotion {
    PhaseAnimator(phases) { phase in /* ... */ }
} else {
    StaticView()
}
```

### Pattern 4: Symbol Effects

```swift
Image(systemName: "wifi")
    .symbolEffect(.pulse, isActive: isSearching)
    .symbolEffectsRemoved(reduceMotion)
```

### Pattern 5: Reusable Helper

```swift
extension Animation {
    static func adaptive(
        _ animation: Animation,
        reduceMotion: Bool
    ) -> Animation? {
        reduceMotion ? nil : animation
    }
}

// Usage
withAnimation(.adaptive(.bouncy, reduceMotion: reduceMotion)) {
    isVisible = true
}
```

## Animation Performance Tips

### Keep Content Closures Light

The `content` closure in `KeyframeAnimator` and `PhaseAnimator` runs every
frame while animating. Keep it to simple view modifiers.

```swift
// WRONG: Expensive computation per frame
.keyframeAnimator(initialValue: v, trigger: t) { content, value in
    let result = heavyComputation(value.progress)
    return content.opacity(result)
} keyframes: { _ in /* ... */ }

// CORRECT: Only apply view modifiers
.keyframeAnimator(initialValue: v, trigger: t) { content, value in
    content.opacity(value.opacity)
} keyframes: { _ in /* ... */ }
```

### Prefer Modifier-Based Animations

Animating view modifiers (`opacity`, `scaleEffect`, `offset`, `rotationEffect`)
is highly optimized. Avoid animating layout-triggering properties when possible.

### Use drawingGroup for Complex Compositing

```swift
ComplexAnimatedView()
    .drawingGroup()
```

Flattens the view hierarchy into a single Metal-backed layer. Use when
compositing many overlapping animated views.

### Limit Concurrent Animations

Avoid animating dozens of views simultaneously. Use staggered delays.

```swift
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
    ItemView(item: item)
        .transition(.move(edge: .bottom).combined(with: .opacity))
        .animation(.spring.delay(Double(index) * 0.05), value: isVisible)
}
```

### Avoid Re-creating Views During Animation

Ensure animated views maintain stable identity. Use explicit `id()` modifiers
or stable `ForEach` identifiers.

```swift
// WRONG: View identity changes, breaks animation
ForEach(Array(items.enumerated()), id: \.offset) { index, item in
    ItemView(item: item)
}

// CORRECT: Stable identity from model
ForEach(items) { item in
    ItemView(item: item)
}
```

### Use geometryGroup() for Nested Geometry

Isolate child geometry from parent animations when they conflict.

```swift
ParentView()
    .scaleEffect(parentScale)
    .geometryGroup()  // children see stable geometry
```

### Layout-Driven Height Changes

`transition` describes child insertion/removal, but a `List` row's changing
height may still snap instead of interpolate. Keep this skill focused on the
animation trigger, curve, and Reduce Motion behavior; route custom row-height,
grid, or layout interpolation work to `swiftui-layout-components`.

### Transaction for Selective Animation Override

Override animation for specific subtrees without affecting siblings.

```swift
// Disable animation on one child while parent animates
ChildView()
    .transaction { $0.animation = nil }
```

### Profile with Instruments

Use the Core Animation instrument in Xcode Instruments to verify:
- The chosen sustainable target frame rate has no avoidable dropped frames; refresh rates are system-managed hints, not guarantees.
- No offscreen rendering passes.
- GPU utilization stays reasonable during animations.
