# WidgetKit Timelines, Configuration, and Deep Links

This reference is WidgetKit-first. ActivityKit and App Intents details appear
only where they affect widget bundles, Live Activity registration, controls, or
Smart Stack visibility; use sibling `activitykit` and `app-intents` skills for
full lifecycle, APNs content-state, Siri/Shortcuts/Spotlight, and entity-query
design.

## Timeline Strategies

### TimelineReloadPolicy

Control when WidgetKit requests a new timeline after the current entries expire.

| Policy | Behavior | Use When |
|---|---|---|
| `.atEnd` | Requests a new timeline after the last entry's date. Default. | Data changes unpredictably. |
| `.after(Date)` | Requests a new timeline after a specific date. | Data updates on a known schedule (market hours, flights). |
| `.never` | No automatic refresh. App must trigger manually. | Data changes only from user action. |

### Multiple Timeline Entries

Pre-generate entries for known future states to reduce refresh requests and
conserve the daily budget.

```swift
func timeline(for configuration: Intent, in context: Context) async -> Timeline<StockEntry> {
    var entries: [StockEntry] = []
    let now = Date()

    // Generate hourly entries for the next 6 hours
    for hourOffset in 0..<6 {
        let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: now)!
        let price = await StockService.shared.projectedPrice(at: entryDate, for: configuration.symbol)
        entries.append(StockEntry(date: entryDate, symbol: configuration.symbol.name, price: price))
    }

    let nextRefresh = Calendar.current.date(byAdding: .hour, value: 6, to: now)!
    return Timeline(entries: entries, policy: .after(nextRefresh))
}
```

### Triggering Manual Reloads

```swift
// Reload a specific widget kind
WidgetCenter.shared.reloadTimelines(ofKind: "OrderStatusWidget")

// Reload all widgets
WidgetCenter.shared.reloadAllTimelines()
```

Call `reloadTimelines(ofKind:)` only when displayed data actually changes. Each
call counts against the daily refresh budget.

### Refresh Budget

Each configured widget has a daily refresh limit. Exemptions apply for:
- Foreground app usage
- Active media sessions
- Standard location service usage

WidgetKit does not impose refresh limits when debugging in Xcode.

## Push-Based Widget and Control Reloads

### WidgetPushHandler

Use WidgetKit push notifications as a budgeted, opportunistic reload signal in
addition to normal timelines. Add the Push Notifications capability to the
widget extension, implement `WidgetPushHandler`, and register the handler on the
widget configuration with `.pushHandler(...)`.

```swift
struct MyWidgetPushHandler: WidgetPushHandler {
    func pushTokenDidChange(_ pushInfo: WidgetPushInfo, widgets: [WidgetInfo]) {
        let tokenString = pushInfo.token.map { String(format: "%02x", $0) }.joined()
        Task {
            try await ServerAPI.shared.register(widgetPushToken: tokenString)
        }
    }
}

struct CaffeineTrackerWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "CaffeineTracker", provider: Provider()) { entry in
            CaffeineTrackerView(entry: entry)
        }
        .configurationDisplayName("Caffeine Tracker")
        .pushHandler(MyWidgetPushHandler.self)
    }
}
```

### Server-Side Integration

Send an APNs push with the widget's push token. The system calls your
`TimelineProvider.getTimeline` or `AppIntentTimelineProvider.timeline(for:in:)`
when the push arrives. Use `apns-push-type: widgets`, an `apns-topic` of
`<bundleID>.push-type.widgets`, and an `aps` payload with
`"content-changed": true`. WidgetKit push notifications cannot use broadcast
channels. Treat this as a reload signal; keep durable state in shared storage
or refetch it when the provider runs.

### ControlPushHandler

Controls use their own push handler and APNs push type. Register the handler on
the `ControlWidgetConfiguration` with `.pushHandler(...)`.

```swift
struct GarageDoorControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "GarageDoor") {
            ControlWidgetButton(action: OpenGarageDoorIntent()) {
                Label("Garage", systemImage: "door.garage.open")
            }
        }
        .pushHandler(MyControlPushHandler.self)
    }
}

struct MyControlPushHandler: ControlPushHandler {
    func pushTokensDidChange(controls: [ControlInfo]) {
        for control in controls {
            guard let token = control.pushInfo?.token else { continue }
            let tokenString = token.map { String(format: "%02x", $0) }.joined()
            Task {
                try await ServerAPI.shared.register(controlPushToken: tokenString)
            }
        }
    }
}
```

For remote control reloads, use `apns-push-type: controls`, an `apns-topic` of
`<bundleID>.push-type.controls`, and an `aps` payload with
`"content-changed": true`. Do not encode the control's new state as a custom
payload key and expect WidgetKit to apply it; update shared state through the
app, server, or control action, then let the value provider read it.

For `ControlWidgetToggle`, the action must conform to `SetValueIntent` with a
Boolean value. The system fills `value` with the new toggle state.

```swift
struct ToggleFlashlightIntent: SetValueIntent {
    static var title: LocalizedStringResource = "Toggle Flashlight"

    @Parameter(title: "On")
    var value: Bool

    func perform() async throws -> some IntentResult {
        try await FlashlightController.shared.setEnabled(value)
        return .result()
    }
}
```

## Widget URL Handling and Deep Links

### widgetURL(_:)

Set a single URL for the entire widget. Tapping anywhere opens the app with this URL.

```swift
struct SmallWidgetView: View {
    let entry: OrderEntry

    var body: some View {
        VStack {
            Text(entry.orderName)
            Text(entry.status)
        }
        .widgetURL(URL(string: "myapp://orders/\(entry.orderID)")!)
    }
}
```

