# Adaptive SwiftUI Patterns

Use this reference after identifying the cause of a responsive-layout failure. Choose the first pattern that expresses the product requirement without unnecessary geometry state.

## Contents

- Content-driven alternatives
- Identity-preserving axis changes
- Adaptive collections
- Safe-area-aware persistent actions
- Focused measurement
- Custom layout threshold

## Content-Driven Alternatives

Use `ViewThatFits` when the design has a small preference-ordered set of valid representations. Each alternative must remain semantically complete; do not make the fallback silently remove an essential action.

```swift
ViewThatFits(in: .horizontal) {
    HStack {
        Label("Add to Favorites", systemImage: "heart")
        Spacer()
        Button("Add") { addFavorite() }
    }

    VStack(alignment: .leading) {
        Label("Add to Favorites", systemImage: "heart")
        Button("Add") { addFavorite() }
            .frame(maxWidth: .infinity)
    }
}
```

Order alternatives from preferred to fallback. Remember that fit is based on proposed size and ideal size along the constrained axes, so verify with real content and Dynamic Type.

## Identity-Preserving Axis Changes

Use `AnyLayout` when the children stay conceptually identical but their arrangement changes. This avoids duplicating stateful subtrees in `if` branches.

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

private var actionLayout: AnyLayout {
    dynamicTypeSize.isAccessibilitySize
        ? AnyLayout(VStackLayout(alignment: .leading, spacing: 12))
        : AnyLayout(HStackLayout(alignment: .center, spacing: 12))
}

var body: some View {
    actionLayout {
        Text(status)
            .frame(maxWidth: .infinity, alignment: .leading)
        Button("Continue") { continueFlow() }
    }
}
```

Choose the breakpoint from the actual content requirement. Dynamic Type is appropriate when text growth is the cause; a component-width decision may need a fit-based or measured signal instead.

## Adaptive Collections

Prefer an adaptive grid to device-specific column counts when cards have a meaningful minimum readable width.

```swift
private let columns = [
    GridItem(.adaptive(minimum: 160, maximum: 280), spacing: 16)
]

LazyVGrid(columns: columns, spacing: 16) {
    ForEach(items) { item in
        Card(item: item)
    }
}
```

The minimum should come from card content and interaction needs, not a convenient divisor of one screen width. Test the narrowest iPad multitasking width and the longest supported content.

## Safe-Area-Aware Persistent Actions

Use `safeAreaInset` when a bottom action must coexist with scrollable content. It reserves space in the observed safe region, unlike a visual overlay.

```swift
ScrollView {
    CheckoutContent()
        .padding()
}
.safeAreaInset(edge: .bottom, spacing: 0) {
    CheckoutBar()
        .padding()
        .background(.bar)
}
.background {
    AppBackground()
        .ignoresSafeArea()
}
```

Keep the background extension separate from interactive content. Test this structure inside the app's actual tab, navigation, sheet, or split-view container and with the keyboard visible.

## Focused Measurement

Use geometry only when the component genuinely needs its container's measured value. Observe the smallest stable value and avoid feeding raw frames into broad shared state.

```swift
@State private var usesCompactLayout = false

Content()
    .onGeometryChange(for: Bool.self) { proxy in
        proxy.size.width < minimumExpandedWidth
    } action: { isCompact in
        usesCompactLayout = isCompact
    }
```

Derive the threshold from content requirements rather than a device model. Check SDK availability before adopting a versioned geometry API, and do not let the chosen layout change the measurement boundary in a way that continuously crosses the same breakpoint.

## Custom Layout Threshold

Create a `Layout` implementation only when standard containers, `ViewThatFits`, and `AnyLayout` cannot express reusable measurement and placement behavior. Define the contract first:

- which axes are constrained
- how each subview is measured
- minimum and ideal spacing
- overflow and fallback behavior
- whether layout values affect placement
- how cache invalidation works

Keep business state out of `sizeThatFits` and `placeSubviews`. Both methods may run repeatedly; they must produce stable results for the same proposal, subviews, and cache.
