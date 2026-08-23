---
name: push-notifications
description: "Implement or debug local and APNs notifications, permissions, payloads, categories, actions, silent pushes, and notification extensions. Use for alerts, badges, sounds, background delivery, rich content, registration, or delivery diagnosis; route Live Activity updates to activitykit."
---

# Push Notifications

Implement, review, and debug local and remote notifications with `UserNotifications` and APNs. Target the project's deployment range; examples assume modern Swift concurrency and note availability when using newer APIs.

Keep adjacent domains separate: Live Activity `content-state` pushes belong to `activitykit`; PushKit/VoIP calls to `callkit`; App Clip ephemeral setup to `app-clips`; long-running or scheduled background work to `background-processing`.

## Contents

- [Route by task](#route-by-task)
- [Core workflow](#core-workflow)
- [Authorization and APNs registration](#authorization-and-apns-registration)
- [Payload and delivery contracts](#payload-and-delivery-contracts)
- [Runtime handling and routing](#runtime-handling-and-routing)
- [Categories and actions](#categories-and-actions)
- [Correction reviews](#correction-reviews)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)

## Route by task

Read only the references needed for the request:

- For notification authorization, APNs registration, token lifecycle, provider headers, visible/background payloads, or delivery diagnosis, read [APNs lifecycle and remote delivery](references/apns-lifecycle.md).
- For time, calendar, or location reminders scheduled on-device, read [local notifications](references/local-notifications.md).
- For complete application-delegate wiring, foreground/tap handling, deep-link routing, and categories, read [notification runtime and routing](references/notification-runtime.md).
- For `.apns`, `simctl`, APNs Sandbox Simulator coverage, provider/device matrices, or delivery diagnosis, read [notification delivery testing](references/notification-testing.md).
- For service-extension mutation and exactly-once completion, read [service extensions](references/service-extension.md).
- For custom expanded UI, read [content extensions](references/content-extension.md); for Messages-style presentation, read [communication notifications](references/communication-notifications.md).
- For the focused reference index, read [notification patterns](references/notification-patterns.md) or [rich notifications](references/rich-notifications.md). Use [complete notification patterns](references/notification-patterns-complete.md) and [complete rich-notification recipes](references/rich-notifications-complete.md) only for broad end-to-end examples or migration.

Do not read every reference for a narrow task. Keep the response scoped to the failed or requested delivery path.

## Core workflow

1. Classify the notification as local, visible remote, background remote, Live Activity, VoIP, or extension-modified.
2. Inspect entitlements, capabilities, bundle/topic, delegate installation, categories, provider ownership, and target platform.
3. Separate visible authorization from APNs registration and server token binding.
4. Define payload keys, APNs headers, expiry/collapse behavior, and sensitive-data policy.
5. Implement foreground presentation, response/action routing, and bounded background or extension work.
6. Verify each boundary independently: scheduling/provider acceptance, device receipt, extension execution, presentation, and response routing.

## Authorization and APNs registration

Notification authorization controls user-visible alerts, sounds, and badges. Request it in context and check `notificationSettings()` because the user can change settings later.

APNs registration is a separate path. Call `registerForRemoteNotifications()` whenever a device token is needed, including server binding or background delivery. Do not gate it on `.authorized`.

Receive tokens through application-delegate callbacks. Treat token data as opaque, convert it to hex for transport, and upload on every successful callback. Do not assume a fixed length or treat a locally cached token as provider truth.

```swift
func application(
    _ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
) {
    let token = deviceToken.map { String(format: "%02x", $0) }.joined()
    Task { await tokenService.upload(token) }
}
```

On supported current Xcode/OS hosts, iOS Simulator can register with the APNs Sandbox and receives a simulator-specific, variable-length token. Provider delivery to that Simulator is useful for sandbox end-to-end checks. `.apns` files and `simctl push` simulate delivery without exercising the provider path; host/CI support varies. Verify production entitlements, signing, and hardware-specific behavior on a physical device.

## Payload and delivery contracts

| Path | Required contract | Key limitation |
|---|---|---|
| Visible remote | `aps.alert`, `apns-push-type: alert` | Presentation depends on authorization, app state, Focus, and delegate policy |
| Background remote | `content-available: 1` only in `aps`, push type `background`, priority `5` | Low priority, throttled, coalesced, and not guaranteed |
| Service extension | Alert payload plus `mutable-content: 1` | Silent-only, sound-only, or badge-only pushes don't launch it |
| Local | `UNNotificationRequest` with time/calendar/location trigger | Device scheduling and current authorization determine presentation |

Put Apple keys inside `aps` and minimal app routing identifiers beside it. Treat payload data as untrusted: validate identity/authorization against current app or server state before navigation or mutation. Avoid sensitive plaintext.

Background pushes are hints to fetch current state, not a timer. Enable Background Modes > Remote notifications, perform bounded work, and return the correct `UIBackgroundFetchResult`. Route `BGTaskScheduler` design to `background-processing`.

## Runtime handling and routing

Set `UNUserNotificationCenter.current().delegate` during launch, before responses can arrive.

```swift
@MainActor
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        [.banner, .list, .sound, .badge]
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        await notificationRouter.handle(response)
    }
}
```

Keep payload parsing in a testable boundary. Hand a validated destination or intent to the app's existing navigation/state owner; notification delegates should not create a competing navigation architecture.

Foreground receipt does not automatically show UI. Return only the presentation options the product wants. Handle body taps, dismiss callbacks when registered, and custom action identifiers deliberately.

## Categories and actions

Register categories during launch. Payload `category` and local `categoryIdentifier` values must exactly match the registered identifier.

Choose action options from behavior:

- `.foreground` launches the app for UI work;
- `.authenticationRequired` protects sensitive actions until unlock;
- `.destructive` communicates irreversible intent;
- `UNTextInputNotificationAction` supports inline text response.

Validate identifiers in `userInfo` again before calling services. Define idempotency for actions the system or user may invoke more than once.

## Correction reviews

For flawed designs, name the violated contract rather than only showing replacement code:

- Registration gated by alert permission: separate authorization and token registration.
- Token cached to skip provider upload: upload on every callback and let the provider reconcile.
- Frequent priority-10 silent pushes: use background payload/headers and state that delivery is throttled and not guaranteed.
- Service extension triggered by silent push: require alert content plus `mutable-content: 1`.
- Extension secrets in App Group defaults: use Keychain Sharing for secrets; App Groups for shared files/defaults.
- Attachment from arbitrary remote URL: download a supported file to disk, then construct `UNNotificationAttachment`.
- Extension missing fallback: call the content handler exactly once on success, failure, and `serviceExtensionTimeWillExpire()`.

## Common mistakes

- Setting the center delegate after launch or inside a transient SwiftUI view.
- Treating a missing banner as proof that APNs didn't deliver.
- Assuming background delivery is immediate or periodic.
- Converting device token data as UTF-8 or assuming token length.
- Doing unbounded network work in a background callback or extension.
- Putting authorization state, secrets, or trusted navigation decisions in payload data.
- Using `removeAll…` for a feature that doesn't own every app notification.
- Mixing Live Activity, VoIP, and ordinary alert payload rules.

## Review checklist

- [ ] Notification path and sibling-skill boundary are explicit.
- [ ] Visible authorization is requested in context and current settings are respected.
- [ ] APNs registration is not incorrectly gated by visible authorization.
- [ ] Token is treated as opaque and uploaded on every registration callback.
- [ ] Provider push type, priority, topic, expiration, and payload match the path.
- [ ] Delegate and categories are installed during launch.
- [ ] Foreground presentation, taps, dismissals, and custom actions follow product policy.
- [ ] Background or extension work is bounded and completes through every path.
- [ ] Payload identifiers are validated before navigation or mutation.
- [ ] Local requests have stable ownership, update, and cancellation semantics.
- [ ] Simulator limitations and physical-device verification are distinguished.
- [ ] Delivery evidence covers the actual provider/device/app boundary that changed.

## Official references

- [UserNotifications](https://sosumi.ai/documentation/usernotifications)
- [Registering your app with APNs](https://sosumi.ai/documentation/usernotifications/registering-your-app-with-apns)
- [Generating a remote notification](https://sosumi.ai/documentation/usernotifications/generating-a-remote-notification)
- [UNUserNotificationCenterDelegate](https://sosumi.ai/documentation/usernotifications/unusernotificationcenterdelegate)
