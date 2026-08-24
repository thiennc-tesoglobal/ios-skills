---
name: eventkit
description: "Creates, reads, edits, and presents calendar events or reminders with EventKit and EventKitUI. Use for authorization, event/reminder CRUD, calendars, recurrence, alarms, change observation, event editors, viewers, calendar choosers, or SwiftUI wrappers."
---

# EventKit

Use EventKit for calendar and reminder authorization, CRUD, recurrence, alarms,
and system editors.

## Workflow

1. Determine whether the app needs event write-only access, full event access, or reminder access and declare the matching usage descriptions.
2. Retain one `EKEventStore`, request the narrowest authorization, and branch on current status.
3. Create or fetch objects from that store, choose writable calendars, and make timezone/recurrence semantics explicit.
4. Save or batch changes with the intended commit policy and surface recoverable errors.
5. Observe store changes and verify denied/restricted access, recurrence edits, timezone changes, and external modifications.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for authorization, events, reminders, recurrence, alarms, EventKitUI, and change observation.
- Read [extended EventKit patterns](references/eventkit-patterns.md) for SwiftUI wrappers, predicates, batch operations, and advanced recurrence workflows.

## Core Decisions

- Use current full-access/write-only authorization APIs rather than legacy generic access calls.
- Never mix `EKObject` instances from different event stores.
- Check calendar mutability before save and preserve explicit timezone intent.
- Decide whether recurring edits affect one occurrence or the future span before saving.

## Common Mistakes

### DON'T: Use legacy requestAccess(to:) on current systems

```swift
// WRONG: Legacy request API on current systems
eventStore.requestAccess(to: .event) { granted, error in }

// CORRECT: Use the granular async methods
let granted = try await eventStore.requestFullAccessToEvents()
```

Keep it only in the compatibility fallback from [Availability](#availability).

### DON'T: Save events to a read-only calendar

```swift
// WRONG: No check -- will throw if calendar is read-only
event.calendar = someCalendar
try eventStore.save(event, span: .thisEvent)

// CORRECT: Verify the calendar allows modifications
guard someCalendar.allowsContentModifications else {
    event.calendar = eventStore.defaultCalendarForNewEvents
    return
}
event.calendar = someCalendar
try eventStore.save(event, span: .thisEvent)
```

### DON'T: Ignore timezone when creating events

```swift
// WRONG: Event appears at wrong time for traveling users
event.startDate = Date()
event.endDate = Date().addingTimeInterval(3600)

// CORRECT: Set the timezone explicitly for location-specific events
event.timeZone = TimeZone(identifier: "America/New_York")
event.startDate = startDate
event.endDate = endDate
```

### DON'T: Forget to commit batched saves

```swift
// WRONG: Changes never persisted
try eventStore.save(event1, span: .thisEvent, commit: false)
try eventStore.save(event2, span: .thisEvent, commit: false)
// Missing commit!

// CORRECT: Commit after batching
try eventStore.save(event1, span: .thisEvent, commit: false)
try eventStore.save(event2, span: .thisEvent, commit: false)
try eventStore.commit()
```

### DON'T: Mix EKObjects from different event stores

```swift
// WRONG: Event fetched from storeA, saved to storeB
let event = storeA.event(withIdentifier: id)!
try storeB.save(event, span: .thisEvent) // Undefined behavior

// CORRECT: Use the same store throughout
let event = eventStore.event(withIdentifier: id)!
try eventStore.save(event, span: .thisEvent)
```

## Review Checklist

- [ ] Correct `Info.plist` usage description keys added for calendars and/or reminders
- [ ] Authorization follows the version split in [Availability](#availability)
- [ ] Write-only calendar access used only for direct event creation, not event/calendar reads
- [ ] Authorization status checked before fetching or saving
- [ ] Full access required before any event or reminder fetch
- [ ] Single `EKEventStore` instance reused across the app
- [ ] Events saved to a writable calendar (`allowsContentModifications` checked)
- [ ] Recurring event saves specify correct `EKSpan` (`.thisEvent` vs `.futureEvents`)
- [ ] Batched saves validate writable calendars, stage with `commit: false`,
      call throwing `commit()`, and on failure `reset()` unsaved state, discard
      every invalidated `EKObject`, then refetch or reconstruct before retry
- [ ] `EKEventStoreChanged` notification observed to refresh stale data
- [ ] Change observation uses the classic notification or guarded typed message per [Availability](#availability)
- [ ] Timezone set explicitly for location-specific events
- [ ] EKObjects not shared across different event store instances
- [ ] EventKitUI delegates dismiss controllers in completion callbacks

## References

- Extended patterns (SwiftUI wrappers, predicate queries, batch operations): [references/eventkit-patterns.md](references/eventkit-patterns.md)
- [EventKit framework](https://sosumi.ai/documentation/eventkit)
- [EKEventStore](https://sosumi.ai/documentation/eventkit/ekeventstore)
- [EKEvent](https://sosumi.ai/documentation/eventkit/ekevent)
- [EKReminder](https://sosumi.ai/documentation/eventkit/ekreminder)
- [EKRecurrenceRule](https://sosumi.ai/documentation/eventkit/ekrecurrencerule)
- [EKCalendar](https://sosumi.ai/documentation/eventkit/ekcalendar)
- [EventKit UI](https://sosumi.ai/documentation/eventkitui)
- [EKEventEditViewController](https://sosumi.ai/documentation/eventkitui/ekeventeditviewcontroller)
- [EKCalendarChooser](https://sosumi.ai/documentation/eventkitui/ekcalendarchooser)
- [Accessing the event store](https://sosumi.ai/documentation/eventkit/accessing-the-event-store)
- [Creating a recurring event](https://sosumi.ai/documentation/eventkit/creating-a-recurring-event)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