### Link (Multiple Targets)

Use `Link` for multiple tap targets in `.accessoryRectangular`, `.systemSmall`,
and larger system widgets. You can combine one `widgetURL(_:)` for the general
surface with `Link` controls for specific subregions.

```swift
struct MediumWidgetView: View {
    let entry: OrderListEntry

    var body: some View {
        VStack {
            ForEach(entry.orders) { order in
                Link(destination: URL(string: "myapp://orders/\(order.id)")!) {
                    HStack {
                        Text(order.name)
                        Spacer()
                        Text(order.status)
                    }
                }
            }
        }
    }
}
```

### Handling in the App

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onOpenURL { url in
                    DeepLinkRouter.shared.handle(url)
                }
        }
    }
}
```

**Important:** If the view hierarchy includes more than one `widgetURL(_:)`,
the behavior is undefined. Use `Link` for additional targets.

## Intent-Driven Widget Configuration

WidgetKit uses `WidgetConfigurationIntent` as the configuration type for
`AppIntentConfiguration` and `AppIntentTimelineProvider`. Keep the intent type
available to the widget extension or a shared framework linked into it. Design
of `AppEntity`, `EntityQuery`, Siri, Shortcuts, Spotlight, and parameter
resolution belongs in the sibling `app-intents` skill.

WidgetKit integration points to review here:
- `AppIntentConfiguration(kind:intent:provider:content:)` uses the intent type.
- `AppIntentTimelineProvider` receives that intent in `snapshot` and `timeline`.
- `recommendations()` may return `AppIntentRecommendation` values for the
  widget gallery.

Do not expand this section into full intent/entity examples; route that work to
`app-intents`.

## Multiple Widget Support in WidgetBundle

### Declaring Multiple Widgets

```swift
@main
struct MyAppWidgets: WidgetBundle {
    var body: some Widget {
        OrderStatusWidget()          // Home Screen widget
        FavoritesWidget()            // Configurable widget
        StepsAccessoryWidget()       // Lock Screen widget
        DeliveryActivityWidget()     // Live Activity
        QuickActionControl()         // Control Center
    }
}
```

### Conditional Widgets

Include widgets conditionally based on platform or availability:

```swift
@main
struct MyAppWidgets: WidgetBundle {
    var body: some Widget {
        CoreWidget()
        if #available(iOS 18, *) {
            QuickActionControl()
        }
    }
}
```

## Widget Previews and Snapshots

### Xcode Previews

```swift
#Preview("Small", as: .systemSmall) {
    OrderStatusWidget()
} timeline: {
    OrderEntry(date: .now, orderName: "Pizza", status: "Preparing")
    OrderEntry(date: .now.addingTimeInterval(600), orderName: "Pizza", status: "Delivering")
}

#Preview("Circular", as: .accessoryCircular) {
    StepsAccessoryWidget()
} timeline: {
    StepsEntry(date: .now, stepCount: 4200)
}
```

### Live Activity Previews

```swift
#Preview("Lock Screen", as: .content, using: DeliveryAttributes.preview) {
    DeliveryActivityWidget()
} contentStates: {
    DeliveryAttributes.ContentState(
        driverName: "Alex",
        estimatedDeliveryTime: Date()...Date().addingTimeInterval(900),
        currentStep: .delivering
    )
}

#Preview("Dynamic Island Compact", as: .dynamicIsland(.compact), using: DeliveryAttributes.preview) {
    DeliveryActivityWidget()
} contentStates: {
    DeliveryAttributes.ContentState(
        driverName: "Alex",
        estimatedDeliveryTime: Date()...Date().addingTimeInterval(900),
        currentStep: .delivering
    )
}
```

### Snapshot Best Practices

- Return sample data immediately in `placeholder(in:)` -- it must be synchronous.
- In `getSnapshot` / `snapshot(for:in:)`, check `context.isPreview`:
  - When `true`, return representative sample data quickly.
  - When `false`, return the current real state.

```swift
// WRONG: Performing a network call in placeholder
func placeholder(in context: Context) -> MyEntry {
    // Compilation error: placeholder must be synchronous
    let data = await fetchData()
    return MyEntry(date: .now, data: data)
}

// CORRECT: Return static sample data
func placeholder(in context: Context) -> MyEntry {
    MyEntry(date: .now, data: SampleData.placeholder)
}
```

## AccessoryWidgetBackground

Provide the standard translucent background for Lock Screen widgets.

```swift
struct CircularStepsView: View {
    let steps: Int

    var body: some View {
        ZStack {
            AccessoryWidgetBackground()
            VStack(spacing: 2) {
                Image(systemName: "figure.walk")
                    .font(.caption)
                Text("\(steps)")
                    .font(.headline)
                    .widgetAccentable()
            }
        }
    }
}
```

### Rendering Mode Awareness

Lock Screen widgets render in `.vibrant` or `.accented` mode. Adapt content:

```swift
@Environment(\.widgetRenderingMode) var renderingMode

var body: some View {
    switch renderingMode {
    case .fullColor:
        ColorfulView()
    case .vibrant, .accented:
        MonochromeView()
    @unknown default:
        MonochromeView()
    }
}
```

Use `.widgetAccentable()` to mark views that should receive the accent tint in
`.accented` rendering mode.

For images that need special treatment in accented mode, use
`Image.widgetAccentedRenderingMode(_:)`. Reserve `.fullColor` for content such
as album art or book covers where preserving the original image matters.

```swift
Image("album-art")
    .resizable()
    .widgetAccentedRenderingMode(.fullColor)
```
