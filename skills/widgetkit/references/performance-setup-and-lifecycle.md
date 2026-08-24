# WidgetKit Performance, Setup, Relevance, and Lifecycle

Read this reference only when the task matches the sections below.

## Widget Performance Best Practices

### Data Preparation

Pre-compute display values in the timeline provider. Pass display-ready data
through the entry.

```swift
// WRONG: Heavy computation in the widget view
struct MyWidgetView: View {
    let entry: RawDataEntry

    var body: some View {
        let processed = HeavyProcessor.process(entry.rawData)  // Slow
        Text(processed.summary)
    }
}

// CORRECT: Pre-compute in the provider
func timeline(for configuration: Intent, in context: Context) async -> Timeline<ProcessedEntry> {
    let raw = await DataStore.shared.fetch()
    let processed = HeavyProcessor.process(raw)
    let entry = ProcessedEntry(date: .now, summary: processed.summary, value: processed.value)
    return Timeline(entries: [entry], policy: .atEnd)
}
```

### Memory Constraints

Widget extensions run with strict memory limits. Avoid:
- Loading large images directly in the widget view
- Storing large data sets in the entry
- Creating complex view hierarchies

### Image Handling

```swift
// WRONG: Loading a full-resolution image
Image(uiImage: UIImage(contentsOfFile: fullResPath)!)

// CORRECT: Use a pre-resized thumbnail stored in the shared container
Image(uiImage: UIImage(contentsOfFile: thumbnailPath)!)
    .resizable()
    .aspectRatio(contentMode: .fill)
```

### Shared Data with App Groups

```swift
// In the main app: write data
let defaults = UserDefaults(suiteName: "group.com.example.myapp")
defaults?.set(encodedData, forKey: "widgetData")
WidgetCenter.shared.reloadTimelines(ofKind: "MyWidget")

// In the widget provider: read data
func timeline(for configuration: Intent, in context: Context) async -> Timeline<MyEntry> {
    let defaults = UserDefaults(suiteName: "group.com.example.myapp")
    let data = defaults?.data(forKey: "widgetData")
    // Decode and build entry
}
```

For larger datasets, use a shared SQLite database or Core Data store in the
App Group container.

## Xcode Setup

### Adding a Widget Extension Target

1. File > New > Target > Widget Extension.
2. Name the extension (e.g., "MyAppWidgets").
3. Select "Include Configuration App Intent" for configurable widgets.
4. Select "Include Live Activity" if building Live Activities.

### Entitlements

| Entitlement | Purpose |
|---|---|
| App Groups (`com.apple.security.application-groups`) | Share data between app and widget |
| Push Notifications (`aps-environment`) | Required for push-based Live Activity updates |

### App Groups Configuration

1. Enable "App Groups" capability on both the main app target and the widget
   extension target.
2. Create a shared group identifier (e.g., `group.com.example.myapp`).
3. Use `UserDefaults(suiteName:)` or `FileManager.containerURL(forSecurityApplicationGroupIdentifier:)`
   for shared storage.

### Build Schemes

- Use the widget extension scheme to debug widget rendering.
- Select "Widget" as the run destination to launch the widget directly.
- Use "Preview" in Xcode canvas for rapid iteration.

### Common Xcode Issues

```text
// ERROR: "Widget extension must include at least one widget"
// FIX: Ensure @main is on the WidgetBundle, not a widget struct.

// ERROR: "No such module 'WidgetKit'"
// FIX: Ensure the widget extension target links WidgetKit and SwiftUI frameworks.

// ERROR: "The operation couldn't be completed. (ActivityKit.ActivityAuthorizationError error 3.)"
// FIX: Add NSSupportsLiveActivities = YES to the HOST APP's Info.plist (not the extension).
```

## Widget Relevance and Smart Stacks

### TimelineEntryRelevance

Score entries to surface widgets in Smart Stacks when relevant:

