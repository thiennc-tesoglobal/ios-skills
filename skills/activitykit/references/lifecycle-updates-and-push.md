# ActivityKit Lifecycle, Updates, and Push

Complete implementation patterns for ActivityKit Live Activities, Dynamic
Island, push-to-update, and lifecycle management. All patterns use modern
Swift async/await and `ActivityContent`, so they target iOS 16.2+ unless noted.

## Complete ActivityAttributes and ContentState

Define the data model for your Live Activity. Static properties go on the
outer struct; dynamic properties go in `ContentState`.

```swift
import ActivityKit

struct RideAttributes: ActivityAttributes {
    // Static -- set at creation, immutable for the activity lifetime
    var riderName: String
    var pickupLocation: String
    var dropoffLocation: String

    struct ContentState: Codable, Hashable {
        var driverName: String
        var driverPhoto: String        // SF Symbol name or asset name
        var vehicleDescription: String
        var etaStartSeconds: Int
        var etaEndSeconds: Int
        // For server pushes, prefer scalar fields or coordinated custom Codable keys.
        var status: RideStatus
        var distanceRemaining: Double   // miles
    }
}

enum RideStatus: String, Codable, Hashable {
    case driverAssigned
    case driverEnRoute
    case driverArrived
    case inProgress
    case arriving
    case completed
    case cancelled
    case failed
}

extension RideAttributes.ContentState {
    var etaRange: ClosedRange<Date> {
        Date(timeIntervalSince1970: TimeInterval(etaStartSeconds))...
            Date(timeIntervalSince1970: TimeInterval(etaEndSeconds))
    }
}
```

Keep `ContentState` lightweight. ActivityKit attributes and content-state data
must fit within the framework's 4 KB data limit. Avoid storing images, large
strings, or deeply nested objects.

## Starting a Live Activity with All Parameters

```swift
import ActivityKit

@MainActor
func startRideActivity(
    rider: String,
    pickup: String,
    dropoff: String,
    driver: String,
    vehicle: String
) async throws -> Activity<RideAttributes> {
    // Check authorization before attempting to start
    let authInfo = ActivityAuthorizationInfo()
    guard authInfo.areActivitiesEnabled else {
        throw RideError.liveActivitiesDisabled
    }

    let attributes = RideAttributes(
        riderName: rider,
        pickupLocation: pickup,
        dropoffLocation: dropoff
    )

    let initialState = RideAttributes.ContentState(
        driverName: driver,
        driverPhoto: "car.fill",
        vehicleDescription: vehicle,
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().addingTimeInterval(600).timeIntervalSince1970),
        status: .driverAssigned,
        distanceRemaining: 2.5
    )

    let content = ActivityContent(
        state: initialState,
        staleDate: Date().addingTimeInterval(120), // stale after 2 min
        relevanceScore: 80
    )

    let activity = try Activity.request(
        attributes: attributes,
        content: content,
        pushType: .token  // Enable push updates
    )

    // Forward push token to server for remote updates
    Task {
        for await token in activity.pushTokenUpdates {
            let tokenString = token.map { String(format: "%02x", $0) }.joined()
            try? await ServerAPI.shared.registerActivityToken(
                tokenString, rideID: activity.id
            )
        }
    }

    // Observe state changes for cleanup
    Task {
        for await state in activity.activityStateUpdates {
            if state == .dismissed {
                // Activity removed from UI -- clean up local resources
                RideStore.shared.removeActivity(id: activity.id)
            }
        }
    }

    return activity
}
```

### Starting with Scheduled Date (iOS 26+)

Schedule the activity to appear at a future time without the app in foreground:

```swift
let gameTime = Calendar.current.date(
    from: DateComponents(year: 2026, month: 3, day: 15, hour: 19, minute: 0)
)!

let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .standard,
    alertConfiguration: AlertConfiguration(
        title: "Game Starting",
        body: "The live score is ready.",
        sound: .default
    ),
    start: gameTime  // iOS 26+
)
```

### Starting with ActivityStyle (iOS 18+ request parameter)

Use `.standard` for persistent Live Activities that should remain visible until
the app, push, user, or system duration limit ends them. `.transient` is only
for short-lived expanded Dynamic Island presentations that can auto-end when the
user locks the device, collapses or shrinks the expanded presentation, leaves
the app, or does other work outside Dynamic Island; it is wrong for persistent
Live Activities.

```swift
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .standard
)
```

## Updating from the App

