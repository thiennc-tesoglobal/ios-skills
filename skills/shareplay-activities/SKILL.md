---
name: shareplay-activities
description: "Build shared real-time experiences using GroupActivities and SharePlay. Use when implementing shared media playback, collaborative app features, synchronized game state, or any FaceTime, Messages, AirDrop, or nearby visionOS group activity on iOS, macOS, tvOS, or visionOS."
---

# GroupActivities and SharePlay

Use GroupActivities for sessions shared through FaceTime, Messages, AirDrop, or
nearby visionOS participation. SharePlay owns invitation, activation, session
lifecycle, participants, messaging, journals, and media-coordination handoffs.

Route Game Center authentication/matchmaking to `gamekit`, tabletop seats and
authoritative board state to `tabletopkit`, and playback UI to `avkit`.

## Contents

- [Choose the workflow](#choose-the-workflow)
- [Setup and activity contract](#setup-and-activity-contract)
- [Session lifecycle](#session-lifecycle)
- [Choose a transport](#choose-a-transport)
- [Activation and UI](#activation-and-ui)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Choose the workflow

Read [SharePlay extended patterns](references/shareplay-patterns.md) when the
task needs a complete long-lived manager, typed message handling, SwiftUI
`ShareLink`/AirDrop integration, collaborative canvas or game state, participant
tracking, or nearby visionOS behavior.

For ordinary implementation:

1. Add Group Activities capability to the app target; do not add it to widgets,
   extensions, or App Clips.
2. Define a small `GroupActivity` with meaningful discovery metadata.
3. Own `Activity.sessions()` in one long-lived manager.
4. Configure observers and transports before `session.join()`.
5. Choose messenger, journal, or AV playback coordination according to the data.
6. Handle late join, leave, end, and invalidation explicitly.

## Setup and activity contract

The capability adds `com.apple.developer.group-session`. A group activity is
Codable; keep it to identifiers, URLs, and concise discovery state:

```swift
import GroupActivities

struct WatchTogetherActivity: GroupActivity {
    let movieID: String
    let movieTitle: String

    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.title = movieTitle
        metadata.type = .watchTogether
        metadata.fallbackURL = URL(string: "https://example.com/movie/\(movieID)")
        return metadata
    }
}
```

Use the metadata type that matches the experience (`watchTogether`,
`listenTogether`, `createTogether`, and so on). Add `Transferable` only when
using `ShareLink`, AirDrop, or share sheets—not merely because the activity is
Codable.

## Session lifecycle

- Start one long-lived `for await session in Activity.sessions()` listener.
- Store the session, create its messenger/journal, subscribe to state and active
  participants, then call `join()`.
- On `.invalidated`, cancel child tasks and release messenger, journal, and
  session state.
- `leave()` exits locally; `end()` terminates the session for everyone. Make the
  product choice explicit.
- Track participant-set differences and send an authoritative current-state
  snapshot to late joiners.
- Do not put the session listener in a SwiftUI view body or another object that
  is recreated during navigation.

## Choose a transport

| Need | Transport | Constraints |
|---|---|---|
| Small shared state/action | `GroupSessionMessenger` `.reliable` | Codable message, under 256 KB |
| High-frequency ephemeral samples | Messenger `.unreliable` | Loss-tolerant; do not use for authoritative turns/selections |
| Non-time-sensitive attachment | `GroupSessionJournal` | `Transferable`, available to late joiners, up to 100 MB |
| Larger/protected asset | App/server transfer | Share an identifier or manifest through SharePlay |
| AVPlayer transport state | `AVPlaybackCoordinator` | Do not duplicate play/pause/seek messages or snapshots |

Journal requires iOS/iPadOS/tvOS 17+, macOS 14+, or visionOS 1+. Application
messages remain responsible for state outside coordinated playback.

## Activation and UI

Use `GroupStateObserver.isEligibleForGroupSession` to adapt the SharePlay entry
point. When a conversation is active, call `prepareForActivation()` and handle
`.activationPreferred`, `.activationDisabled`, and `.cancelled`. When no
conversation is active, present `GroupActivitySharingController` so the user
can choose participants.

Use the `shareplay` SF Symbol for custom controls and keep metadata title,
subtitle, image, and type aligned with the entry point. A disabled activation
can fall back to the local experience; it is not an error to force past.

## Common mistakes

- Receiving a session but never calling `join()`.
- Leaving child observation tasks alive after invalidation.
- Broadcasting deltas without bootstrapping late joiners.
- Sending large attachments through the messenger.
- Using `.unreliable` for authoritative state changes.
- Manually synchronizing AVPlayer transport after attaching its playback coordinator.
- Presenting only a FaceTime-active path and omitting participant selection.

## Review checklist

- [ ] Capability belongs to the app target only.
- [ ] Activity payload is small, Codable, and has accurate metadata.
- [ ] `Transferable` exists only where a sharing surface requires it.
- [ ] One long-lived owner observes `sessions()` and cleans up child tasks.
- [ ] Session configuration precedes `join()`; leave/end semantics are intentional.
- [ ] Participant changes trigger late-join state bootstrap.
- [ ] Messenger delivery mode and size fit the message semantics.
- [ ] Journal or app-managed transfer handles larger assets.
- [ ] AV media uses `AVPlaybackCoordinator` without redundant transport messages.
- [ ] Eligibility, activation result, and no-conversation sharing UI are handled.

## References

- [SharePlay extended patterns](references/shareplay-patterns.md)
- [GroupActivities documentation](https://sosumi.ai/documentation/groupactivities)
- [GroupSession](https://sosumi.ai/documentation/groupactivities/groupsession)
- [GroupSessionMessenger](https://sosumi.ai/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://sosumi.ai/documentation/groupactivities/groupsessionjournal)
- [SharePlay HIG](https://sosumi.ai/design/human-interface-guidelines/shareplay)
