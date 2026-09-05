---
name: core-data
description: "Build or review persistence in apps that still use Core Data, including managed objects, fetched results, batch operations, persistent history, staged migration, and concurrency. Use for Core Data-only work; route SwiftData adoption or coexistence to swiftdata."
---

# Core Data

Build and maintain data persistence using Core Data for apps that have not adopted SwiftData. Covers stack setup, concurrency, batch operations, NSFetchedResultsController, persistent history tracking, staged migration, and testing.

## Contents

- [Stack Setup & Concurrency](#stack-setup--concurrency)
- [NSFetchedResultsController](#nsfetchedresultscontroller)
- [Batch Operations](#batch-operations)
- [Persistent History Tracking](#persistent-history-tracking)
- [Staged Migration & Coexistence](#staged-migration--coexistence)
- [Testing](#testing)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Stack Setup & Concurrency

Core Data contexts are bound to queues: `viewContext` runs on the main queue, while background tasks use `newBackgroundContext()`.

- **Context Isolation**: Always wrap access in `context.perform(_:)` or `context.performAndWait(_:)`.
- **Thread Crossing**: Never pass `NSManagedObject` instances between contexts or threads; pass `NSManagedObjectID` and re-fetch via `existingObject(with:)`.
- **Automatic Merging**: Set `automaticallyMergesChangesFromParent = true` and configure `mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy` on `viewContext`.

```swift
import CoreData

func updateTrip(id: NSManagedObjectID, name: String) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        guard let trip = try context.existingObject(with: id) as? CDTrip else { return }
        trip.name = name
        if context.hasChanges { try context.save() }
    }
}
```

## NSFetchedResultsController

Drives UI collections from an `NSFetchRequest` with automatic change tracking:

- Always supply at least one sort descriptor in the fetch request.
- Use diffable snapshots (`controller(_:didChangeContentWith:)`) on iOS 13+ to animate UI changes.
- Delete the cache with `deleteCache(withName:)` before changing predicate or sort descriptors, or pass `cacheName: nil`.

## Batch Operations

`NSBatchInsertRequest`, `NSBatchUpdateRequest`, and `NSBatchDeleteRequest` execute directly at the SQLite level, bypassing managed object contexts.

- Set `resultType = .objectIDs` / `.resultTypeObjectIDs`.
- Merge results manually into live contexts using `NSManagedObjectContext.mergeChanges(fromRemoteContextSave:into:)`.
- Note that batch deletes bypass Core Data relationship delete rules (e.g. `Deny`).

## Persistent History Tracking

Track store modifications across app extensions, widgets, and processes:

- Enable `NSPersistentHistoryTrackingKey: true` in store options.
- Query changes using `NSPersistentHistoryChangeRequest` and merge them into local contexts.
- Purge consumed transactions periodically with history truncation requests to prevent database bloat.
- Read [references/persistent-history.md](references/persistent-history.md) for full transaction tracking and purge loops.

## Staged Migration & Coexistence

- **Staged Migration (iOS 17+)**: Use `NSStagedMigrationManager` with lightweight and custom stages (`NSCustomMigrationStage`) for deterministic upgrades. Read [references/staged-migration.md](references/staged-migration.md).
- **SwiftData Boundary**: When sharing a database file with SwiftData, point both to the same store URL, preserve model schemas and attribute names, and map renames with `@Attribute(originalName:)`. Route pure SwiftData work to the `swiftdata` skill.

## Testing

Use `NSInMemoryStoreType` for deterministic unit testing. Share a single compiled `NSManagedObjectModel` instance across tests to prevent duplicate entity runtime errors.

## Common Mistakes

- **Passing NSManagedObject across threads**: Causes concurrency crashes. Always pass `NSManagedObjectID` and refetch with `existingObject(with:)`.
- **Missing mergeChanges after batch requests**: Batch operations bypass memory contexts. Always merge returned object IDs.
- **Calling save() without hasChanges**: Avoid redundant I/O; guard saves with `if context.hasChanges`.
- **Omitting merge policy on viewContext**: Missing `mergePolicy` causes conflict save crashes. Set `NSMergeByPropertyObjectTrumpMergePolicy`.
- **Marking NSManagedObject as Sendable**: Managed objects are queue-bound. Do not mark `@unchecked Sendable`.

## Review Checklist

- [ ] `NSPersistentContainer` created once and shared across the app
- [ ] Context access strictly guarded by `perform(_:)` or `performAndWait(_:)`
- [ ] No `NSManagedObject` instances cross thread or context boundaries
- [ ] `viewContext.automaticallyMergesChangesFromParent` is enabled
- [ ] `mergePolicy` configured on contexts to handle conflicts cleanly
- [ ] Batch operation results merged into active contexts via `mergeChanges`
- [ ] `NSFetchedResultsController` requests include explicit sort descriptors
- [ ] In-memory test stores reuse a shared `NSManagedObjectModel`

## References

- Implementation patterns (Stack, FRC, Batch, Testing): [references/core-data-patterns.md](references/core-data-patterns.md)
- Cross-process tracking: [references/persistent-history.md](references/persistent-history.md)
- Staged migration: [references/staged-migration.md](references/staged-migration.md)
- [Core Data](https://sosumi.ai/documentation/coredata)
- [NSPersistentContainer](https://sosumi.ai/documentation/coredata/nspersistentcontainer)
- [NSFetchedResultsController](https://sosumi.ai/documentation/coredata/nsfetchedresultscontroller)
- [NSStagedMigrationManager](https://sosumi.ai/documentation/coredata/nsstagedmigrationmanager)
