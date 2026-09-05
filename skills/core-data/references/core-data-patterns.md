# Core Data Implementation Patterns

Extended patterns for Core Data stack setup, NSFetchedResultsController, batch operations, and test harness. See `SKILL.md` for core rules and concurrency constraints.

## Contents

- [Persistent Container Setup](#persistent-container-setup)
- [Concurrency & Background Contexts](#concurrency--background-contexts)
- [NSFetchedResultsController with Diffable Data Source](#nsfetchedresultscontroller-with-diffable-data-source)
- [Batch Insert, Update, and Delete](#batch-insert-update-and-delete)
- [In-Memory Test Container](#in-memory-test-container)

## Persistent Container Setup

Encapsulate the Core Data stack in a thread-safe singleton:

```swift
import CoreData

final class CoreDataStack: @unchecked Sendable {
    static let shared = CoreDataStack()

    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "MyAppModel")
        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data store failed: \(error)") }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    var viewContext: NSManagedObjectContext { container.viewContext }

    func newBackgroundContext() -> NSManagedObjectContext {
        container.newBackgroundContext()
    }
}
```

## Concurrency & Background Contexts

Execute background writes using `perform(_:)` or `performAndWait(_:)`, passing object IDs instead of managed object instances across threads:

```swift
func updateTrip(id: NSManagedObjectID, newName: String) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        guard let trip = try context.existingObject(with: id) as? CDTrip else {
            throw PersistenceError.notFound
        }
        trip.name = newName
        if context.hasChanges {
            try context.save()
        }
    }
}
```

## NSFetchedResultsController with Diffable Data Source

Drive collection and table views with diffable snapshot change tracking:

```swift
import CoreData
import UIKit

class TripsViewController: UITableViewController, NSFetchedResultsControllerDelegate {
    private lazy var fetchedResultsController: NSFetchedResultsController<CDTrip> = {
        let request: NSFetchRequest<CDTrip> = CDTrip.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \CDTrip.startDate, ascending: false)]
        request.fetchBatchSize = 20

        let controller = NSFetchedResultsController(
            fetchRequest: request,
            managedObjectContext: CoreDataStack.shared.viewContext,
            sectionNameKeyPath: nil,
            cacheName: nil
        )
        controller.delegate = self
        return controller
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        try? fetchedResultsController.performFetch()
    }

    func controller(
        _ controller: NSFetchedResultsController<any NSFetchRequestResult>,
        didChangeContentWith snapshot: NSDiffableDataSourceSnapshotReference
    ) {
        let diffableSnapshot = snapshot as NSDiffableDataSourceSnapshot<String, NSManagedObjectID>
        dataSource.apply(diffableSnapshot, animatingDifferences: true)
    }
}
```

## Batch Insert, Update, and Delete

Batch operations run directly against SQLite, bypassing context change tracking. Always merge returned object IDs into live contexts:

```swift
// Batch Insert
func batchImport(_ records: [[String: Any]]) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let request = NSBatchInsertRequest(entity: CDTrip.entity(), objects: records)
        request.resultType = .objectIDs
        let result = try context.execute(request) as? NSBatchInsertResult
        if let ids = result?.result as? [NSManagedObjectID] {
            NSManagedObjectContext.mergeChanges(
                fromRemoteContextSave: [NSInsertedObjectsKey: ids],
                into: [CoreDataStack.shared.viewContext]
            )
        }
    }
}

// Batch Delete
func deleteOldTrips(before cutoff: Date) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let fetchRequest: NSFetchRequest<NSFetchRequestResult> = CDTrip.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "endDate < %@", cutoff as NSDate)
        let request = NSBatchDeleteRequest(fetchRequest: fetchRequest)
        request.resultType = .resultTypeObjectIDs
        let result = try context.execute(request) as? NSBatchDeleteResult
        if let ids = result?.result as? [NSManagedObjectID] {
            NSManagedObjectContext.mergeChanges(
                fromRemoteContextSave: [NSDeletedObjectsKey: ids],
                into: [CoreDataStack.shared.viewContext]
            )
        }
    }
}
```

## In-Memory Test Container

Share a single compiled `NSManagedObjectModel` to prevent duplicate entity warnings across tests:

```swift
import CoreData
import Testing

private let sharedModel: NSManagedObjectModel = {
    let url = Bundle.main.url(forResource: "MyAppModel", withExtension: "momd")!
    return NSManagedObjectModel(contentsOf: url)!
}()

func makeTestContainer() throws -> NSPersistentContainer {
    let container = NSPersistentContainer(name: "MyAppModel", managedObjectModel: sharedModel)
    let description = NSPersistentStoreDescription()
    description.type = NSInMemoryStoreType
    container.persistentStoreDescriptions = [description]

    var loadError: Error?
    container.loadPersistentStores { _, error in loadError = error }
    if let loadError { throw loadError }
    return container
}
```
