# Swift Charts Types and Composition Patterns

Extended patterns, accessibility guidance, and theming for Swift Charts on
iOS 26+. Import `Charts` in every file that uses these APIs.

```swift
import SwiftUI
import Charts
```

---

## Data Modeling

Use `@Observable` for chart data models. Pair with `@State` in views.

```swift
@Observable
class SalesModel {
    var monthlySales: [MonthlySale] = []

    func load() async {
        monthlySales = await SalesService.fetchMonthlySales()
    }
}

struct MonthlySale: Identifiable {
    let id = UUID()
    let month: Date
    let revenue: Double
    let category: String
}
```

```swift
struct SalesDashboard: View {
    @State private var model = SalesModel()

    var body: some View {
        Chart(model.monthlySales) { item in
            BarMark(
                x: .value("Month", item.month, unit: .month),
                y: .value("Revenue", item.revenue)
            )
            .foregroundStyle(by: .value("Category", item.category))
        }
        .task { await model.load() }
    }
}
```

---

## Bar Chart Patterns

### Simple vertical bars

```swift
Chart(data) { item in
    BarMark(
        x: .value("Department", item.department),
        y: .value("Revenue", item.revenue)
    )
}
```

### Stacked bars (automatic)

When multiple bars share the same x value, they stack automatically:

```swift
Chart(data) { item in
    BarMark(
        x: .value("Quarter", item.quarter),
        y: .value("Sales", item.sales)
    )
    .foregroundStyle(by: .value("Product", item.product))
}
```

### Grouped bars

Use `.position(by:)` to place bars side by side instead of stacking:

```swift
Chart(data) { item in
    BarMark(
        x: .value("Quarter", item.quarter),
        y: .value("Sales", item.sales)
    )
    .foregroundStyle(by: .value("Product", item.product))
    .position(by: .value("Product", item.product))
}
```

### Horizontal bars

Swap the x and y axes:

```swift
Chart(data) { item in
    BarMark(
        x: .value("Sales", item.sales),
        y: .value("Region", item.region)
    )
}
.chartYAxis {
    AxisMarks { _ in
        AxisValueLabel()
    }
}
```

### Normalized stacked bars (100%)

```swift
Chart(data) { item in
    BarMark(
        x: .value("Quarter", item.quarter),
        y: .value("Sales", item.sales),
        stacking: .normalized
    )
    .foregroundStyle(by: .value("Product", item.product))
}
```

### Bar with annotation

```swift
Chart(data) { item in
    BarMark(
        x: .value("Month", item.month),
        y: .value("Revenue", item.revenue)
    )
    .annotation(position: .top, alignment: .center, spacing: 4) {
        Text(item.revenue, format: .currency(code: "USD").precision(.fractionLength(0)))
            .font(.caption2)
    }
}
```

### Gantt chart (interval bars)

```swift
Chart(tasks) { task in
    BarMark(
        xStart: .value("Start", task.startDate),
        xEnd: .value("End", task.endDate),
        y: .value("Task", task.name)
    )
    .foregroundStyle(by: .value("Status", task.status))
}
```

---

## Line Chart Patterns

### Single line with points

```swift
Chart(data) { item in
    LineMark(
        x: .value("Date", item.date),
        y: .value("Price", item.price)
    )
    PointMark(
        x: .value("Date", item.date),
        y: .value("Price", item.price)
    )
    .symbolSize(30)
}
```

### Multi-series lines

```swift
Chart(temperatures) { item in
    LineMark(
        x: .value("Date", item.date),
        y: .value("Temp", item.temperature)
    )
    .foregroundStyle(by: .value("City", item.city))
    .symbol(by: .value("City", item.city))
}
```

### Line with area fill

```swift
Chart(data) { item in
    AreaMark(
        x: .value("Date", item.date),
        y: .value("Value", item.value)
    )
    .foregroundStyle(
        .linearGradient(
            colors: [.blue.opacity(0.3), .blue.opacity(0.05)],
            startPoint: .top,
            endPoint: .bottom
        )
    )
    LineMark(
        x: .value("Date", item.date),
        y: .value("Value", item.value)
    )
    .foregroundStyle(.blue)
}
```

### Interpolation methods

| Method | Use Case |
|---|---|
| `.linear` | Default; straight segments between points |
| `.monotone` | Smooth curve that preserves monotonicity |
| `.catmullRom` | Smooth general-purpose curve |
| `.cardinal` | Smooth with adjustable tension |
| `.stepStart` | Step function starting at data point |
| `.stepCenter` | Step function centered on data point |
| `.stepEnd` | Step function ending at data point |

```swift
LineMark(x: .value("X", item.x), y: .value("Y", item.y))
    .interpolationMethod(.monotone)
```

### Sparkline (minimal inline chart)

