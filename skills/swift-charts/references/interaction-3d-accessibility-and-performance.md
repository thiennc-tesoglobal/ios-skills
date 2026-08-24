# Swift Charts Interaction, 3D, Accessibility, and Performance

Read this reference only when the task matches the sections below.

## Chart Selection with Overlay Annotation

Show a tooltip at the selected position using `chartOverlay`:

```swift
@State private var selectedDate: Date?

var body: some View {
    Chart(data) { item in
        LineMark(
            x: .value("Date", item.date),
            y: .value("Value", item.value)
        )
        if let selectedDate,
           let match = data.first(where: { Calendar.current.isDate($0.date, inSameDayAs: selectedDate) }) {
            RuleMark(x: .value("Selected", match.date))
                .foregroundStyle(.secondary)
            PointMark(
                x: .value("Date", match.date),
                y: .value("Value", match.value)
            )
            .symbolSize(60)
            .annotation(position: .top) {
                Text("\(match.value, format: .number)")
                    .font(.caption)
                    .padding(4)
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 4))
            }
        }
    }
    .chartXSelection(value: $selectedDate)
}
```

---

## Scrollable Chart with Visible Domain

```swift
@State private var scrollPosition: Date?

var body: some View {
    Chart(dailySteps) { item in
        BarMark(
            x: .value("Date", item.date, unit: .day),
            y: .value("Steps", item.steps)
        )
    }
    .chartScrollableAxes(.horizontal)
    .chartXVisibleDomain(length: 3600 * 24 * 7) // 7 days
    .chartScrollPosition(x: $scrollPosition)
    .chartScrollTargetBehavior(
        .valueAligned(matching: DateComponents(hour: 0), majorAlignment: .page)
    )
    .chartXAxis {
        AxisMarks(values: .stride(by: .day)) { value in
            AxisGridLine()
            AxisValueLabel(format: .dateTime.weekday(.abbreviated))
        }
    }
}
```

---

## Function Plotting (LinePlot, iOS 18+)

### Standard function y = f(x)

```swift
Chart {
    LinePlot(x: "x", y: "y", domain: -2 * .pi ... 2 * .pi) { x in
        sin(x)
    }
    .foregroundStyle(.blue)
}
.chartYScale(domain: -1.5...1.5)
```

### Parametric function (x, y) = f(t)

```swift
Chart {
    LinePlot(x: "x", y: "y", t: "t", domain: 0 ... 2 * .pi) { t in
        (x: cos(t), y: sin(t))
    }
}
.chartXScale(domain: -1.5...1.5)
.chartYScale(domain: -1.5...1.5)
```

### Range area function

```swift
Chart {
    AreaPlot(x: "x", yStart: "min", yEnd: "max", domain: 0...10) { x in
        (yStart: sin(x) - 0.5, yEnd: sin(x) + 0.5)
    }
    .foregroundStyle(.blue.opacity(0.2))
}
```

---

## 3D Charts and Surfaces (Chart3D, iOS 26+)

Use `Chart3D` when the data has a real third dimension, such as `(x, y, z)`
points, 3D regions, or a bivariate surface. Keep ordinary category comparison,
time series, and proportions in 2D charts because they are easier to label,
compare, and make accessible.

### SurfacePlot for bivariate functions

```swift
@State private var pose: Chart3DPose = .default

Chart3D {
    SurfacePlot(x: "x", y: "y", z: "z") { x, z in
        sin(2 * x) * cos(2 * z)
    }
    .foregroundStyle(.heightBased)
}
.chartXScale(domain: -2...2)
.chartYScale(domain: -1...1)
.chartZScale(domain: -2...2)
.chart3DPose($pose)
```

### 3D point cloud

```swift
Chart3D(points) { point in
    PointMark(
        x: .value("Width", point.x),
        y: .value("Height", point.y),
        z: .value("Depth", point.z)
    )
    .foregroundStyle(by: .value("Cluster", point.cluster))
}
.chart3DCameraProjection(.perspective)
```

### 3D review notes

- Confirm the z dimension is meaningful and labeled; do not use depth only for decoration.
- Set explicit x/y/z domains when users need stable comparisons across states.
- Bind `Chart3DPose` when users need to inspect the scene interactively.
- Use `SurfacePlot` for `y = f(x, z)` surfaces; use 3D mark initializers for observed data points or regions.

---

## Accessibility

### Baseline VoiceOver support

