---
name: mapkit
description: "Build or review maps and location features with MapKit and Core Location. Use for map views, annotations, overlays, user location, geocoding, place search, directions, geofencing, region monitoring, location authorization, or coordinate-based app behavior."
---

# MapKit

Build map-based and location-aware features targeting iOS 17+ with SwiftUI
MapKit and modern CoreLocation async APIs. Use `Map` with `MapContentBuilder`
for views, `CLLocationUpdate.liveUpdates()` for streaming location, and
`CLMonitor` for geofencing.

Read [references/mapkit-patterns.md](references/mapkit-patterns.md) when you need full map setup, search,
routes, Look Around, snapshots, or iOS 26 place APIs. Read
[references/mapkit-corelocation-patterns.md](references/mapkit-corelocation-patterns.md) when the task involves
location update lifecycle, geofencing, background location, testing, or privacy keys.

## Workflow

1. Define the exact map/location capability and request only the authorization it needs.
2. Choose SwiftUI Map or UIKit hosting, then establish camera ownership, selection, annotations, and overlay identity.
3. Keep search, geocoding, directions, and live-location tasks cancellable and scoped to the current query/session.
4. Handle denied/restricted/reduced-accuracy states and avoid treating coordinates as always available.
5. Verify empty results, movement, camera changes, route failures, localization, offline/network transitions, and background rules.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for SwiftUI maps, camera, annotations, overlays, live updates, authorization, geocoding, search, and directions.
- Read [MapKit patterns](references/mapkit-patterns.md) for clustering, Look Around, snapshots, complex routes, and full map setup.
- Read [Core Location patterns](references/mapkit-corelocation-patterns.md) for `CLLocationUpdate`, monitoring, service sessions, background behavior, and testing.

## Core Decisions

- Do not infer authorization from API availability or a non-nil cached location.
- Use stable identities for annotations and overlays.
- Debounce and cancel search/geocoding work when input changes.
- Treat size, viewport, and user interaction as live state rather than fixed screen assumptions.

## Common Mistakes

**DON'T:** Request always authorization upfront.
**DO:** Start with when-in-use authorization. On iOS 18+, hold a `CLServiceSession`
for the feature lifetime; request `.always` only for background features that
need system relaunch after termination.

**DON'T:** Use `CLLocationManagerDelegate` for simple location fetches on iOS 17+.
**DO:** Use `CLLocationUpdate.liveUpdates()` async stream for cleaner, more concise code.

**DON'T:** Ignore `CLLocationUpdate` diagnostics such as denied, globally denied, or unavailable location.
**DO:** Stop or degrade the feature, show recovery UI such as Settings guidance, and keep search/manual flows usable.

**DON'T:** Let `liveUpdates()` run from an unowned task after the map/view is gone.
**DO:** Store the `Task`, cancel it when the feature stops, and filter invalid, inaccurate, stale, or impossible movement fixes.

**DON'T:** Force-unwrap `CLPlacemark` properties — they are all optional.
**DO:** Use nil-coalescing: `placemark.locality ?? "Unknown"`.

**DON'T:** Fire `MKLocalSearchCompleter` queries on every keystroke.
**DO:** Debounce with `.task(id: searchText)` + `Task.sleep(for: .milliseconds(300))`.

**DON'T:** Silently fail when location authorization is denied.
**DO:** Detect `.denied` status and show an alert with a Settings deep link.

**DON'T:** Assume geocoding always succeeds — handle empty results and network errors.

## Review Checklist

- [ ] Info.plist has `NSLocationWhenInUseUsageDescription` with specific reason
- [ ] Authorization denial handled with Settings deep link
- [ ] `CLLocationUpdate` task cancelled when not needed (battery)
- [ ] Location accuracy appropriate for the use case
- [ ] Map annotations use `Identifiable` data with stable IDs
- [ ] Geocoding errors handled (network failure, no results)
- [ ] Search completer input debounced
- [ ] `CLMonitor` limited to 20 conditions, instance kept alive
- [ ] Background location uses `CLBackgroundActivitySession`
- [ ] Map tested with VoiceOver
- [ ] Map annotation view models and location UI updates are `@MainActor`-isolated

## References

- [references/mapkit-patterns.md](references/mapkit-patterns.md) — Map setup, annotations, search, routes, clustering, Look Around, snapshots.
- [references/mapkit-corelocation-patterns.md](references/mapkit-corelocation-patterns.md) — CLLocationUpdate, CLMonitor, CLServiceSession, background location, testing.
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
