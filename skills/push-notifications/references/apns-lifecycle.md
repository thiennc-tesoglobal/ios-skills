# APNs Lifecycle and Remote Delivery

Use this reference for permission strategy, APNs registration, device tokens, provider payloads, background notifications, and delivery diagnosis. Rich notification extensions are covered separately in `rich-notifications.md`.

## Contents

- Authorization and notification settings
- APNs registration and device tokens
- Provider request contracts
- Background notifications
- Runtime delivery handling
- Delivery diagnosis

## Authorization and notification settings

`UNUserNotificationCenter` authorization controls user-visible interactions such as alerts, sounds, and badges. It is separate from APNs device-token registration.

Request visible authorization in context, after the user understands the benefit. The system records the decision; repeated calls do not recreate the initial prompt. Query `notificationSettings()` because the user can change individual settings later.

```swift
let center = UNUserNotificationCenter.current()
let settings = await center.notificationSettings()

if settings.authorizationStatus == .notDetermined {
    _ = try await center.requestAuthorization(options: [.alert, .sound, .badge])
}
```

Provisional authorization is appropriate only when quiet trial delivery matches the product experience. Critical alerts require Apple's entitlement and a qualifying health, safety, or security use case. Do not present a Settings link as another permission prompt; use it only after denial when the user explicitly wants to change notification behavior.

## APNs registration and device tokens

Call `UIApplication.shared.registerForRemoteNotifications()` whenever the app needs an APNs token for provider binding or background delivery. Do not gate it on `.authorized`; visible-notification authorization and token registration are different contracts.

Receive registration callbacks through the application delegate, including in SwiftUI apps via `UIApplicationDelegateAdaptor`.

```swift
final class AppDelegate: NSObject, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02x", $0) }.joined()
        Task { await tokenService.upload(token) }
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        logger.error("APNs registration failed: \(error.localizedDescription)")
    }
}
```

Treat the token as opaque and variable-length. Upload it on every successful callback; APNs can change it. Do not persist a token locally as the provider's source of truth or skip upload because it matches a cached value. Associate tokens with the correct user/session on the provider and remove invalid tokens in response to APNs feedback.

Simulator can receive simulated `.apns` or `simctl push` payloads, but it doesn't provide normal APNs device-token registration. Confirm real registration and provider delivery on a physical device.

## Provider request contracts

Keep Apple-reserved keys inside `aps`; place product routing identifiers beside it. Validate and authorize custom identifiers again in the app before navigating or mutating data.

| Delivery | Required payload/headers | Important behavior |
|---|---|---|
| Visible alert | `aps.alert`; `apns-push-type: alert` | Authorization and Focus settings affect presentation |
| Background update | `aps` contains only `content-available: 1`; `apns-push-type: background`; `apns-priority: 5` | Low priority, throttled, and not guaranteed |
| Service extension | Alert payload plus `mutable-content: 1`; alert push type | Silent-only payloads don't launch the extension |

Use the correct `apns-topic` for the target bundle, an expiration appropriate to the content, and a stable collapse identifier only when replacing an older pending notification is intended. Inspect APNs HTTP status and reason values rather than treating every non-200 response as retryable. Authentication failures, bad topics, malformed payloads, and invalid tokens require different recovery.

Avoid sensitive plaintext in alert bodies and custom payload fields. APNs payloads are delivery envelopes, not trusted authorization state or durable storage.

### Visible payload

```json
{
  "aps": {
    "alert": {
      "title": "New message",
      "body": "Open the app to read it"
    },
    "sound": "default",
    "thread-id": "conversation-42",
    "category": "MESSAGE_CATEGORY"
  },
  "messageID": "42"
}
```

Use `title-loc-key`, `loc-key`, and `loc-args` when the device should localize the alert from app resources.

## Background notifications

Enable Background Modes > Remote notifications. The `aps` dictionary for a background notification contains `content-available: 1` without alert, sound, or badge keys.

```json
{
  "aps": { "content-available": 1 },
  "changeToken": "opaque-server-token"
}
```

The provider must use `apns-push-type: background` and priority `5`. Apple treats these pushes as low priority, may coalesce or throttle them, and doesn't guarantee delivery. Don't promise immediate refresh or schedule them every few minutes; use them as a hint to fetch current server state.

Perform bounded work and return the correct result promptly:

```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any]
) async -> UIBackgroundFetchResult {
    do {
        let changed = try await syncService.refresh(using: userInfo)
        return changed ? .newData : .noData
    } catch {
        return .failed
    }
}
```

Route scheduled or long-running work that needs `BGTaskScheduler` to `background-processing`. A push doesn't grant unlimited runtime.

## Runtime delivery handling

Set `UNUserNotificationCenter.current().delegate` during app launch, before a notification response can arrive. Implement:

- `willPresent` to decide foreground banner, list, sound, and badge behavior;
- `didReceive` to handle body taps, dismissals, and registered actions;
- a validated routing handoff so notification delegates don't own SwiftUI navigation state directly.

Register categories before relevant notifications arrive. Ensure payload `category` identifiers and app category/action identifiers match exactly.

## Delivery diagnosis

Work from the first failed boundary:

1. Confirm target capabilities, entitlements, provisioning, bundle/topic, environment, and physical-device token registration.
2. Confirm the provider has the current token for the active user and environment.
3. Inspect APNs response status, reason, request ID, topic, push type, priority, expiration, and payload size/shape.
4. Check device notification settings, Focus/Scheduled Summary behavior, app state, delegate installation, and category registration.
5. Test background delivery separately from visible presentation and service-extension execution.
6. Use Push Notifications Console, device logs, or a minimal provider request to isolate provider logic.

Do not diagnose a missing banner as proof that APNs delivery failed; foreground policy, authorization, Focus, summary, and extension failure are separate stages.

## Sources

- [Registering your app with APNs](https://sosumi.ai/documentation/usernotifications/registering-your-app-with-apns)
- [Requesting authorization](https://sosumi.ai/documentation/usernotifications/asking-permission-to-use-notifications)
- [Pushing background updates](https://sosumi.ai/documentation/usernotifications/pushing-background-updates-to-your-app)
- [Sending notification requests to APNs](https://sosumi.ai/documentation/usernotifications/sending-notification-requests-to-apns)
- [Troubleshooting push notifications](https://sosumi.ai/documentation/usernotifications/troubleshooting-push-notifications)