Swift Charts can derive baseline accessibility information from descriptive
`.value("Label", ...)` metadata. Do not treat that as a complete VoiceOver
experience: add explicit labels and values when raw axis metadata lacks context,
and verify the reading order and spoken result on the target OS.

### Custom accessibility labels

```swift
Chart(data) { item in
    BarMark(
        x: .value("Month", item.month),
        y: .value("Sales", item.sales)
    )
    .accessibilityLabel("Sales for \(item.month)")
    .accessibilityValue("\(item.sales) units sold")
}
```

### Accessibility on vectorized plots (KeyPath-based)

```swift
BarPlot(data, x: .value("Month", \.month), y: .value("Sales", \.sales))
    .accessibilityLabel(\.accessibilityDescription)
    .accessibilityValue(\.formattedSales)
```

### Audio graphs

The system automatically generates audio representations of chart data for
VoiceOver users. Use clear, consistent data labels to ensure audio graphs
convey meaningful patterns.

### Best practices

- Use descriptive strings in `.value("Label", ...)` -- these become VoiceOver labels.
- Add `.accessibilityLabel` and `.accessibilityValue` for context beyond raw numbers.
- Test with VoiceOver enabled: navigate the chart and verify each element is announced.
- Avoid `.accessibilityHidden(true)` on data-bearing marks.

---

## Dynamic Type and Color Considerations

### Dynamic Type

Charts automatically adjust axis label sizes with Dynamic Type. Avoid fixed
frame heights that clip labels at larger text sizes.

```swift
// WRONG -- clips at large text sizes
Chart(data) { ... }
    .frame(height: 200)

// CORRECT -- adaptive height
Chart(data) { ... }
    .frame(minHeight: 200)
    .frame(maxHeight: 400)
```

Test charts at the "Accessibility Extra Extra Extra Large" text size to verify
axis labels, annotations, and legends remain readable.

### Color

- Avoid encoding meaning solely in color. Pair `.foregroundStyle(by:)` with
  `.symbol(by:)` or `.lineStyle(by:)` for distinguishability.
- Use system colors that adapt to both light and dark modes.
- Test with color blindness simulations in the Accessibility Inspector.

```swift
LineMark(x: .value("Date", item.date), y: .value("Value", item.value))
    .foregroundStyle(by: .value("Category", item.category))
    .symbol(by: .value("Category", item.category))
    .lineStyle(by: .value("Category", item.category))
```

---

## Performance: Vectorized Plots for Large Datasets

For datasets exceeding 1000 data points, use vectorized plot types instead of
individual marks. Vectorized plots accept entire collections and render
efficiently.

### When to use vectorized plots

| Data Points | Recommended Approach |
|---|---|
| < 100 | Individual marks (`BarMark`, `LineMark`, etc.) |
| 100 - 1000 | Either approach; profile if performance matters |
| > 1000 | Vectorized plots (`BarPlot`, `LinePlot`, etc.) |

### Data-driven vectorized plot

```swift
struct SensorReading: Identifiable {
    let id: Int
    let timestamp: Date
    let temperature: Double
    var color: Color { temperature > 30 ? .red : .blue }
    var accessibilityDescription: Text {
        Text("\(timestamp.formatted(.dateTime.hour().minute())): \(temperature, specifier: "%.1f") degrees")
    }
}

Chart {
    LinePlot(
        readings,
        x: .value("Time", \.timestamp),
        y: .value("Temperature", \.temperature)
    )
    .foregroundStyle(.blue)
}
```

### KeyPath modifier ordering

Apply KeyPath-based modifiers before simple-value modifiers:

```swift
// WRONG
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .opacity(0.8)                // value modifier
    .foregroundStyle(\.color)    // KeyPath -- compiler error

// CORRECT
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .foregroundStyle(\.color)    // KeyPath first
    .opacity(0.8)                // value modifier second
```

### Available vectorized plot types

| Plot Type | Mark Equivalent | Available From |
|---|---|---|
| `BarPlot` | `BarMark` | iOS 18+ |
| `LinePlot` | `LineMark` | iOS 18+ |
| `PointPlot` | `PointMark` | iOS 18+ |
| `AreaPlot` | `AreaMark` | iOS 18+ |
| `RulePlot` | `RuleMark` | iOS 18+ |
| `RectanglePlot` | `RectangleMark` | iOS 18+ |
| `SectorPlot` | `SectorMark` | iOS 18+ |

---
