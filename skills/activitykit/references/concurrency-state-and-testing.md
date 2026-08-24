# ActivityKit Concurrency, State, and Testing

Read this reference only when the task matches the sections below.

## Multiple Concurrent Activities

An app can run multiple Live Activities simultaneously (system limit applies).
Track them by storing references or querying `Activity<T>.activities`.

```swift
@Observable
@MainActor
final class ActivityManager {
    private(set) var activeDeliveries: [String: Activity<DeliveryAttributes>] = [:]

    func startDelivery(orderID: String, attributes: DeliveryAttributes,
                       state: DeliveryAttributes.ContentState) async throws {
        let content = ActivityContent(state: state, staleDate: nil, relevanceScore: 75)
        let activity = try Activity.request(
            attributes: attributes, content: content, pushType: .token
        )
        activeDeliveries[orderID] = activity

        // Token forwarding
        Task { [weak self] in
            for await token in activity.pushTokenUpdates {
                let tokenString = token.map { String(format: "%02x", $0) }.joined()
                try? await ServerAPI.shared.registerActivityToken(tokenString, orderID: orderID)
            }
            self?.activeDeliveries.removeValue(forKey: orderID)
        }
    }

    func updateDelivery(orderID: String, state: DeliveryAttributes.ContentState) async {
        guard let activity = activeDeliveries[orderID] else { return }
        let content = ActivityContent(state: state, staleDate: nil, relevanceScore: 80)
        await activity.update(content)
    }

    func endDelivery(orderID: String, finalState: DeliveryAttributes.ContentState) async {
        guard let activity = activeDeliveries[orderID] else { return }
        let content = ActivityContent(state: finalState, staleDate: nil, relevanceScore: 0)
        await activity.end(content, dismissalPolicy: .default)
        activeDeliveries.removeValue(forKey: orderID)
    }

    /// Reconcile in-memory state with system activities on app launch
    func reconcile() {
        let systemActivities = Activity<DeliveryAttributes>.activities
        for activity in systemActivities {
            let orderID = "\(activity.attributes.orderNumber)"
            if activeDeliveries[orderID] == nil {
                activeDeliveries[orderID] = activity
            }
        }
    }
}
```

## Observing Activity State Changes

```swift
func observeActivityState(_ activity: Activity<RideAttributes>) {
    // State updates: .active, .pending, .stale, .ended, .dismissed
    Task {
        for await state in activity.activityStateUpdates {
            switch state {
            case .active:
                print("Activity is visible and running")
            case .pending:
                // iOS 26+: scheduled but not yet displayed
                print("Activity is pending start")
            case .stale:
                // iOS 16.2+: staleDate passed without an update
                print("Content is stale -- update or end")
            case .ended:
                // Ended but may still be visible on Lock Screen
                print("Activity ended, may still linger on Lock Screen")
            case .dismissed:
                // Fully removed from UI -- safe to release resources
                print("Activity dismissed from Lock Screen")
                cleanupResources(for: activity.id)
            @unknown default:
                break
            }
        }
    }

    // Content updates (observe state changes from push or other processes)
    Task {
        for await content in activity.contentUpdates {
            print("New state: \(content.state)")
        }
    }
}
```

## Token Update Handling

Push tokens can change at any time. Always observe the async sequence and
re-register with your server.

```swift
func observePushToken(for activity: Activity<RideAttributes>) {
    Task {
        for await token in activity.pushTokenUpdates {
            let tokenString = token.map { String(format: "%02x", $0) }.joined()
            do {
                try await ServerAPI.shared.registerActivityToken(
                    tokenString, activityID: activity.id
                )
            } catch {
                // Retry with exponential backoff; token is critical for updates
                print("Failed to register token: \(error)")
            }
        }
    }
}

/// Observe the ActivityKit push-to-start token for remote activity creation (iOS 17.2+).
/// This token is distinct from ordinary app/device APNs tokens and per-activity update tokens.
func observePushToStartToken() {
    Task {
        for await token in Activity<RideAttributes>.pushToStartTokenUpdates {
            let tokenString = token.map { String(format: "%02x", $0) }.joined()
            try? await ServerAPI.shared.registerPushToStartToken(tokenString)
        }
    }
}
```

## Authorization Check

Always check authorization before starting an activity. The user can disable
Live Activities in Settings at any time.

