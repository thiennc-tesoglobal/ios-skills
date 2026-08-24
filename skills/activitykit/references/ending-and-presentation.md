# ActivityKit Ending and Presentation

Read this reference only when the task matches the sections below.

## Ending with Different Dismissal Policies

```swift
func endRideActivity(
    _ activity: Activity<RideAttributes>,
    finalStatus: RideStatus
) async {
    let finalState = RideAttributes.ContentState(
        driverName: activity.content.state.driverName,
        driverPhoto: activity.content.state.driverPhoto,
        vehicleDescription: activity.content.state.vehicleDescription,
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().timeIntervalSince1970),
        status: finalStatus,
        distanceRemaining: 0
    )

    let content = ActivityContent(state: finalState, staleDate: nil, relevanceScore: 0)

    switch finalStatus {
    case .completed:
        // Keep on Lock Screen for 1 hour so user can review trip details
        await activity.end(content, dismissalPolicy: .after(
            Date().addingTimeInterval(3600)
        ))
    case .cancelled:
        // Remove immediately -- no useful info to show
        await activity.end(content, dismissalPolicy: .immediate)
    default:
        // Let the system decide
        await activity.end(content, dismissalPolicy: .default)
    }
}
```

When reviewing duration claims, distinguish the active lifetime (up to 8 hours
unless the app or user ends it sooner), system-ended Lock Screen presence (up to
4 additional hours, for 12 hours total from start), and app-ended `.default`
dismissal linger (up to 4 hours after ending).

### Ending on Terminal Server Failure

When a server reports that the tracked event failed or can no longer be
represented accurately, publish a terminal state and end the activity instead of
leaving stale progress visible.

```swift
func handleTerminalServerFailure(
    _ activity: Activity<RideAttributes>,
    message: String
) async {
    let failedState = RideAttributes.ContentState(
        driverName: activity.content.state.driverName,
        driverPhoto: activity.content.state.driverPhoto,
        vehicleDescription: message,
        etaStartSeconds: Int(Date().timeIntervalSince1970),
        etaEndSeconds: Int(Date().timeIntervalSince1970),
        status: .failed,
        distanceRemaining: 0
    )

    let content = ActivityContent(state: failedState, staleDate: nil, relevanceScore: 0)
    await activity.end(content, dismissalPolicy: .immediate)
}
```

### Ending All Activities (cleanup on sign-out)

```swift
func endAllRideActivities() async {
    for activity in Activity<RideAttributes>.activities {
        await activity.end(nil, dismissalPolicy: .immediate)
    }
}
```

## Complete Dynamic Island Layout (All Regions)

```swift
struct RideActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: RideAttributes.self) { context in
            // Lock Screen presentation
            RideLockScreenView(context: context)
        } dynamicIsland: { context in
            DynamicIsland {
                // EXPANDED: shown on long-press
                DynamicIslandExpandedRegion(.leading) {
                    VStack(alignment: .leading) {
                        Image(systemName: context.state.driverPhoto)
                            .font(.title2)
                        Text(context.state.driverName)
                            .font(.caption2)
                            .lineLimit(1)
                    }
                }

                DynamicIslandExpandedRegion(.trailing) {
                    VStack(alignment: .trailing) {
                        Text(timerInterval: context.state.etaRange, countsDown: true)
                            .font(.title3.monospacedDigit())
                        Text(String(format: "%.1f mi", context.state.distanceRemaining))
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }

                DynamicIslandExpandedRegion(.center) {
                    Text(context.state.status.displayName)
                        .font(.headline)
                        .lineLimit(1)
                }

                DynamicIslandExpandedRegion(.bottom) {
                    VStack {
                        ProgressView(
                            value: context.state.status.progress,
                            total: 1.0
                        )
                        .tint(.green)

                        HStack {
                            Label(context.attributes.pickupLocation,
                                  systemImage: "mappin.circle.fill")
                            Spacer()
                            Label(context.attributes.dropoffLocation,
                                  systemImage: "flag.checkered")
                        }
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                    }
                }
            } compactLeading: {
                // COMPACT LEADING: tiny icon identifying the activity
                Image(systemName: context.state.driverPhoto)
                    .foregroundStyle(.green)
            } compactTrailing: {
                // COMPACT TRAILING: one key value
                Text(timerInterval: context.state.etaRange, countsDown: true)
                    .frame(width: 44)
                    .monospacedDigit()
            } minimal: {
                // MINIMAL: shown when multiple activities compete
                Image(systemName: "car.fill")
                    .foregroundStyle(.green)
            }
            .keylineTint(.green)
        }
    }
}
```

## Lock Screen Layout with Timer and Progress

```swift
struct RideLockScreenView: View {
    let context: ActivityViewContext<RideAttributes>

    var body: some View {
        VStack {
            // Header
            HStack {
                VStack(alignment: .leading) {
                    Text(context.state.status.displayName)
                        .font(.headline)
                    Text(context.state.vehicleDescription)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                // Live countdown timer (auto-updating, no code needed)
                Text(timerInterval: context.state.etaRange, countsDown: true)
                    .font(.title2.monospacedDigit().bold())
                    .foregroundStyle(.green)
            }

            if context.isStale {
                Label("Checking for updates...",
                      systemImage: "arrow.trianglehead.2.clockwise")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            // Progress bar
            ProgressView(value: context.state.status.progress, total: 1.0)
                .tint(.green)

            // Route
            HStack {
                VStack(alignment: .leading) {
                    Text("Pickup").font(.caption2).foregroundStyle(.secondary)
                    Text(context.attributes.pickupLocation).font(.caption).lineLimit(1)
                }
                Spacer()
                Image(systemName: "arrow.right")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                VStack(alignment: .trailing) {
                    Text("Dropoff").font(.caption2).foregroundStyle(.secondary)
                    Text(context.attributes.dropoffLocation).font(.caption).lineLimit(1)
                }
            }
        }
        .padding()
    }
}
```
