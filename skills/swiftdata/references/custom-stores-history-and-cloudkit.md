# SwiftData Custom Stores, History, and CloudKit

Deep reference for custom data stores, history tracking, CloudKit integration,
Core Data coexistence, batch operations, complex predicates, composite
attributes, model inheritance, multiple containers, undo/redo, and preview
patterns.

---

## Custom Data Stores (iOS 18+)

### DataStore Protocol

Implement the `DataStore` protocol to replace the default SQLite-backed store
with a custom persistence backend (JSON files, in-memory caches, REST APIs,
etc.).

```swift
final class JSONStore: DataStore {
    typealias Configuration = JSONStoreConfiguration
    typealias Snapshot = DefaultSnapshot

    let configuration: JSONStoreConfiguration
    let identifier: String
    let schema: Schema

    init(_ configuration: JSONStoreConfiguration,
         migrationPlan: (any SchemaMigrationPlan.Type)?) throws {
        self.configuration = configuration
        self.identifier = configuration.name
        self.schema = configuration.schema ?? Schema()
    }

    func fetch<T: PersistentModel>(
        _ request: DataStoreFetchRequest<T>
    ) throws -> DataStoreFetchResult<T, DefaultSnapshot> {
        // Load data from JSON file, apply predicate/sort from request.descriptor
        let snapshots: [DefaultSnapshot] = []  // Populate from file
        return DataStoreFetchResult(
            descriptor: request.descriptor,
            fetchedSnapshots: snapshots,
            relatedSnapshots: [:]
        )
    }

    func fetchCount<T: PersistentModel>(
        _ request: DataStoreFetchRequest<T>
    ) throws -> Int {
        try fetch(request).fetchedSnapshots.count
    }

    func fetchIdentifiers<T: PersistentModel>(
        _ request: DataStoreFetchRequest<T>
    ) throws -> [PersistentIdentifier] {
        try fetch(request).fetchedSnapshots.map(\.persistentIdentifier)
    }

    func save(
        _ request: DataStoreSaveChangesRequest<DefaultSnapshot>
    ) throws -> DataStoreSaveChangesResult<DefaultSnapshot> {
        // Persist inserted, updated; remove deleted
        return DataStoreSaveChangesResult(
            for: identifier,
            remappedIdentifiers: [:],
            snapshotsToReregister: [:]
        )
    }

    func erase() throws {
        // Remove all persisted data
    }

    func initializeState(for editingState: EditingState) {}
    func invalidateState(for editingState: EditingState) {}

    func cachedSnapshots(
        for identifiers: [PersistentIdentifier],
        editingState: EditingState
    ) throws -> [PersistentIdentifier: DefaultSnapshot] {
        [:]
    }
}
```

### DataStoreConfiguration

```swift
struct JSONStoreConfiguration: DataStoreConfiguration {
    typealias Store = JSONStore

    let name: String
    var schema: Schema?
    let fileURL: URL

    init(name: String, fileURL: URL) {
        self.name = name
        self.fileURL = fileURL
    }

    func validate() throws {
        // Validate file URL is accessible
    }
}
```

### Using a Custom Store

```swift
let config = JSONStoreConfiguration(
    name: "JSONStore",
    fileURL: URL.documentsDirectory.appending(path: "data.json")
)
let container = try ModelContainer(
    for: Trip.self,
    configurations: config
)
```

### Optional Conformances

- **`DataStoreBatching`**: Implement `delete(_:)` for batch delete support.
- **`HistoryProviding`**: Implement `fetchHistory(_:)` and `deleteHistory(_:)`
  for change tracking.

### DataStoreError Cases

Handle these when implementing custom stores:

| Case | Meaning |
|------|---------|
| `.invalidPredicate` | Predicate cannot be evaluated by the store |
| `.preferInMemoryFilter` | Store cannot filter; framework filters in memory |
| `.preferInMemorySort` | Store cannot sort; framework sorts in memory |
| `.unsupportedFeature` | Store does not support the requested operation |

---

## History Tracking and Change Detection (iOS 18+)

### Enable History Tracking

Set the `author` property on `ModelContext` to tag changes with an identifier.
Mark attributes with `.preserveValueOnDeletion` to retain values in tombstones
after deletion.

```swift
@Model
class Trip {
    @Attribute(.preserveValueOnDeletion) var name: String
    @Attribute(.preserveValueOnDeletion) var destination: String
    var startDate: Date

    init(name: String, destination: String, startDate: Date) {
        self.name = name
        self.destination = destination
        self.startDate = startDate
    }
}

// Tag context for history attribution
modelContext.author = "mainApp"
```

### Fetch History Transactions

