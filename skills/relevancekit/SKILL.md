---
name: relevancekit
description: "Increase widget visibility on Apple Watch using RelevanceKit. Use when providing contextual relevance signals for watchOS widgets, declaring time-based or location-based relevance, combining multiple relevance providers, helping the system surface the right widget at the right time on watchOS 26, or routing mixed RelevanceKit/WidgetKit/HealthKit/MapKit Smart Stack scope."
---

# RelevanceKit

Use RelevanceKit to tell the Apple Watch Smart Stack when a widget matters by
time, location, fitness state, sleep schedule, or connected hardware. Targets
Swift 6.3 and watchOS 26+ relevant-widget workflows.

> **Beta-sensitive.** Re-check current Apple documentation before changing
> availability, signatures, or Smart Stack behavior.

## Contents

- [Choose a provider](#choose-a-provider)
- [Scope boundaries](#scope-boundaries)
- [Signals and permissions](#signals-and-permissions)
- [Provider invariants](#provider-invariants)
- [Testing](#testing)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Choose a provider

Use one of two models:

1. Add `relevance()` to an existing `AppIntentTimelineProvider` when the widget
   always has timeline content and relevance is supplementary.
2. Use `RelevanceConfiguration` with a `RelevanceEntriesProvider` when the
   widget should appear only under matching conditions or create multiple
   relevant cards. This path is watchOS 26+.

Read [RelevanceKit patterns](references/relevancekit-patterns.md) for complete
providers, every `RelevantContext` factory, permissions, grouping,
`associatedKind`, previews, and `RelevantIntentManager` updates.

`RelevantContext` is declared across Apple platforms, but its relevance effect
is watchOS-only. Shared provider code may compile elsewhere without changing
widget visibility there.

## Scope boundaries

Keep this skill focused on `RelevantContext`, `WidgetRelevanceAttribute`,
provider `relevance()`, `RelevanceConfiguration`, grouping,
`RelevantIntentManager`, and permissions required by relevance clues.

Route these sibling concerns elsewhere:

- Widget timelines, families, reload budgets, rendering, push reloads, Live
  Activities, and controls → `widgetkit`.
- Workout sessions, activity/sleep queries, routes, and HealthKit authorization
  UX → `healthkit`.
- Geocoding, place search, directions, regions, geofencing, and location
  authorization architecture → `mapkit`.

## Signals and permissions

| Context | Use | Required setup |
|---|---|---|
| `.date(...)` | Moment, scheduled event, or date interval | None |
| `.location(inferred:)` | Home, work, school, commute | App location permission plus `NSWidgetWantsLocation` |
| `.location(_:)` | Specific `CLRegion` | Same location setup |
| `.location(category:)` | Nearby point-of-interest category | Same setup; returns optional |
| `.fitness(.workoutActive)` | Active workout | HealthKit read access to `HKWorkoutType` |
| `.fitness(.activityRingsIncomplete)` | Ring progress | Exact exercise/move/stand read types |
| `.sleep(...)` | Bedtime or wakeup | Sleep-analysis read access |
| `.hardware(headphones:)` | Headphone connection | None |

Location purpose strings belong in the containing app. The widget extension
declares `NSWidgetWantsLocation` and checks
`CLLocationManager.isAuthorizedForWidgetUpdates`. Enable HealthKit and request
the exact read types in every target that supplies fitness or sleep relevance.

## Provider invariants

- Return `WidgetRelevanceAttribute` values in priority order; the system may use
  only a subset.
- `location(category:)` is optional—omit unsupported categories rather than
  force-unwrapping.
- A relevance entries provider supplies `relevance`, `entry`, `placeholder`,
  and a deterministic preview path.
- When timeline and relevant widgets represent the same data, set
  `.associatedKind(_:)` to avoid duplicate Smart Stack cards.
- Use `.automatic`, `.ungrouped`, or `.named` grouping intentionally.
- For timeline-provider relevance, call
  `RelevantIntentManager.shared.updateRelevantIntents` whenever source data
  changes, not only during timeline refresh.
- Degrade gracefully when authorization is absent; do not manufacture false
  location, fitness, or sleep clues.

## Testing

- Enable WidgetKit Developer Mode on the Apple Watch.
- Preview entry and configuration states at relevant display sizes.
- Exercise permission granted, denied, restricted, and unavailable data paths.
- Verify ordering, grouping, and duplicate suppression with realistic entries.
- Finish on a physical watch; do not treat compilation or iOS preview behavior
  as proof of Smart Stack ranking.

## Common mistakes

- Expecting RelevanceKit calls to affect iOS widget ranking.
- Creating a relevant widget when a normal timeline plus relevance is sufficient.
- Returning location clues without widget-update authorization.
- Failing to refresh relevant intents after source data changes.
- Omitting `associatedKind` and creating duplicate cards.
- Assuming every point-of-interest category creates a context.

## Review checklist

- [ ] Provider model matches always-available versus condition-only content.
- [ ] Relevance scope is separated from WidgetKit, HealthKit, and MapKit ownership.
- [ ] Every clue has its exact permission and availability setup.
- [ ] Attributes are priority-ordered and unsupported optionals are omitted.
- [ ] Entry, placeholder, relevance, and preview paths are deterministic.
- [ ] Grouping and `associatedKind` prevent unwanted duplicates.
- [ ] Relevant intents update whenever underlying data changes.
- [ ] Physical-watch testing covers permission and ranking behavior.

## References

- [RelevanceKit patterns](references/relevancekit-patterns.md)
- [RelevanceKit documentation](https://sosumi.ai/documentation/relevancekit)
- [RelevantContext](https://sosumi.ai/documentation/relevancekit/relevantcontext)
- [Smart Stack widget suggestions](https://sosumi.ai/documentation/widgetkit/widget-suggestions-in-smart-stacks)
- [RelevanceConfiguration](https://sosumi.ai/documentation/widgetkit/relevanceconfiguration)
- [RelevanceEntriesProvider](https://sosumi.ai/documentation/widgetkit/relevanceentriesprovider)
