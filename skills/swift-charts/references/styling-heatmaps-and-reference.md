# Swift Charts Styling, Heat Maps, and Modifier Reference

Read this reference only when the task matches the sections below.

## Dark Mode and Theming

### Automatic adaptation

Swift Charts inherits the current color scheme automatically. System colors
(`.blue`, `.orange`, `.green`) adapt to light and dark modes without extra code.

### Custom color palettes

Use `.chartForegroundStyleScale` to define a consistent palette:

```swift
Chart(data) { item in
    BarMark(
        x: .value("Category", item.category),
        y: .value("Value", item.value)
    )
    .foregroundStyle(by: .value("Category", item.category))
}
.chartForegroundStyleScale([
    "Electronics": .blue,
    "Clothing": .purple,
    "Food": .orange,
    "Books": .green,
    "Other": .gray
])
```

### Background and plot area styling

```swift
Chart(data) { ... }
.chartPlotStyle { plotArea in
    plotArea
        .background(.quaternary.opacity(0.3))
        .border(.quaternary, width: 0.5)
}
```

### Axis styling

```swift
.chartXAxisStyle { axis in
    axis.background(.blue.opacity(0.05))
}
```

### Testing dark mode

Always preview charts in both light and dark color schemes. In Xcode previews:

```swift
#Preview {
    ChartView()
        .preferredColorScheme(.dark)
}
```

Verify:
- Axis labels and grid lines are readable.
- Data colors maintain sufficient contrast.
- Annotations and legend text adapt properly.

---

## Heat Map Pattern

```swift
Chart(heatMapData) { item in
    RectangleMark(
        x: .value("Hour", item.hour),
        y: .value("Day", item.day)
    )
    .foregroundStyle(by: .value("Count", item.count))
}
.chartForegroundStyleScale(range: Gradient(colors: [.blue, .yellow, .red]))
```

---

## Stacking Methods

| Method | Behavior |
|---|---|
| `.standard` | Default. Regions stack on top showing absolute values. |
| `.normalized` | Scales to 0-100% proportional view. |
| `.center` | Baseline centered (streamgraph). |
| `.unstacked` | Overlapping; no stacking. |

```swift
AreaMark(
    x: .value("Date", item.date),
    y: .value("Revenue", item.revenue),
    stacking: .normalized
)
.foregroundStyle(by: .value("Category", item.category))
```

---

## MarkDimension Options

| Dimension | Description |
|---|---|
| `.automatic` | Framework decides |
| `.fixed(CGFloat)` | Exact pixel size |
| `.inset(CGFloat)` | Inset from available space |
| `.ratio(CGFloat)` | Proportion of available space (0...1) |

Use for `width`, `height` on `BarMark` and `innerRadius`, `outerRadius` on `SectorMark`.

---

## Symbol Configuration

### Built-in shapes

`circle`, `square`, `triangle`, `diamond`, `pentagon`, `plus`, `cross`, `asterisk`

```swift
PointMark(x: .value("X", item.x), y: .value("Y", item.y))
    .symbol(.diamond)
    .symbolSize(80)
```

### Data-driven symbol encoding

```swift
PointMark(x: .value("X", item.x), y: .value("Y", item.y))
    .symbol(by: .value("Category", item.category))
```

### Custom symbol view

```swift
PointMark(x: .value("X", item.x), y: .value("Y", item.y))
    .symbol {
        Image(systemName: "star.fill")
            .font(.caption2)
    }
```

---

## ChartProxy and Coordinate Conversion

Use `chartOverlay` or `chartBackground` to access `ChartProxy`:

```swift
.chartOverlay { proxy in
    GeometryReader { geometry in
        Rectangle()
            .fill(.clear)
            .contentShape(Rectangle())
            .gesture(
                DragGesture()
                    .onChanged { value in
                        let origin = geometry[proxy.plotAreaFrame].origin
                        let location = CGPoint(
                            x: value.location.x - origin.x,
                            y: value.location.y - origin.y
                        )
                        if let date: Date = proxy.value(atX: location.x) {
                            selectedDate = date
                        }
                    }
            )
    }
}
```

### Key ChartProxy methods

| Method | Purpose |
|---|---|
| `position(forX:)` | Data value to screen x-coordinate |
| `position(forY:)` | Data value to screen y-coordinate |
| `value(atX:as:)` | Screen x-coordinate to data value |
| `value(atY:as:)` | Screen y-coordinate to data value |
| `plotAreaSize` | Size of the plot area |
| `plotAreaFrame` | Anchor for the plot area frame |

---

## Quick Reference: Chart View Modifiers

### Axes
- `chartXAxis(_:)` / `chartXAxis(content:)`
- `chartYAxis(_:)` / `chartYAxis(content:)`
- `chartXAxisLabel(...)` / `chartYAxisLabel(...)`
- `chartXAxisStyle(content:)` / `chartYAxisStyle(content:)`

### Scales
- `chartXScale(domain:range:type:)` and variants
- `chartYScale(domain:range:type:)` and variants
- `chartZScale(domain:range:type:)` for `Chart3D`
- `chartForegroundStyleScale(_:)` -- custom color mapping

### 3D charts (iOS 26+)
- `Chart3D` with `SurfacePlot` or 3D mark initializers
- `chart3DPose(_:)` for interactive pose binding
- `chart3DCameraProjection(_:)` for orthographic/perspective projection

### Legend
- `chartLegend(_:)` -- visibility
- `chartLegend(position:alignment:spacing:)` -- positioning
- `chartLegend(position:alignment:spacing:content:)` -- custom content

### Selection (iOS 17+)
- `chartXSelection(value:)` / `chartXSelection(range:)`
- `chartYSelection(value:)` / `chartYSelection(range:)`
- `chartAngleSelection(value:)` -- for `SectorMark`

### Scrolling (iOS 17+)
- `chartScrollableAxes(_:)`
- `chartXVisibleDomain(length:)` / `chartYVisibleDomain(length:)`
- `chartScrollPosition(initialX:)` / `chartScrollPosition(x:)`
- `chartScrollTargetBehavior(_:)`

### Overlay and Background
- `chartOverlay(alignment:content:)` -- with `ChartProxy`
- `chartBackground(alignment:content:)` -- with `ChartProxy`
- `chartPlotStyle(content:)` -- plot area styling

---

## Apple Documentation Links

- [Swift Charts](https://sosumi.ai/documentation/charts)
- [Creating a chart using Swift Charts](https://sosumi.ai/documentation/charts/Creating-a-chart-using-Swift-Charts)
- [BarMark](https://sosumi.ai/documentation/charts/BarMark)
- [LineMark](https://sosumi.ai/documentation/charts/LineMark)
- [SectorMark](https://sosumi.ai/documentation/charts/SectorMark)
- [Chart3D](https://sosumi.ai/documentation/charts/Chart3D)
- [SurfacePlot](https://sosumi.ai/documentation/charts/SurfacePlot)
- [LinePlot](https://sosumi.ai/documentation/charts/LinePlot)
- [AxisMarks](https://sosumi.ai/documentation/charts/AxisMarks)
- [Swift Charts updates](https://sosumi.ai/documentation/updates/swiftcharts)