```swift
func checkLiveActivityAuthorization() async -> Bool {
    let authInfo = ActivityAuthorizationInfo()
    return authInfo.areActivitiesEnabled
}

func checkFrequentPushAuthorization() -> Bool {
    ActivityAuthorizationInfo().frequentPushesEnabled
}

/// Observe authorization changes to react when user toggles the setting
func observeAuthorization() {
    Task {
        let authInfo = ActivityAuthorizationInfo()
        for await enabled in authInfo.activityEnablementUpdates {
            if enabled {
                observePushToStartToken()
            } else {
                try? await ServerAPI.shared.disableActivityPush()
            }
        }
    }

    Task {
        let authInfo = ActivityAuthorizationInfo()
        for await frequentPushesEnabled in authInfo.frequentPushEnablementUpdates {
            try? await ServerAPI.shared.setFrequentPushesEnabled(frequentPushesEnabled)
        }
    }
}
```

## Error Handling

```swift
func startActivitySafely(
    attributes: DeliveryAttributes,
    state: DeliveryAttributes.ContentState
) async {
    let content = ActivityContent(state: state, staleDate: nil, relevanceScore: 75)

    do {
        let activity = try Activity.request(
            attributes: attributes, content: content, pushType: .token
        )
        print("Started: \(activity.id)")
    } catch let error as ActivityAuthorizationError {
        switch error {
        case .denied:
            // User disabled Live Activities in Settings
            print("Live Activities disabled by user")
        case .globalMaximumExceeded:
            // Device-level ongoing Live Activity maximum reached
            print("System-wide activity limit reached")
        case .targetMaximumExceeded:
            // Too many Live Activities for this app
            print("App activity limit reached -- end an existing one first")
        default:
            print("Authorization error: \(error)")
        }
    } catch {
        print("Unexpected error: \(error)")
    }
}
```

## Background Handling Considerations

Live Activities continue to display when the app is backgrounded or suspended.
The Live Activity UI runs in a widget extension sandbox and cannot fetch network
data or receive location updates directly. Push-to-update is the primary
mechanism for background updates. When the app returns to foreground, reconcile
local state with the activity's current content.

```swift
@MainActor
func handleAppBecameActive() {
    // Reconcile local state with live activities on foregrounding
    let activities = Activity<DeliveryAttributes>.activities
    for activity in activities {
        switch activity.activityState {
        case .active:
            // Refresh from server in case pushes were missed
            Task {
                let serverState = try await ServerAPI.shared.fetchDeliveryState(
                    orderNumber: activity.attributes.orderNumber
                )
                let content = ActivityContent(
                    state: serverState,
                    staleDate: Date().addingTimeInterval(120),
                    relevanceScore: 80
                )
                await activity.update(content)
            }
        case .stale:
            // Content is outdated -- update immediately
            Task {
                let serverState = try await ServerAPI.shared.fetchDeliveryState(
                    orderNumber: activity.attributes.orderNumber
                )
                let content = ActivityContent(
                    state: serverState,
                    staleDate: Date().addingTimeInterval(120),
                    relevanceScore: 80
                )
                await activity.update(content)
            }
        case .ended, .dismissed:
            // Clean up local tracking
            break
        default:
            break
        }
    }
}
```

For truly background-driven updates, rely on push-to-update rather than
Background App Refresh. Push updates can arrive while the app is suspended, but
APNs delivery, priority, budget, and throttling still apply; use `staleDate` and
foreground reconciliation for missed updates.

## Testing in Simulator and on Device

### Simulator

The Simulator supports Live Activity rendering on the Lock Screen and displays
the Dynamic Island on simulator models that include Dynamic Island. Use Xcode
previews for rapid iteration:

