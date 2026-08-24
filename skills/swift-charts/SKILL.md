---
name: swift-charts
description: "Builds or reviews Swift Charts visualizations, including bar, line, area, point, sector, vectorized, and 3D charts. Use for marks, axes, scales, legends, annotations, selection, scrolling, styling, accessibility, large datasets, plots, or spatial surfaces."
---

# Swift Charts

Build data visualizations with Swift Charts targeting iOS 26+. Compose marks
inside `Chart` or `Chart3D`, configure axes and scales with view modifiers, and
use vectorized plots or 3D plots when the data calls for them.

Use the task-specific chart references routed below instead of loading every recipe.

## Workflow

1. Identify the analytical question, data shape, deployment target, and accessibility requirement before choosing marks.
2. Select the smallest mark set and encode series, categories, scales, and domains explicitly where ambiguity matters.
3. Add axes, legends, annotations, selection, or scrolling only when they improve interpretation.
4. Prefer vectorized plots or aggregation for large datasets and avoid expensive per-mark decoration.
5. Verify empty/single/extreme data, localization, Dynamic Type, VoiceOver summaries, selection, and performance.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for chart containers, marks, axes, scales, styles, selection, scrolling, annotations, vectorized plots, and 3D charts.
- Read [chart types and composition](references/chart-types-and-composition.md) for bars, lines, sectors, combined charts, and data modeling.
- Read [interaction, 3D, accessibility, and performance](references/interaction-3d-accessibility-and-performance.md) for selection, scrolling, function plots, surfaces, and large datasets.
- Read [styling, heat maps, and modifier reference](references/styling-heatmaps-and-reference.md) for themes, symbols, stacking, coordinate conversion, and quick-reference modifiers.

## Core Decisions

- Choose marks from the question being answered, not visual novelty.
- Preserve truthful scale domains and label units/aggregation clearly.
- Encode multiple line series with an explicit series dimension.
- Keep charts readable at large text sizes and expose nonvisual summaries.

## Common Mistakes

### 1. Missing series parameter for multi-line charts

```swift
// WRONG -- all points connect into one line
Chart {
    ForEach(allCities) { item in
        LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
    }
}

// CORRECT -- separate lines per city
Chart {
    ForEach(allCities) { item in
        LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
            .foregroundStyle(by: .value("City", item.city))
    }
}
```

### 2. Too many SectorMark slices

```swift
// WRONG -- 20 tiny sectors are unreadable
Chart(twentyCategories, id: \.name) { item in
    SectorMark(angle: .value("Value", item.value))
}

// CORRECT -- group into top 5 + "Other"
Chart(groupedData, id: \.name) { item in
    SectorMark(angle: .value("Value", item.value))
        .foregroundStyle(by: .value("Category", item.name))
}
```

### 3. Missing scale domain when zero-baseline matters

```swift
// WRONG -- axis starts at ~95; small changes look dramatic
Chart(data) {
    LineMark(x: .value("Day", $0.day), y: .value("Score", $0.score))
}

// CORRECT -- explicit domain for honest representation
Chart(data) {
    LineMark(x: .value("Day", $0.day), y: .value("Score", $0.score))
}
.chartYScale(domain: 0...100)
```

### 4. Static foregroundStyle overriding data encoding

```swift
// WRONG -- static color overrides by-value encoding
BarMark(x: .value("X", item.x), y: .value("Y", item.y))
    .foregroundStyle(by: .value("Category", item.category))
    .foregroundStyle(.blue)

// CORRECT -- use only the data encoding
BarMark(x: .value("X", item.x), y: .value("Y", item.y))
    .foregroundStyle(by: .value("Category", item.category))
```

### 5. Individual marks for 10,000+ data points

```swift
// WRONG -- creates 10,000 mark views; slow
Chart(largeDataset) { item in
    PointMark(x: .value("X", item.x), y: .value("Y", item.y))
}

// CORRECT -- vectorized plot (iOS 18+)
Chart {
    PointPlot(largeDataset, x: .value("X", \.x), y: .value("Y", \.y))
}
```

### 6. Fixed chart height breaking Dynamic Type

```swift
// WRONG -- clips axis labels at large text sizes
Chart(data) { ... }
    .frame(height: 200)

// CORRECT -- adaptive sizing
Chart(data) { ... }
    .frame(minHeight: 200, maxHeight: 400)
```

### 7. KeyPath modifier after value modifier on vectorized plots

```swift
// WRONG -- compiler error
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .opacity(0.8)
    .foregroundStyle(\.color)

// CORRECT -- KeyPath modifiers first
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .foregroundStyle(\.color)
    .opacity(0.8)
```

### 8. Missing accessibility labels

```swift
// WRONG -- VoiceOver users get no context
Chart(data) {
    BarMark(x: .value("Month", $0.month), y: .value("Sales", $0.sales))
}

// CORRECT -- add per-mark accessibility
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .accessibilityLabel("\(item.month)")
        .accessibilityValue("\(item.sales) units sold")
}
```

### 9. Treating angle selection as category selection

`chartAngleSelection(value:)` binds the selected plottable angle value. For
pie and donut charts, map that numeric value through cumulative sector ranges
before comparing it to a category label.

## Review Checklist

- [ ] Data model uses `Identifiable` or chart uses `id:` key path
- [ ] Mark type matches goal (bar=comparison, line=trend, sector=proportion)
- [ ] Multi-series lines use `series:` parameter or `.foregroundStyle(by:)`
- [ ] Axes configured with appropriate labels, ticks, and grid lines
- [ ] Scale domain set explicitly when zero-baseline matters
- [ ] Pie/donut uses positive values, 5-7 sectors, and "Other" grouping
- [ ] Selection binding type matches axis data type (`Date?` for date axis)
- [ ] Pie/donut angle selection maps numeric angle values back to categories
- [ ] Scrollable charts set `.chartXVisibleDomain(length:)` for viewport
- [ ] Vectorized plots used for datasets exceeding 1000 points
- [ ] KeyPath modifiers applied before value modifiers on vectorized plots
- [ ] `Chart3D` used only for real 3D data or surfaces, with z scale and pose reviewed
- [ ] Accessibility labels added to marks for VoiceOver
- [ ] Chart tested with Dynamic Type and Dark Mode
- [ ] Legend visible and positioned, or intentionally hidden
- [ ] Ensure chart data model types are Sendable; update chart data on @MainActor

## References

- [Chart types and composition](references/chart-types-and-composition.md)
- [Interaction, 3D, accessibility, and performance](references/interaction-3d-accessibility-and-performance.md)
- [Styling, heat maps, and modifier reference](references/styling-heatmaps-and-reference.md)
- Apple docs: [Swift Charts](https://sosumi.ai/documentation/charts)
- Apple docs: [Creating a chart using Swift Charts](https://sosumi.ai/documentation/charts/Creating-a-chart-using-Swift-Charts)
- Apple docs: [Swift Charts updates](https://sosumi.ai/documentation/updates/swiftcharts)
- Apple docs: [Chart3D](https://sosumi.ai/documentation/charts/Chart3D)
- Apple docs: [SurfacePlot](https://sosumi.ai/documentation/charts/SurfacePlot)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