```swift
struct GameEntry: TimelineEntry {
    var date: Date
    var score: String
    var isLive: Bool

    var relevance: TimelineEntryRelevance? {
        isLive ? TimelineEntryRelevance(score: 100, duration: 3600) : nil
    }
}
```

Higher scores make the widget more likely to surface. The `duration` specifies
how long the relevance lasts.

### WidgetRelevance (AppIntentTimelineProvider)

On iPhone and iPad, prefer `TimelineEntryRelevance` on timeline entries and
donate App Intents that match configurable widget parameters. Smart Stacks on
iPhone and iPad don't use the timeline provider's `relevance()` callback.

On watchOS, use `relevance()` only when providing RelevanceKit contextual clues.
Return `WidgetRelevance([WidgetRelevanceAttribute(...)])`; there is no
`WidgetRelevance(intent, score:)` initializer.

## ActivityState Lifecycle

Track the full lifecycle of a Live Activity:

```swift
Task {
    for await state in activity.activityStateUpdates {
        switch state {
        case .active:
            // Activity is running and visible
            break
        case .pending:
            // Requested but not yet displayed (iOS 26+)
            break
        case .stale:
            // Content is outdated; update or end
            break
        case .ended:
            // Ended but may still be visible on Lock Screen
            break
        case .dismissed:
            // Fully removed from UI; clean up resources
            break
        @unknown default:
            break
        }
    }
}
```

## ActivityStyle

Control Live Activity persistence behavior (iOS 18+):

```swift
// Standard: persists until explicitly ended
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .standard
)

// Transient: appears in Dynamic Island's extended presentation and ends
// automatically when the user leaves that interaction context.
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .transient
)
```

Use `.transient` for short interactions that should not persist as a standard
Live Activity after the user locks the device, collapses the Dynamic Island,
leaves the app, or performs other tasks outside the Dynamic Island.

## Dismissal Policies

Control when an ended Live Activity disappears from the Lock Screen:

```swift
// System-determined timing (default)
await activity.end(finalContent, dismissalPolicy: .default)

// Remove immediately
await activity.end(finalContent, dismissalPolicy: .immediate)

// Remove after a specific date (max 4 hours)
let removalDate = Date().addingTimeInterval(3600)
await activity.end(finalContent, dismissalPolicy: .after(removalDate))
```

## Querying Active Widgets and Activities

### Current Widget Configurations

```swift
let widgets = try await WidgetCenter.shared.currentConfigurations()
for widget in widgets {
    print("Kind: \(widget.kind), Family: \(widget.family)")
}
```

### Current Live Activities

```swift
let activities = Activity<DeliveryAttributes>.activities
for activity in activities {
    print("ID: \(activity.id), State: \(activity.activityState)")
}
```

### Observing New Activities

```swift
Task {
    for await activity in Activity<DeliveryAttributes>.activityUpdates {
        print("New activity started: \(activity.id)")
    }
}
```

## Design Patterns

### Prefer Gauge for Value Indicators

Use `Gauge` (iOS 16+) instead of manual `Circle` or `Path` arcs to show a value
within a range. The system handles styling, accessibility, and rendering-mode
adaptation automatically.

- `.accessoryCircular` — open ring with center value label, matches the system
  complication style. Use for `accessoryCircular` Lock Screen widgets.
- `.linearCapacity` — horizontal bar that fills leading to trailing. Use for
  home screen widgets when a capacity bar fits.

```swift
// accessoryCircular Lock Screen widget
struct StepsCircularView: View {
    let entry: StepsEntry

    var body: some View {
        Gauge(value: Double(entry.stepCount), in: 0...10000) {
            Image(systemName: "figure.walk")
        } currentValueLabel: {
            Text("\(entry.stepCount)")
        }
        .gaugeStyle(.accessoryCircular)
    }
}

// Home screen capacity bar
Gauge(value: storageUsed, in: 0...storageTotal) {
    Text("Storage")
} currentValueLabel: {
    Text(storageUsed, format: .byteCount(style: .file))
}
.gaugeStyle(.linearCapacity)
```

