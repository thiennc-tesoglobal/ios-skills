---
name: permissionkit
description: "Create child communication safety experiences using PermissionKit to request parental permission for children. Use when building apps that involve child-to-contact communication, need to check communication limits, request parent/guardian approval, or handle permission responses for minors."
---

# PermissionKit

Create child communication safety experiences by requesting parental permission for communication exceptions. PermissionKit enables children to ask parents/guardians for approval when reaching communication limits.

> **Scope Boundary:** PermissionKit communication experiences are dispatched exclusively via iMessage. Use it strictly for parental exception approval flows, not as a general permission, chat, or content-moderation framework.

## Contents

- [Availability & Setup](#availability--setup)
- [Checking Communication Limits](#checking-communication-limits)
- [Creating Questions & Requesting Permission](#creating-questions--requesting-permission)
- [SwiftUI PermissionButton](#swiftui-permissionbutton)
- [Handling Responses](#handling-responses)
- [Significant App Updates](#significant-app-updates)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Availability & Setup

Import `PermissionKit`. Gate APIs according to the platform availability matrix:
- **Core (iOS 26.0+)**: Topics, handles, questions, responses, choices, `CommunicationLimits`.
- **Errors (iOS 26.1+)**: `AskError`.
- **UI & Presentation (iOS 26.2+)**: `AskCenter`, `PermissionButton`, `SignificantAppUpdateTopic`.

No custom entitlements are required; verify capabilities against official SDK documentation.

## Checking Communication Limits

Check whether a target handle is already authorized before initiating permission prompts. Guard against empty bundle identifiers:

```swift
import PermissionKit

func requiresParentalApproval(for handle: CommunicationHandle) async -> Bool {
    guard Bundle.main.bundleIdentifier?.isEmpty == false else { return false }
    let limits = CommunicationLimits.current
    let isKnown = await limits.isKnownHandle(handle)
    return !isKnown
}
```

If communication limits are not enabled on the device, `AskCenter.shared.ask(...)` throws `AskError.communicationLimitsNotEnabled`.

## Creating Questions & Requesting Permission

Construct a `CommunicationTopic` and `PermissionQuestion` to present to the child:

```swift
let handle = CommunicationHandle(email: "coach@example.com")
let topic = CommunicationTopic(handle: handle)
let question = PermissionQuestion(topic: topic, message: "Can I message Coach Alex?")

// Send request via AskCenter
do {
    let response = try await AskCenter.shared.ask(question)
    switch response.choice {
    case .approved:
        // Parent approved; proceed with communication
        allowCommunication(with: handle)
    case .denied:
        // Parent declined
        notifyUserDenied()
    @unknown default:
        break
    }
} catch AskError.communicationLimitsNotEnabled {
    // Limits disabled; allow without prompt
    allowCommunication(with: handle)
} catch {
    print("Permission request failed: \(error)")
}
```

## SwiftUI PermissionButton

Use `PermissionButton` (iOS 26.2+) to render standardized, accessible triggers:

```swift
import SwiftUI
import PermissionKit

struct ContactRow: View {
    let question: PermissionQuestion

    var body: some View {
        PermissionButton(question) { response in
            if response.choice == .approved {
                // Handle approval
            }
        }
    }
}
```

## Significant App Updates

When introducing major updates to communication features, notify parents using `SignificantAppUpdateTopic`:

```swift
let updateTopic = SignificantAppUpdateTopic(
    title: "Video Calling Feature",
    summary: "New capability to initiate video calls with approved contacts."
)
let question = PermissionQuestion(topic: updateTopic)
```

## Common Mistakes

- **Using PermissionKit for general permissions**: It only manages parental communication exceptions via iMessage.
- **Assuming isKnownHandle checks limit enablement**: It only checks whether a handle is already approved. Handle `AskError.communicationLimitsNotEnabled` explicitly.
- **Omitting bundleIdentifier check**: Calling `knownHandles` without a valid bundle identifier results in runtime failures.
- **Inventing unofficial entitlements**: PermissionKit does not require custom entitlements.
- **Ignoring unknown choice cases**: Always handle `@unknown default` for future parent response choices.

## Review Checklist

- [ ] Availability gates match SDK requirements (iOS 26.0+ core, 26.2+ UI)
- [ ] `Bundle.main.bundleIdentifier` validated before checking handles
- [ ] `AskError.communicationLimitsNotEnabled` caught and handled appropriately
- [ ] `PermissionButton` used in SwiftUI for system-consistent UX
- [ ] All parent response choices (`.approved`, `.denied`) handled cleanly

## References

- Extended patterns (response handling, multi-topic, UIKit): [references/permissionkit-patterns.md](references/permissionkit-patterns.md)
- [PermissionKit framework](https://sosumi.ai/documentation/permissionkit)
- [AskCenter](https://sosumi.ai/documentation/permissionkit/askcenter)
- [PermissionQuestion](https://sosumi.ai/documentation/permissionkit/permissionquestion)
- [PermissionButton](https://sosumi.ai/documentation/permissionkit/permissionbutton)
- [PermissionResponse](https://sosumi.ai/documentation/permissionkit/permissionresponse)
- [CommunicationTopic](https://sosumi.ai/documentation/permissionkit/communicationtopic)
- [CommunicationHandle](https://sosumi.ai/documentation/permissionkit/communicationhandle)
- [CommunicationLimits](https://sosumi.ai/documentation/permissionkit/communicationlimits)
- [SignificantAppUpdateTopic](https://sosumi.ai/documentation/permissionkit/significantappupdatetopic)
- [AskError](https://sosumi.ai/documentation/permissionkit/askerror)
- [Creating a communication experience](https://sosumi.ai/documentation/permissionkit/creating-a-communication-experience)