```swift
var descriptor = HistoryDescriptor<DefaultHistoryTransaction>()

// Filter by token (only new changes since last check)
if let lastToken = savedToken {
    descriptor.predicate = #Predicate<DefaultHistoryTransaction> { transaction in
        transaction.token > lastToken
    }
}

// iOS 26+: Sort by timestamp
descriptor.sortBy = [SortDescriptor(\.timestamp, order: .reverse)]

let transactions = try modelContext.fetchHistory(descriptor)

for transaction in transactions {
    for change in transaction.changes {
        switch change {
        case .insert(let insert):
            let insertedID = insert.changedPersistentIdentifier
            // Process new record

        case .update(let update):
            let updatedID = update.changedPersistentIdentifier
            let changedAttributes = update.updatedAttributes
            // Process modification

        case .delete(let delete):
            let deletedID = delete.changedPersistentIdentifier
            let tombstone = delete.tombstone
            // Access preserved values
            if let name = tombstone[\.name] as? String {
                // Use preserved name for sync/audit
            }
        }
    }

    // Save token for next incremental fetch
    savedToken = transaction.token
}
```

### Delete Stale History

```swift
let cutoffDate = Calendar.current.date(byAdding: .month, value: -3, to: .now)!
var descriptor = HistoryDescriptor<DefaultHistoryTransaction>()
descriptor.predicate = #Predicate<DefaultHistoryTransaction> { transaction in
    transaction.timestamp < cutoffDate
}
try modelContext.deleteHistory(descriptor)
```

### DefaultHistoryTransaction Properties

| Property | Type | Description |
|----------|------|-------------|
| `author` | `String?` | The context author that made the change |
| `changes` | `[HistoryChange]` | Insert, update, delete changes |
| `storeIdentifier` | `String` | Store that owns the transaction |
| `timestamp` | `Date` | When the transaction occurred |
| `token` | `DefaultHistoryToken` | Opaque token for incremental queries |
| `transactionIdentifier` | ... | Unique transaction ID |
| `bundleIdentifier` | `String` | Bundle that made the change |
| `processIdentifier` | `String` | Process that made the change |

### Cross-Process Change Detection

Use `bundleIdentifier` and `processIdentifier` to differentiate changes from
widgets, extensions, or the main app.

```swift
for transaction in transactions {
    if transaction.author == "widget" {
        // Handle widget-originated changes
    }
}
```

---

## CloudKit Integration

### Configuration Options

```swift
// Automatic: uses CloudKit entitlement from the app
let autoConfig = ModelConfiguration(
    cloudKitDatabase: .automatic
)

// Explicit private database
let privateConfig = ModelConfiguration(
    cloudKitDatabase: .private("iCloud.com.example.myapp")
)

// No CloudKit sync
let localConfig = ModelConfiguration(
    cloudKitDatabase: .none
)
```

### Setup Requirements

1. Enable iCloud capability in Xcode.
2. Add CloudKit entitlement (`com.apple.developer.icloud-services`).
3. Configure a CloudKit container identifier.
4. Enable Background Modes > Remote notifications.
5. Use the container identifier in `ModelConfiguration`.

### CloudKit-Compatible Model Design

```swift
@Model
class SyncedNote {
    // Keep required scalars nonoptional when defaults/initializers support them
    var title: String = ""
    var body: String?

    // Encrypt sensitive fields in CloudKit
    @Attribute(.allowsCloudEncryption) var secretContent: String?

    // Store large data externally
    @Attribute(.externalStorage) var attachment: Data?

    // Avoid .unique with CloudKit -- CloudKit does not enforce server-side uniqueness
    // Use @Attribute(.unique) only for local-only stores

    init(title: String? = nil, body: String? = nil) {
        self.title = title
        self.body = body
    }
}
```

### CloudKit Limitations

- **Unique constraints**: CloudKit does not enforce uniqueness server-side.
  Avoid `@Attribute(.unique)` and `#Unique` on CloudKit-synced models. Use
  `cloudKitDatabase: .none` for local-only stores that need uniqueness.
- **Relationships**: CloudKit requires optional relationships. Do not make every
  scalar optional just for CloudKit; keep required scalars when defaults,
  initializers, or migrations provide valid values.
- **Delete rules**: `.deny` is unsupported for CloudKit sync; enforce that
  invariant in app logic if needed.
- **Schema changes**: Initialize and verify the development schema in
  nonproduction builds, promote it before release, and treat production changes
  as additive-only.

### Multiple Stores: Local + Synced

```swift
let localConfig = ModelConfiguration(
    "Local",
    schema: Schema([DraftNote.self]),
    cloudKitDatabase: .none
)

let syncedConfig = ModelConfiguration(
    "Synced",
    schema: Schema([PublishedNote.self]),
    cloudKitDatabase: .private("iCloud.com.example.app")
)

let container = try ModelContainer(
    for: Schema([DraftNote.self, PublishedNote.self]),
    configurations: [localConfig, syncedConfig]
)
```

---

## Core Data Coexistence and Migration

Read `references/core-data-coexistence.md` when the task involves sharing an
existing Core Data store, adding SwiftData screens to a Core Data app, or
planning migration from Core Data to SwiftData. Keep standalone Core Data stack
guidance in the sibling `core-data` skill.

---
