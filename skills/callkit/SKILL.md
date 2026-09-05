---
name: callkit
description: "Implement VoIP calling with CallKit and PushKit. Use when building incoming/outgoing call flows, registering for VoIP push notifications, configuring CXProvider and CXCallController, handling call actions, coordinating audio sessions, or creating Call Directory extensions for caller ID and call blocking."
---

# CallKit

Build VoIP calling experiences that integrate with the native iOS call UI using CallKit and PushKit. Covers incoming and outgoing call flows, PushKit VoIP registration, audio session coordination, and call directory extensions. Targets Swift 6.3 / iOS 26+.

## Contents

- [Capabilities and Key Types](#capabilities-and-key-types)
- [Core Calling Architecture](#core-calling-architecture)
- [Critical VoIP Push Rule](#critical-voip-push-rule)
- [Audio Session Lifecycle](#audio-session-lifecycle)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Capabilities and Key Types

Enable **Voice over IP** in Signing & Capabilities > Background Modes, and add the **Push Notifications** capability.

| Type | Role |
|---|---|
| `CXProvider` | Reports incoming calls, connections, and external resets to the system; receives `CXAction` requests |
| `CXCallController` | Requests user-initiated call actions (`CXStartCallAction`, `CXEndCallAction`, `CXSetHeldCallAction`) |
| `CXCallUpdate` | Encapsulates call metadata (remote handle, caller name, video capability) |
| `CXProviderDelegate` | Handles telephony events, user interactions (answer, end, hold, mute), and audio session activation |
| `PKPushRegistry` | Registers for and receives PushKit VoIP push notifications |

## Core Calling Architecture

```
[PushKit VoIP Push] ──> [reportNewIncomingCall] ──> [System Call UI]
                                                            │ (user answers)
                                                            ▼
[WebRTC / VoIP Stack] <── [configureAudioSession] <── [CXAnswerCallAction]
```

1. **Maintain single CXProvider**: Keep one retained `CXProvider` instance alive across the app lifecycle. Recreating providers disconnects active calls.
2. **Handle CXProviderDelegate on serial queue**: Dispatch delegate callbacks to a dedicated queue or `@MainActor` to prevent race conditions during call state transitions.
3. **Fulfill or fail every action**: Call `action.fulfill()` or `action.fail()` promptly inside delegate methods. Unfulfilled actions cause UI timeouts.

## Critical VoIP Push Rule

Every VoIP push received via `pushRegistry(_:didReceiveIncomingPushWith:for:)` **must** immediately report an incoming call to CallKit via `reportNewIncomingCall(with:update:completion:)`.

> [!WARNING]
> Failing to report a new incoming call upon receiving a VoIP push causes iOS to terminate the app and revoke future VoIP push credentials. On iOS 26.4+, inspect `PKVoIPPushMetadata` to check if a push is exempt from reporting.

## Audio Session Lifecycle

Do not activate the `AVAudioSession` during call initialization. Only configure categories in advance (`.playAndRecord` with `.voiceChat` mode). Activate the audio session **only** when the system invokes `provider(_:didActivate:)`. Deactivate audio in `provider(_:didDeactivate:)`.

## Route by Task

- For a complete, observable VoIP call manager with incoming and outgoing flows, read [Full Call Manager](references/callkit-patterns.md#full-call-manager).
- For handling hold, mute, and multiple concurrent calls, read [Hold and Mute Actions](references/callkit-patterns.md#hold-and-mute-actions) and [Multiple Concurrent Calls](references/callkit-patterns.md#multiple-concurrent-calls).
- For encrypted VoIP push payloads and payload filtering, read [Encrypted VoIP Push Filtering](references/callkit-patterns.md#encrypted-voip-push-filtering).
- For building Call Directory extensions (Caller ID and call blocking with incremental phone updates), read [Call Directory Incremental Updates](references/callkit-patterns.md#call-directory-incremental-updates).
- For local debugging with terminal scripts and simulated push payloads, read [Testing VoIP Locally](references/callkit-patterns.md#testing-voip-locally).

## Common Mistakes

- Receiving a VoIP push without calling `reportNewIncomingCall`, causing iOS to terminate the app.
- Activating `AVAudioSession` before the system calls `provider(_:didActivate:)`.
- Forgetting to call `action.fulfill()` in `CXProviderDelegate` action handlers.
- Recreating `CXProvider` instances instead of keeping a single shared instance for the app lifecycle.
- Using standard APNs alerts for VoIP incoming calls instead of PushKit.

## Review Checklist

- [ ] Voice over IP background mode and Push Notifications capabilities enabled
- [ ] Single retained `CXProvider` shared across the application lifetime
- [ ] Every VoIP push immediately reports an incoming call via `reportNewIncomingCall`
- [ ] `AVAudioSession` activated exclusively inside `provider(_:didActivate:)`
- [ ] All `CXAction` delegate callbacks call `fulfill()` or `fail()` promptly
- [ ] App cleanly cleans up calls when `providerDidReset(_:)` is triggered
- [ ] Handle types (`.phoneNumber`, `.emailAddress`, `.generic`) match backend identifiers
- [ ] Outgoing calls reported with `reportOutgoingCall(with:startedConnectingAt:)` and `connectedAt:`
- [ ] Call Directory extension handles incremental reload without re-inserting unchanged numbers

## References

- [CallKit extended patterns and Call Directory guide](references/callkit-patterns.md)
- [CallKit documentation](https://sosumi.ai/documentation/callkit)
- [CXProvider](https://sosumi.ai/documentation/callkit/cxprovider)
- [CXCallController](https://sosumi.ai/documentation/callkit/cxcallcontroller)
- [PushKit documentation](https://sosumi.ai/documentation/pushkit)
