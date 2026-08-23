# Local Notifications

Use this reference when the device schedules reminders without a provider server. Keep product scheduling semantics separate from remote APNs delivery.

## Model the reminder

Define a stable request identifier so updates and cancellation target the intended reminder. Put only the minimal routing data in `userInfo`; persist authoritative domain data elsewhere.

```swift
let content = UNMutableNotificationContent()
content.title = String(localized: "Workout reminder")
content.body = String(localized: "Your scheduled workout starts soon.")
content.sound = .default
content.userInfo = ["workoutID": workout.id]
content.threadIdentifier = "workouts"
```

Check `notificationSettings()` before scheduling user-visible content. Authorization can change after onboarding. If alerts are denied, preserve the in-app reminder state and explain that system presentation is unavailable rather than silently discarding the user's intent.

## Choose a trigger

### Time interval

Use for a duration relative to scheduling. Repeating time-interval triggers require at least 60 seconds.

```swift
let trigger = UNTimeIntervalNotificationTrigger(
    timeInterval: 15 * 60,
    repeats: false
)
```

### Calendar

Use for wall-clock recurrences. Specify only the date components that define the recurrence and decide how time-zone changes should behave. Test daylight-saving transitions for calendar-sensitive products.

```swift
var components = DateComponents()
components.hour = 8
components.minute = 30

let trigger = UNCalendarNotificationTrigger(
    dateMatching: components,
    repeats: true
)
```

### Location

Use a `UNLocationNotificationTrigger` only when the product genuinely depends on region entry or exit. Request the appropriate Core Location authorization and respect platform region-monitoring limits. Route broader location behavior to `mapkit`.

## Schedule, inspect, update, and remove

```swift
let request = UNNotificationRequest(
    identifier: "workout-\(workout.id)",
    content: content,
    trigger: trigger
)

let center = UNUserNotificationCenter.current()
try await center.add(request)
let pending = await center.pendingNotificationRequests()
```

Adding a request with an existing identifier replaces the pending request. Remove pending requests when the underlying reminder is deleted or disabled. Removing a pending request doesn't remove an already delivered notification; manage delivered notifications separately.

```swift
center.removePendingNotificationRequests(withIdentifiers: [identifier])
center.removeDeliveredNotifications(withIdentifiers: [identifier])
```

Avoid `removeAll…` in a feature-level operation unless the product explicitly owns every notification created by the app.

## Categories, attachments, and grouping

Register categories/actions during app launch and set `content.categoryIdentifier` before scheduling. Create attachments from supported files the app can read; remote URLs must be downloaded to disk before attachment creation. For custom extension UI or bounded media downloads, read [rich-notifications.md](rich-notifications.md).

Use `threadIdentifier`, `summaryArgument`, and `summaryArgumentCount` only when grouping matches the user's mental model. Badge counts need an explicit source-of-truth policy; don't increment and decrement opportunistically across devices.

## Verification

- Test the next trigger date rather than assuming calendar components produce the intended schedule.
- Inspect pending requests after create, edit, disable, and delete flows.
- Test authorization denied, provisional, and settings-changed states.
- Verify foreground presentation and response routing separately.
- Test long localized content, multiple reminders, restart, time-zone change, daylight-saving transition, and device reboot where relevant.
- Use deterministic identifiers and injected calendar/clock dependencies in unit tests when scheduling rules are complex.

## Sources

- [Scheduling a notification locally from your app](https://sosumi.ai/documentation/usernotifications/scheduling-a-notification-locally-from-your-app)
- [UNNotificationRequest](https://sosumi.ai/documentation/usernotifications/unnotificationrequest)
- [UNCalendarNotificationTrigger](https://sosumi.ai/documentation/usernotifications/uncalendarnotificationtrigger)
