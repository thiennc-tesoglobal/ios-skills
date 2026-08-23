# Notification Delivery Testing

Use this reference for Simulator, provider, device, and delivery diagnostics.
Test the boundary that changed instead of treating a banner as proof that every
layer is correct.

## Choose the test boundary

| Test | What it proves | What it does not prove |
|---|---|---|
| `.apns` file or `xcrun simctl push` | Payload parsing, app receipt, foreground/background handling, and local presentation in Simulator | Provider authentication, APNs routing, production entitlements, or hardware behavior |
| APNs Sandbox to a supported current iOS Simulator | Registration callback and sandbox provider delivery using a simulator-specific, variable-length token | Production APNs behavior, device-only capabilities, or every CI/VM host |
| APNs Sandbox to a physical device | Device registration, provider routing, signing, and hardware-relevant behavior | Production environment parity |
| APNs Production to a physical device | Release topic/entitlement/provider path | Local payload or extension logic in isolation |

Current Xcode/OS hosts may let iOS Simulator register with the APNs Sandbox.
Treat support as host/runtime-dependent, not as a universal Simulator promise.
Keep a physical-device check for production, signing, and hardware-specific
behavior. Simulator APNs tokens are not interchangeable with device tokens.

## Provider-free Simulator smoke test

Create a payload with the app's bundle identifier:

```json
{
  "Simulator Target Bundle": "com.example.myapp",
  "aps": {
    "alert": { "title": "Test", "body": "Provider-free smoke test" },
    "sound": "default"
  },
  "route": "inbox"
}
```

Then run:

```sh
xcrun simctl push booted com.example.myapp payload.apns
```

Use this path to isolate payload decoding, delegate behavior, categories, and
extension presentation. It does not exercise the APNs provider path.

## Provider and device matrix

For a remote test, record the environment, bundle/topic, push type, priority,
expiration, token source, APNs response, app callback, and final presentation.
Use `apns-push-type: alert` for visible notifications and
`apns-push-type: background` with priority `5` for background notifications.
Background pushes are hints: they can be delayed, coalesced, throttled, or
dropped, and they must not be used as a timer.

When a Simulator registration fails, inspect the Xcode/OS runtime, host
architecture, signing, network, CI/VM restrictions, and entitlements before
calling it an Apple-wide limitation. Re-register after reinstalling and log the
opaque token length and environment without treating a cached token as truth.

## Delivery debugging checklist

- Confirm the app's topic/bundle identifier and environment match the token.
- Capture APNs provider status and reason, not only the client log.
- Verify the application-delegate registration callback and upload each token.
- Inspect `aps` placement, push type, priority, expiration, and collapse ID.
- Check authorization, Focus, app state, notification settings, and category IDs.
- For extensions, verify the alert plus `mutable-content: 1` trigger and the
  exact-once completion path in [service-extension.md](service-extension.md).
- Repeat production or hardware-specific checks on a physical device.

For the original all-in-one recipes, read
[notification-patterns-complete.md](notification-patterns-complete.md#testing-notifications).