```swift
func updateRideActivity(
    _ activity: Activity<RideAttributes>,
    newStatus: RideStatus,
    eta: ClosedRange<Date>,
    distance: Double,
    showAlert: Bool = false
) async {
    let updatedState = RideAttributes.ContentState(
        driverName: activity.content.state.driverName,
        driverPhoto: activity.content.state.driverPhoto,
        vehicleDescription: activity.content.state.vehicleDescription,
        etaStartSeconds: Int(eta.lowerBound.timeIntervalSince1970),
        etaEndSeconds: Int(eta.upperBound.timeIntervalSince1970),
        status: newStatus,
        distanceRemaining: distance
    )

    let content = ActivityContent(
        state: updatedState,
        staleDate: Date().addingTimeInterval(120),
        relevanceScore: newStatus == .driverArrived ? 100 : 80
    )

    if showAlert {
        await activity.update(content, alertConfiguration: AlertConfiguration(
            title: "Ride Update",
            body: alertMessage(for: newStatus),
            sound: .default
        ))
    } else {
        await activity.update(content)
    }
}

private func alertMessage(for status: RideStatus) -> String {
    switch status {
    case .driverArrived: "Your driver has arrived!"
    case .arriving: "You're almost there!"
    case .completed: "You've arrived at your destination."
    default: "Your ride status has changed."
    }
}
```

## Push-to-Update Server Payload Format

### Update Payload

```json
{
    "aps": {
        "timestamp": 1700000000,
        "event": "update",
        "content-state": {
            "driverName": "Maria",
            "driverPhoto": "car.fill",
            "vehicleDescription": "White Toyota Camry",
            "etaStartSeconds": 1700000000,
            "etaEndSeconds": 1700000300,
            "status": "driverArrived",
            "distanceRemaining": 0.0
        },
        "stale-date": 1700000300,
        "relevance-score": 100,
        "alert": {
            "title": "Ride Update",
            "body": "Your driver has arrived!",
            "sound": "default"
        }
    }
}
```

### End Payload

```json
{
    "aps": {
        "timestamp": 1700002000,
        "event": "end",
        "dismissal-date": 1700005600,
        "content-state": {
            "driverName": "Maria",
            "driverPhoto": "car.fill",
            "vehicleDescription": "White Toyota Camry",
            "etaStartSeconds": 1700002000,
            "etaEndSeconds": 1700002000,
            "status": "completed",
            "distanceRemaining": 0.0
        }
    }
}
```

### Push-to-Start Payload (iOS 17.2+)

Send to the push-to-start token to remotely create an activity. The `alert` field is required for push-to-start:

```json
{
    "aps": {
        "timestamp": 1700000000,
        "event": "start",
        "attributes-type": "RideAttributes",
        "attributes": {
            "riderName": "Jordan",
            "pickupLocation": "123 Main St",
            "dropoffLocation": "456 Oak Ave"
        },
        "content-state": {
            "driverName": "Maria",
            "driverPhoto": "car.fill",
            "vehicleDescription": "White Toyota Camry",
            "etaStartSeconds": 1700000000,
            "etaEndSeconds": 1700000600,
            "status": "driverAssigned",
            "distanceRemaining": 3.2
        },
        "alert": {
            "title": "Ride Matched",
            "body": "Maria is on the way in a White Toyota Camry."
        }
    }
}
```

### Required APNs HTTP Headers

| Header | Value |
|---|---|
| `apns-push-type` | `liveactivity` |
| `apns-topic` | `<bundle-id>.push-type.liveactivity` |
| `apns-priority` | `5` (lower priority) or `10` (immediate, counts against budget) |
| `authorization` | `bearer <jwt>` (token auth) or use certificate auth |

The `aps.alert` payload controls visible alert/banner/sound behavior; priority
alone does not create an alert. The `content-state` JSON must decode into
`ActivityAttributes.ContentState`. Use the default synthesized `Codable` key and
value shape unless the Swift model declares custom `CodingKeys`; then coordinate
those exact keys and value shapes server-side. Do not assume `Date` or
`ClosedRange<Date>` values are Unix timestamp dictionaries unless your Swift
model explicitly encodes them that way. A type mismatch (e.g., sending a string
where a number is expected) can prevent ActivityKit from applying the update.

### Channel / Broadcast Updates (iOS 18+)

Use channel-based push only with a valid APNs-created channel ID. Enable the
broadcast capability outside Xcode, have the server create the channel, and pass
that channel ID to the app:

```swift
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .channel(channelIDFromServer)
)
```

Channel pushes can update or end Live Activities, but cannot start them. Use
`apns-channel-id` and expiration for channel requests instead of the device-token
`apns-topic` header.