```swift
#Preview("Lock Screen", as: .content, using: RideAttributes.preview) {
    RideActivityWidget()
} contentStates: {
    RideAttributes.ContentState(
        driverName: "Alex",
        driverPhoto: "car.fill",
        vehicleDescription: "White Toyota Camry",
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(300).timeIntervalSince1970),
        status: .driverEnRoute,
        distanceRemaining: 1.5
    )
    RideAttributes.ContentState(
        driverName: "Alex",
        driverPhoto: "car.fill",
        vehicleDescription: "White Toyota Camry",
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(60).timeIntervalSince1970),
        status: .arriving,
        distanceRemaining: 0.1
    )
}

#Preview("Dynamic Island Compact", as: .dynamicIsland(.compact), using: RideAttributes.preview) {
    RideActivityWidget()
} contentStates: {
    RideAttributes.ContentState(
        driverName: "Alex",
        driverPhoto: "car.fill",
        vehicleDescription: "White Toyota Camry",
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(300).timeIntervalSince1970),
        status: .driverEnRoute,
        distanceRemaining: 1.5
    )
}

#Preview("Dynamic Island Expanded", as: .dynamicIsland(.expanded), using: RideAttributes.preview) {
    RideActivityWidget()
} contentStates: {
    RideAttributes.ContentState(
        driverName: "Alex",
        driverPhoto: "car.fill",
        vehicleDescription: "White Toyota Camry",
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(300).timeIntervalSince1970),
        status: .driverEnRoute,
        distanceRemaining: 1.5
    )
}

#Preview("Dynamic Island Minimal", as: .dynamicIsland(.minimal), using: RideAttributes.preview) {
    RideActivityWidget()
} contentStates: {
    RideAttributes.ContentState(
        driverName: "Alex",
        driverPhoto: "car.fill",
        vehicleDescription: "White Toyota Camry",
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(300).timeIntervalSince1970),
        status: .driverEnRoute,
        distanceRemaining: 1.5
    )
}
```

### Preview Data Helper

```swift
extension RideAttributes {
    static var preview: RideAttributes {
        RideAttributes(
            riderName: "Jordan",
            pickupLocation: "123 Main St",
            dropoffLocation: "456 Oak Ave"
        )
    }
}
```

### On Device

Test push-to-update by sending payloads through APNs using a tool like `curl`
or a push notification testing app. The Simulator does not support APNs, so
push-to-update must be tested on a physical device.

```bash
# Example curl command for APNs push update (HTTP/2)
curl -v \
  --http2 \
  --header "apns-push-type: liveactivity" \
  --header "apns-topic: com.example.app.push-type.liveactivity" \
  --header "apns-priority: 10" \
  --header "authorization: bearer $JWT_TOKEN" \
  --data '{"aps":{"timestamp":1700000000,"event":"update","content-state":{"driverName":"Alex","driverPhoto":"car.fill","vehicleDescription":"White Toyota Camry","etaStartSeconds":1700000000,"etaEndSeconds":1700000300,"status":"driverArrived","distanceRemaining":0.0},"alert":{"title":"Driver Arrived","body":"Your driver is here!"}}}' \
  https://api.push.apple.com/3/device/$DEVICE_PUSH_TOKEN
```

### Debugging Tips

- Check Console.app for `ActivityKit` log messages when activities fail to start.
- Verify `content-state` JSON keys match the default `ContentState` `Codable`
  shape or coordinated `CodingKeys`. Mismatches can prevent ActivityKit from
  applying updates.
- Use `Activity<T>.activities` to inspect all running activities in the debugger.
- Set a breakpoint in `pushTokenUpdates` to verify tokens are being delivered.
- If activities do not appear, confirm `NSSupportsLiveActivities = YES` is in
  the host app's Info.plist (not the widget extension's).

## Info.plist Keys Reference

| Key | Value | Purpose |
|---|---|---|
| `NSSupportsLiveActivities` | `YES` | Enable Live Activities (required) |
| `NSSupportsLiveActivitiesFrequentUpdates` | `YES` | Increase the system-managed push update budget |

Both keys belong in the host app's Info.plist, not the widget extension.

## Apple Documentation Links

- [ActivityKit](https://sosumi.ai/documentation/activitykit)
- [ActivityAttributes](https://sosumi.ai/documentation/activitykit/activityattributes)
- [Activity](https://sosumi.ai/documentation/activitykit/activity)
- [ActivityContent](https://sosumi.ai/documentation/activitykit/activitycontent)
- [ActivityAuthorizationInfo](https://sosumi.ai/documentation/activitykit/activityauthorizationinfo)
- [DynamicIsland](https://sosumi.ai/documentation/widgetkit/dynamicisland)
- [ActivityConfiguration](https://sosumi.ai/documentation/widgetkit/activityconfiguration)
- [Starting and updating with push notifications](https://sosumi.ai/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Sending broadcast push notifications](https://sosumi.ai/documentation/usernotifications/sending-broadcast-push-notification-requests-to-apns)