### Use containerBackground for Widget Backgrounds

`.containerBackground(_:for: .widget)` (iOS 17+) is the designated way to set
widget backgrounds. Replaces older padding and background patterns. The system
uses this placement to correctly render backgrounds across all widget surfaces.

```swift
struct OrderWidgetView: View {
    let entry: OrderEntry

    var body: some View {
        VStack(alignment: .leading) {
            Text(entry.orderName).font(.headline)
            Text(entry.status).foregroundStyle(.secondary)
        }
        .containerBackground(.fill.tertiary, for: .widget)
    }
}
```

### Use Canvas for Dense Visualizations

Use `Canvas` for sparklines, mini bar charts, or heat maps inside widgets. The
lack of per-element accessibility is acceptable since the entire widget surface
is a single tap target.

```swift
struct SparklineView: View {
    let values: [Double]

    var body: some View {
        Canvas { context, size in
            guard values.count > 1 else { return }
            let maxVal = values.max() ?? 1
            let step = size.width / CGFloat(values.count - 1)
            var path = Path()
            for (i, value) in values.enumerated() {
                let x = step * CGFloat(i)
                let y = size.height * (1 - value / maxVal)
                if i == 0 { path.move(to: CGPoint(x: x, y: y)) }
                else { path.addLine(to: CGPoint(x: x, y: y)) }
            }
            context.stroke(path, with: .color(.blue), lineWidth: 2)
        }
    }
}
```

### Match Timeline Refresh to Data Granularity

Apple budgets
[40–70 refreshes per day](https://sosumi.ai/documentation/widgetkit/keeping-a-widget-up-to-date)
for frequently viewed widgets, with entries at least 5 minutes apart. Align
reload cadence to how often the underlying data actually changes.

- Generate entries for as many future dates as possible to reduce reload requests.
- Use `.after(date)` when data updates on a known schedule (market hours, transit).
- Use `.never` when data only changes from user action.
- Use `Text(timerInterval:countsDown:)` for live countdowns instead of burning
  timeline entries on every tick.

## Apple Documentation Links

- [WidgetKit](https://sosumi.ai/documentation/widgetkit)
- [ActivityKit](https://sosumi.ai/documentation/activitykit)
- [TimelineProvider](https://sosumi.ai/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://sosumi.ai/documentation/widgetkit/appintenttimelineprovider)
- [ActivityAttributes](https://sosumi.ai/documentation/activitykit/activityattributes)
- [ActivityConfiguration](https://sosumi.ai/documentation/widgetkit/activityconfiguration)
- [DynamicIsland](https://sosumi.ai/documentation/widgetkit/dynamicisland)
- [ControlWidgetButton](https://sosumi.ai/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://sosumi.ai/documentation/widgetkit/controlwidgettoggle)
- [Keeping a widget up to date](https://sosumi.ai/documentation/widgetkit/keeping-a-widget-up-to-date)
- [Updating widgets with WidgetKit push notifications](https://sosumi.ai/documentation/widgetkit/updating-widgets-with-widgetkit-push-notifications)
- [Updating controls locally and remotely](https://sosumi.ai/documentation/widgetkit/updating-controls-locally-and-remotely)
- [Linking to specific app scenes](https://sosumi.ai/documentation/widgetkit/linking-to-specific-app-scenes-from-your-widget-or-live-activity)
- [Adding StandBy and CarPlay support](https://sosumi.ai/documentation/widgetkit/adding-standby-and-carplay-support-to-your-widget)
- [Optimizing for accented rendering and Liquid Glass](https://sosumi.ai/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- [Increasing widget visibility in Smart Stacks](https://sosumi.ai/documentation/widgetkit/widget-suggestions-in-smart-stacks)
