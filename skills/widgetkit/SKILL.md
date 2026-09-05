---
name: widgetkit
description: "Builds or reviews WidgetKit widgets and controls for Home Screen, Lock Screen, StandBy, CarPlay, and Control Center. Use for timelines, App Intent configuration, interactive controls, push reloads, refresh budgets, deep links, Smart Stack relevance, rendering, extensions, and App Groups."
---

# WidgetKit

Build glanceable Home Screen widgets, Lock Screen complications, Control Center controls, and StandBy or CarPlay widgets using `WidgetKit`. Targets Swift 6.3 / iOS 26+.

## Contents

- [Extension Architecture](#extension-architecture)
- [Widget Families and Surfaces](#widget-families-and-surfaces)
- [Timeline Management and Reload Budgets](#timeline-management-and-reload-budgets)
- [Interactive Controls and Intent Handoff](#interactive-controls-and-intent-handoff)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Extension Architecture

1. **Separate extension target**: Widgets run in an out-of-process widget extension.
2. **Shared storage with App Groups**: Use `UserDefaults(suiteName: "group.com.example.app")` or shared container directories to share data between the main app and the widget.
3. **Widget Bundle**: Group all widgets, live activities, and controls in a single `@main` `WidgetBundle`.

```swift
@main
struct AppWidgetsBundle: WidgetBundle {
    var body: some Widget {
        OrderStatusWidget()
        QuickActionControl()
    }
}
```

## Widget Families and Surfaces

| Surface | Supported Families | Configuration | Key API |
|---|---|---|---|
| Home Screen | `.systemSmall`, `.systemMedium`, `.systemLarge`, `.systemExtraLarge` | `AppIntentConfiguration` | `containerBackground(for:)` |
| Lock Screen | `.accessoryCircular`, `.accessoryRectangular`, `.accessoryInline` | `StaticConfiguration` | Monochrome / accented styling |
| StandBy | `.systemSmall`, `.systemMedium` | Same as Home Screen | Night mode / red tint adaptation |
| Control Center | `ControlWidget` (buttons & toggles) | `StaticControlConfiguration` | `ControlWidgetButton`, `ControlWidgetToggle` |

## Timeline Management and Reload Budgets

Timelines provide entries into the future:
- `.atEnd`: Requests a new timeline after the last entry date passes.
- `.after(Date)`: Schedules a reload at a specific future timestamp.
- `.never`: Never reloads automatically; relies on app foreground reloads or push notifications.

> [!IMPORTANT]
> The system enforces a daily reload budget (typically 40-70 reloads per day). Do not schedule sub-minute reloads with `.after`. For urgent real-time state, push remote updates via `push-notifications` or use `activitykit` Live Activities.

## Interactive Controls and Intent Handoff

Widgets support interactive buttons and toggles:
- Use `Button(intent:)` and `Toggle(isOn:intent:)` conforming to `AppIntent`.
- Route detailed intent modeling and parameter resolution to `app-intents`.
- Route Dynamic Island and Lock Screen real-time progress to `activitykit`.

## Route by Task

- For timeline provider setups, deep link handling (`widgetURL`), and configurable intents, read [Timelines, Configuration, and Deep Links](references/timelines-configuration-and-deep-links.md).
- For Live Activity registration in widget bundles and push-to-update tokens, read [Live Activity Presentation and Push](references/live-activity-presentation-and-push.md).
- For memory budget limits, container backgrounds, and relevance entries for Smart Stacks, read [Performance, Setup, and Lifecycle](references/performance-setup-and-lifecycle.md).

## Common Mistakes

- Performing network requests or expensive computations inside the SwiftUI widget view instead of the `TimelineProvider`.
- Hardcoding views without `.containerBackground(for: .widget)`, breaking iOS 17+ StandBy and Lock Screen rendering.
- Scheduling timeline reloads every few seconds, rapidly exhausting the daily reload budget.
- Forgetting App Group entitlement when reading data stored by the main app.
- Attempting to display videos, web views, or complex continuous animations in widget views.

## Review Checklist

- [ ] App Group configured on both app and widget extension targets
- [ ] Timeline entries include future dates with appropriate reload policy (`.atEnd`, `.after`)
- [ ] Widget views support all declared `supportedFamilies`
- [ ] `.containerBackground` applied to all widget content views
- [ ] Accessory families designed for high-contrast, monochrome display
- [ ] Interactive controls trigger `AppIntent` without launching the main app unnecessarily
- [ ] Daily reload budget respected; urgent changes pushed via APNs

## References

- [Timelines, configuration, and deep links](references/timelines-configuration-and-deep-links.md)
- [Live Activity presentation and push](references/live-activity-presentation-and-push.md)
- [Performance, setup, and lifecycle](references/performance-setup-and-lifecycle.md)
- [WidgetKit documentation](https://sosumi.ai/documentation/widgetkit)
- [Widget](https://sosumi.ai/documentation/widgetkit/widget)
- [TimelineProvider](https://sosumi.ai/documentation/widgetkit/timelineprovider)
