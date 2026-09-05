---
name: alarmkit
description: "Builds AlarmKit alarms and countdowns with system Lock Screen, Dynamic Island, StandBy, and Apple Watch presentation. Use for authorization, AlarmManager scheduling, stop/secondary actions, countdown extension handoff, state observation, or Live Activity-backed alarm experiences."
---

# AlarmKit

Schedule prominent alarms and countdown timers that surface on the Lock Screen, Dynamic Island, StandBy, and paired Apple Watch when firing. Targets iOS 26+ / iPadOS 26+.

> **UI Boundary:** AlarmKit alerts use system-managed alert UI that breaks through Focus and Silent modes. Custom UI is limited to countdown and paused Live Activity states rendered by a Widget Extension.

## Contents

- [Authorization & Setup](#authorization--setup)
- [Scheduling Alarms](#scheduling-alarms)
- [Countdown Timers](#countdown-timers)
- [Alarm State Observation](#alarm-state-observation)
- [Widget Extension Live Activity](#widget-extension-live-activity)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Authorization & Setup

Add `NSAlarmKitUsageDescription` to Info.plist. Request authorization before scheduling alarms:

```swift
import AlarmKit

func setupAlarmKit() async throws {
    let status = await AlarmManager.shared.requestAuthorization()
    guard status == .authorized else { throw AlarmError.unauthorized }
}
```

## Scheduling Alarms

Construct and schedule an alarm with firing date and stop actions:

```swift
let alarm = Alarm(
    id: UUID(),
    schedule: .time(Date().addingTimeInterval(3600)),
    title: "Morning Medication",
    stopAction: .dismiss,
    secondaryAction: .snooze(duration: 300)
)

try await AlarmManager.shared.schedule(alarm)
```

## Countdown Timers

Create active countdown experiences that present live timers across Dynamic Island and Lock Screen:

```swift
let timer = Alarm(
    id: UUID(),
    schedule: .countdown(duration: 600),
    title: "Tea Steep",
    stopAction: .dismiss
)

try await AlarmManager.shared.schedule(timer)
```

## Alarm State Observation

Observe active alarms and firing transitions asynchronously:

```swift
Task {
    for await activeAlarms in AlarmManager.shared.alarms {
        for alarm in activeAlarms {
            print("Alarm \(alarm.title): \(alarm.state)")
        }
    }
}
```

## Widget Extension Live Activity

Render custom UI for countdown and paused states in a Widget Extension conforming to `ActivityConfiguration(for: AlarmAttributes<MyMetadata>.self)`:

```swift
import WidgetKit
import SwiftUI
import AlarmKit

struct AlarmLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: AlarmAttributes<MyMetadata>.self) { context in
            // Lock Screen presentation
            Text(context.state.presentationState.title)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Image(systemName: "alarm")
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.schedule, style: .timer)
                }
            } compactLeading: {
                Image(systemName: "alarm")
            } compactTrailing: {
                Text(context.state.schedule, style: .timer)
            } minimal: {
                Image(systemName: "alarm")
            }
        }
    }
}
```

## Common Mistakes

- **Attempting custom firing alert UI**: Firing alerts are strictly system-managed. Custom views only apply to countdown Live Activities.
- **Missing NSAlarmKitUsageDescription**: Throws unhandled exceptions when calling `requestAuthorization()`.
- **Scheduling without authorization check**: Alarms scheduled while unauthorized fail silently or throw errors.
- **Ignoring state observation stream**: Fails to update in-app UI when the user dismisses an alarm via the Lock Screen or Apple Watch.
- **Confusing AlarmKit with UserNotifications**: Use AlarmKit for critical alarms that must break through Silent/Focus; use UserNotifications for standard app alerts.

## Review Checklist

- [ ] `NSAlarmKitUsageDescription` declared in target Info.plist
- [ ] `AlarmManager.shared.requestAuthorization()` confirmed authorized
- [ ] Firing schedule and stop/snooze actions configured
- [ ] Widget Extension matches `AlarmAttributes` generic metadata
- [ ] State changes observed via `AlarmManager.shared.alarms`

## References

- Patterns and code: [references/alarmkit-patterns.md](references/alarmkit-patterns.md)
- [AlarmKit](https://sosumi.ai/documentation/alarmkit)
- [AlarmManager](https://sosumi.ai/documentation/alarmkit/alarmmanager)
- [AlarmAttributes](https://sosumi.ai/documentation/alarmkit/alarmattributes)
- [Scheduling an alarm](https://sosumi.ai/documentation/alarmkit/scheduling-an-alarm-with-alarmkit)
