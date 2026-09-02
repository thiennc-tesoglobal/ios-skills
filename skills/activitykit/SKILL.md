---
name: activitykit
description: "Build or review Live Activities and Dynamic Island experiences with ActivityKit, including lifecycle, layouts, push updates, and scheduled delivery. Use for time-sensitive Lock Screen or Dynamic Island state; route ordinary widgets to widgetkit."
---

# ActivityKit

ActivityKit owns real-time, glanceable Live Activities on the Lock Screen and
Dynamic Island. Route ordinary timeline widgets to `widgetkit` and generic APNs
setup to `push-notifications`; keep the Live Activity lifecycle, token handling,
and payload contract here.

Modern `ActivityContent` lifecycle APIs require iOS 16.2+ unless noted. The
server's `aps.content-state` must decode into the exact
`ActivityAttributes.ContentState` shape, including coordinated custom date or
range encoding.

## Contents

- [Choose the workflow](#choose-the-workflow)
- [Core contract](#core-contract)
- [Lifecycle and delivery rules](#lifecycle-and-delivery-rules)
- [Presentation rules](#presentation-rules)
- [Availability-sensitive features](#availability-sensitive-features)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Choose the workflow

- For attributes, local request/update code, push-to-update, push-to-start,
  channel payloads, and exact APNs headers, read
  [Lifecycle, updates, and push](references/lifecycle-updates-and-push.md).
- For dismissal policies, terminal cleanup, Lock Screen layouts, and every
  Dynamic Island region, read
  [Ending and presentation](references/ending-and-presentation.md).
- For multiple activities, authorization, rotating tokens, background behavior,
  Simulator/device verification, previews, and Info.plist keys, read
  [Concurrency, state, and testing](references/concurrency-state-and-testing.md).

For a new Live Activity:

1. Enable the host-app capability and set `NSSupportsLiveActivities = YES`.
2. Separate immutable `ActivityAttributes` from a small, `Codable`, `Hashable`
   `ContentState`; encode a representative server fixture before integrating APNs.
3. Build `ActivityConfiguration` for the Lock Screen first, then compact,
   minimal, and expanded Dynamic Island presentations.
4. Check `ActivityAuthorizationInfo.areActivitiesEnabled`, request with
   `ActivityContent`, and exercise local update plus every terminal end path.
5. For remote delivery, observe every emitted token and validate update, end,
   and push-to-start payloads against the same Codable contract.

## Core contract

Keep static identity in the outer attributes and only changing display state in
`ContentState`:

```swift
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    let orderNumber: Int

    struct ContentState: Codable, Hashable {
    var stage: String
        var estimatedDelivery: ClosedRange<Date>
    }
}
```

Use `ActivityContent` for request, update, and end. Set `staleDate` whenever the
display can become misleading, and render a safe fallback from
`ActivityViewContext.isStale`. Treat Lock Screen content as public: never place
secrets or sensitive detail in attributes or state.

## Lifecycle and delivery rules

- End on success, user/app cancellation, sign-out, unrecoverable app error, and
  terminal server failure. Apply a final truthful state before ending when one
  exists.
- Distinguish the active lifetime (up to 8 hours), system-ended Lock Screen
  presence (up to 4 additional hours), and an app-ended `.default` dismissal
  linger (up to 4 hours after ending).
- Use `.token` for per-activity remote updates. Observe
  `activity.pushTokenUpdates` for the full activity lifetime because tokens rotate.
- Push-to-start uses `Activity<Attributes>.pushToStartTokenUpdates`; it is not an
  app APNs token or an activity update token. Its payload requires an alert.
- Live Activity pushes require `apns-push-type: liveactivity`. Device-token
  pushes use `<bundle-id>.push-type.liveactivity` as the topic. Priority controls
  delivery urgency; only `aps.alert` requests visible alert behavior.
- `NSSupportsLiveActivitiesFrequentUpdates` requests a larger system-managed
  budget, not a guaranteed cadence. Check `frequentPushesEnabled`.
- Do not fetch network or location data from the widget extension view. Compute
  display state in the app/server and deliver it through ActivityKit.

## Presentation rules

- Design the Lock Screen first; Dynamic Island is unavailable on some devices.
- Compact leading/trailing regions contain only identity plus one critical value.
- Minimal presentation must work as a single glyph when activities compete.
- Expanded regions must tolerate content changes without relying on fixed sizes.
- Render stale and terminal states explicitly; avoid pretending old progress is live.
- Test push delivery and Dynamic Island behavior on physical hardware.

## Availability-sensitive features

| Feature | Availability and constraint |
|---|---|
| Push-to-start | iOS 17.2+ |
| `style:` request parameter | iOS 18+; `.standard` for persistent work, `.transient` only for short-lived expanded presentation |
| Channel/broadcast updates | iOS 18+; update/end only, not start |
| Supplemental activity families | iOS 18+ |
| Scheduled start | iOS 26+ |
| Paired Mac and CarPlay presentation | iOS 26+; validate compact layouts and noninteractive CarPlay behavior |

Use availability guards around each newer API. Read the lifecycle reference for
complete request and payload examples rather than combining signatures from
different OS branches.

## Common mistakes

- Using deprecated `contentState` request/update/end overloads instead of
  `ActivityContent`.
- Ignoring token rotation or registering only the first emitted token.
- Assuming APNs priority creates an alert without `aps.alert`.
- Leaving an activity alive after a terminal state.
- Treating Dynamic Island as the only presentation surface.
- Omitting stale UI, overloading compact regions, or exposing sensitive data.
- Assuming frequent-update capability guarantees a fixed update frequency.

## Review checklist

- [ ] Static attributes and dynamic `ContentState` have a small, tested Codable contract.
- [ ] Host app contains `NSSupportsLiveActivities = YES` and authorization is checked.
- [ ] Request, update, and end use `ActivityContent`.
- [ ] Every terminal path ends the activity with an intentional dismissal policy.
- [ ] Lock Screen, stale, compact, minimal, expanded, and terminal states are covered.
- [ ] Update and push-to-start tokens are collected from the correct async sequences.
- [ ] APNs headers, alert semantics, and `content-state` fixtures are validated.
- [ ] Newer APIs have explicit availability guards.
- [ ] Extension views perform no network or location work.
- [ ] Simulator previews and physical-device delivery checks both exist.

## References

- [Lifecycle, updates, and push](references/lifecycle-updates-and-push.md)
- [Ending and presentation](references/ending-and-presentation.md)
- [Concurrency, state, and testing](references/concurrency-state-and-testing.md)
- [ActivityKit documentation](https://sosumi.ai/documentation/activitykit)