```swift
Chart(recentData) { item in
    LineMark(
        x: .value("Time", item.time),
        y: .value("Value", item.value)
    )
    .interpolationMethod(.catmullRom)
}
.chartXAxis(.hidden)
.chartYAxis(.hidden)
.chartLegend(.hidden)
.frame(width: 80, height: 30)
```

---

## Pie and Donut Chart Patterns (SectorMark, iOS 17+)

Use strictly positive values for sectors. Filter, aggregate, or show zero and
negative values outside the pie or donut so angular sizes remain meaningful.

### Basic pie chart

```swift
Chart(products, id: \.name) { item in
    SectorMark(angle: .value("Sales", item.sales))
        .foregroundStyle(by: .value("Product", item.name))
}
```

### Donut chart with golden ratio inner radius

```swift
Chart(products, id: \.name) { item in
    SectorMark(
        angle: .value("Sales", item.sales),
        innerRadius: .ratio(0.618),
        outerRadius: .inset(10),
        angularInset: 1
    )
    .cornerRadius(4)
    .foregroundStyle(by: .value("Product", item.name))
}
```

### Donut chart with center label

```swift
Chart(products, id: \.name) { item in
    SectorMark(
        angle: .value("Sales", item.sales),
        innerRadius: .ratio(0.618),
        angularInset: 1
    )
    .cornerRadius(4)
    .foregroundStyle(by: .value("Product", item.name))
}
.chartBackground { _ in
    VStack {
        Text("Total")
            .font(.caption)
            .foregroundStyle(.secondary)
        Text("\(totalSales, format: .number)")
            .font(.title2.bold())
    }
}
```

### Angular selection on donut

```swift
struct ProductSales: Identifiable {
    let id = UUID()
    let name: String
    let sales: Double
}

@State private var selectedAngle: Double?

var selectedProduct: ProductSales? {
    guard let selectedAngle else { return nil }
    var runningTotal = 0.0

    return products.first { product in
        let range = runningTotal..<(runningTotal + product.sales)
        runningTotal += product.sales
        return range.contains(selectedAngle)
    }
}

Chart(products, id: \.name) { item in
    SectorMark(
        angle: .value("Sales", item.sales),
        innerRadius: .ratio(0.618),
        angularInset: 1
    )
    .cornerRadius(4)
    .foregroundStyle(by: .value("Product", item.name))
    .opacity(selectedProduct == nil || selectedProduct?.name == item.name ? 1.0 : 0.4)
}
.chartAngleSelection(value: $selectedAngle)
```

`chartAngleSelection(value:)` binds the selected plottable angle value, not the
sector label. Convert that value through cumulative sector ranges before using
it to highlight or annotate a category.

### Grouping small slices

Limit pie/donut charts to 5-7 positive-value sectors. Group the rest into "Other":

```swift
func groupSmallSlices(_ data: [CategorySales], topN: Int = 5) -> [CategorySales] {
    let sorted = data.sorted { $0.sales > $1.sales }
    let top = Array(sorted.prefix(topN))
    let otherTotal = sorted.dropFirst(topN).reduce(0) { $0 + $1.sales }
    guard otherTotal > 0 else { return top }
    return top + [CategorySales(name: "Other", sales: otherTotal)]
}
```

---

## Combined Chart Patterns

### Line + area (trend with fill)

```swift
Chart(data) { item in
    AreaMark(
        x: .value("Date", item.date),
        yStart: .value("Min", item.low),
        yEnd: .value("Max", item.high)
    )
    .foregroundStyle(.blue.opacity(0.15))

    LineMark(
        x: .value("Date", item.date),
        y: .value("Average", item.average)
    )
    .foregroundStyle(.blue)
    .lineStyle(StrokeStyle(lineWidth: 2))
}
```

### Bar + threshold rule

```swift
Chart {
    ForEach(data) { item in
        BarMark(
            x: .value("Month", item.month),
            y: .value("Revenue", item.revenue)
        )
    }
    RuleMark(y: .value("Target", targetRevenue))
        .foregroundStyle(.red)
        .lineStyle(StrokeStyle(lineWidth: 1, dash: [5, 3]))
        .annotation(position: .top, alignment: .leading) {
            Text("Target: \(targetRevenue, format: .number)")
                .font(.caption)
                .foregroundStyle(.red)
        }
}
```

### Scatter + trend line

```swift
Chart {
    ForEach(data) { item in
        PointMark(
            x: .value("Experience", item.yearsExperience),
            y: .value("Salary", item.salary)
        )
        .opacity(0.6)
    }
    LinePlot(x: "Experience", y: "Salary", domain: 0...20) { x in
        baseSalary + x * salaryPerYear  // linear trend
    }
    .foregroundStyle(.red)
    .lineStyle(StrokeStyle(lineWidth: 1.5, dash: [4, 2]))
}
```

---
