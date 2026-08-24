# WidgetKit Live Activity Presentation and Push

Read this reference only when the task matches the sections below.

## Dynamic Island Expanded Layout Patterns

### Full Layout Example

```swift
DynamicIsland {
    DynamicIslandExpandedRegion(.leading) {
        VStack(alignment: .leading) {
            Image(systemName: "airplane")
                .font(.title2)
            Text("UA 1234")
                .font(.caption2)
        }
    }
    DynamicIslandExpandedRegion(.trailing) {
        VStack(alignment: .trailing) {
            Text("SFO")
                .font(.title3.bold())
            Text("On Time")
                .font(.caption2)
                .foregroundStyle(.green)
        }
    }
    DynamicIslandExpandedRegion(.center) {
        Text("San Francisco to New York")
            .font(.caption)
            .lineLimit(1)
    }
    DynamicIslandExpandedRegion(.bottom) {
        ProgressView(value: 0.45)
            .tint(.blue)
        HStack {
            Text("Departed 2:30 PM")
            Spacer()
            Text("Arrives 10:45 PM")
        }
        .font(.caption2)
        .foregroundStyle(.secondary)
    }
} compactLeading: {
    Image(systemName: "airplane")
} compactTrailing: {
    Text("2h 15m")
        .monospacedDigit()
} minimal: {
    Image(systemName: "airplane")
}
```

### Vertical Placement

Control vertical alignment within expanded regions:

```swift
DynamicIslandExpandedRegion(.leading) {
    Text("Top")
        .dynamicIsland(verticalPlacement: .belowIfTooWide)
}
```

### Content Margins

Override margins for specific Dynamic Island modes:

```swift
.contentMargins(.trailing, 20, for: .expanded)
.contentMargins(.bottom, 16, for: .expanded)
```

### Keyline Tint

Apply a subtle tint to the Dynamic Island border:

```swift
DynamicIsland { /* ... */ }
    .keylineTint(.blue)
```

## Alert Configuration for Live Activities

Trigger a visible and audible alert when updating a Live Activity:

```swift
let alert = AlertConfiguration(
    title: "Delivery Update",
    body: "Your order is out for delivery!",
    sound: .default
)
await activity.update(updatedContent, alertConfiguration: alert)
```

### Custom Alert Sound

```swift
let alert = AlertConfiguration(
    title: "Score Update",
    body: "Goal! The score is now 2-1.",
    sound: .named("goal-horn.aiff")
)
```

Place the sound file in the app bundle. Use `.default` when no custom sound is needed.

## Push Notification Support for Live Activities

### Registering for Push Updates

```swift
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token  // Enable push updates
)

// Observe token changes
Task {
    for await token in activity.pushTokenUpdates {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        try await ServerAPI.shared.registerActivityToken(tokenString, activityID: activity.id)
    }
}
```

### Push-to-Start (Remote Activity Creation)

```swift
// Observe the push-to-start token
Task {
    for await token in Activity<DeliveryAttributes>.pushToStartTokenUpdates {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        try await ServerAPI.shared.registerPushToStartToken(tokenString)
    }
}
```

### Channel-Based ActivityKit Push (iOS 18+)

ActivityKit broadcast channels are for Live Activity updates, not WidgetKit
timeline push notifications. Pass a valid base64-encoded channel ID that your
server created through APNs channel management.

```swift
let channelID = "ZGVsaXZlcnktdXBkYXRlcw=="
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .channel(channelID)
)
```

### APNs Payload Format for Live Activity Updates

```json
{
    "aps": {
        "timestamp": 1234567890,
        "event": "update",
        "content-state": {
            "driverName": "Alex",
            "estimatedDeliveryTime": {
                "lowerBound": 1234567890,
                "upperBound": 1234568790
            },
            "currentStep": "delivering"
        },
        "alert": {
            "title": "Delivery Update",
            "body": "Your driver is nearby!"
        }
    }
}
```

The `content-state` must match the `ContentState` Codable structure exactly.

### Info.plist Keys

| Key | Value | Purpose |
|---|---|---|
| `NSSupportsLiveActivities` | `YES` | Enable Live Activities |
| `NSSupportsLiveActivitiesFrequentUpdates` | `YES` | Enable frequent push updates (budget increase) |

## ActivityAuthorizationInfo

Check whether Live Activities are permitted before attempting to start one.

```swift
let authInfo = ActivityAuthorizationInfo()

// Check permission synchronously
if authInfo.areActivitiesEnabled {
    try Activity.request(attributes: attributes, content: content, pushType: .token)
}

// Observe permission changes
Task {
    for await enabled in authInfo.activityEnablementUpdates {
        if enabled {
            // Activities became available
        }
    }
}

// Check frequent push support
if authInfo.frequentPushesEnabled {
    // Safe to use frequent push updates
}
```

### Error Handling

```swift
do {
    let activity = try Activity.request(attributes: attributes, content: content, pushType: .token)
} catch let error as ActivityAuthorizationError {
    switch error {
    case .denied:
        // User disabled Live Activities in Settings
        break
    case .globalMaximumExceeded:
        // Too many Live Activities across all apps
        break
    case .targetMaximumExceeded:
        // Too many Live Activities for this app
        break
    default:
        break
    }
}
```
