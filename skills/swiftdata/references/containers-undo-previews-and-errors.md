# SwiftData Containers, Undo, Previews, and Errors

Read this reference only when the task matches the sections below.

## Multiple ModelContainer Configurations

### Separate Stores for Different Data

```swift
// Local-only data (no sync)
let localConfig = ModelConfiguration(
    "Local",
    schema: Schema([AppSettings.self, CacheEntry.self]),
    isStoredInMemoryOnly: false,
    cloudKitDatabase: .none
)

// Synced data
let syncConfig = ModelConfiguration(
    "Synced",
    schema: Schema([UserDocument.self, SharedNote.self]),
    cloudKitDatabase: .private("iCloud.com.example.app")
)

let container = try ModelContainer(
    for: Schema([AppSettings.self, CacheEntry.self, UserDocument.self, SharedNote.self]),
    configurations: [localConfig, syncConfig]
)
```

### Read-Only Bundled Database

```swift
let bundledURL = Bundle.main.url(forResource: "seed", withExtension: "store")!
let readOnlyConfig = ModelConfiguration(
    "SeedData",
    schema: Schema([ReferenceItem.self]),
    url: bundledURL,
    allowsSave: false
)
```

### App Group Sharing (Widget / Extension)

```swift
let sharedConfig = ModelConfiguration(
    groupContainer: .identifier("group.com.example.myapp")
)
let container = try ModelContainer(for: Trip.self, configurations: sharedConfig)
```

---

## Undo/Redo Support

### Setup

```swift
let context = ModelContext(container)
context.undoManager = UndoManager()
```

### SwiftUI Integration

```swift
@main
struct MyApp: App {
    let container: ModelContainer

    init() {
        do {
            container = try ModelContainer(for: Trip.self)
            container.mainContext.undoManager = UndoManager()
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

### Using Undo/Redo

```swift
struct TripEditorView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.undoManager) private var undoManager

    var body: some View {
        VStack {
            // ... editing UI ...
        }
        .toolbar {
            ToolbarItemGroup {
                Button("Undo") {
                    modelContext.undoManager?.undo()
                }
                .disabled(!(modelContext.undoManager?.canUndo ?? false))

                Button("Redo") {
                    modelContext.undoManager?.redo()
                }
                .disabled(!(modelContext.undoManager?.canRedo ?? false))
            }
        }
        .onAppear {
            modelContext.undoManager = undoManager
        }
    }
}
```

Process pending changes to register undo actions:

```swift
modelContext.insert(trip)
modelContext.processPendingChanges()
// Now undo is available for the insertion
```

---

## Preview Patterns with In-Memory Stores

### Basic Preview Container

```swift
@MainActor
let previewContainer: ModelContainer = {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try! ModelContainer(for: Trip.self, configurations: config)

    // Seed sample data
    let sampleTrips = [
        Trip(name: "Summer in Paris", destination: "Paris",
             startDate: .now, endDate: .now.addingTimeInterval(86400 * 7)),
        Trip(name: "Tokyo Adventure", destination: "Tokyo",
             startDate: .now.addingTimeInterval(86400 * 30),
             endDate: .now.addingTimeInterval(86400 * 37)),
    ]
    for trip in sampleTrips {
        container.mainContext.insert(trip)
    }

    return container
}()

#Preview {
    TripListView()
        .modelContainer(previewContainer)
}
```

### Preview with Relationships

```swift
#Preview {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try! ModelContainer(
        for: Trip.self, LivingAccommodation.self,
        configurations: config
    )

    let trip = Trip(name: "Beach Trip", destination: "Malibu",
                    startDate: .now, endDate: .now.addingTimeInterval(86400 * 3))
    let hotel = LivingAccommodation(name: "Beach Resort")
    trip.accommodation = hotel

    container.mainContext.insert(trip)

    return TripDetailView(trip: trip)
        .modelContainer(container)
}
```

### Preview Trait (iOS 18+)

Use `PreviewModifier` for reusable preview configurations:

```swift
struct SampleDataPreview: PreviewModifier {
    static func makeSharedContext() async throws -> ModelContainer {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: Trip.self, configurations: config)
        // Insert sample data
        return container
    }

    func body(content: Content, context: ModelContainer) -> some View {
        content.modelContainer(context)
    }
}

extension PreviewTrait where T == Preview.ViewTraits {
    static var sampleData: Self = .modifier(SampleDataPreview())
}

#Preview(traits: .sampleData) {
    TripListView()
}
```

---

## Notification Observation

### Observing Save Events

```swift
NotificationCenter.default.publisher(for: ModelContext.didSave, object: modelContext)
    .sink { notification in
        if let insertedIDs = notification.userInfo?[
            ModelContext.NotificationKey.insertedIdentifiers
        ] as? Set<PersistentIdentifier> {
            // Handle new insertions
        }

        if let updatedIDs = notification.userInfo?[
            ModelContext.NotificationKey.updatedIdentifiers
        ] as? Set<PersistentIdentifier> {
            // Handle updates
        }

        if let deletedIDs = notification.userInfo?[
            ModelContext.NotificationKey.deletedIdentifiers
        ] as? Set<PersistentIdentifier> {
            // Handle deletions
        }
    }
```

### Available Notification Keys

| Key | Description |
|-----|-------------|
| `.insertedIdentifiers` | IDs of newly inserted models |
| `.updatedIdentifiers` | IDs of updated models |
| `.deletedIdentifiers` | IDs of deleted models |
| `.invalidatedAllIdentifiers` | All data invalidated (e.g., store reset) |
| `.queryGeneration` | Query generation token |

---

## Error Handling

### SwiftDataError Cases

```swift
do {
    let trips = try modelContext.fetch(descriptor)
} catch let error as SwiftDataError {
    switch error {
    case SwiftDataError.unsupportedPredicate:
        // Predicate uses unsupported operations
    case SwiftDataError.unsupportedSortDescriptor:
        // Sort descriptor cannot be processed
    case SwiftDataError.modelValidationFailure:
        // Model fails validation (e.g., unique constraint)
    case SwiftDataError.loadIssueModelContainer:
        // Container could not load the store
    default:
        // Handle other SwiftData errors
    }
} catch {
    // Handle non-SwiftData errors
}
```

### Common Error Categories

| Category | Errors |
|----------|--------|
| Fetch | `.unsupportedPredicate`, `.unsupportedSortDescriptor`, `.unsupportedKeyPath`, `.includePendingChangesWithBatchSize` |
| Configuration | `.duplicateConfiguration`, `.configurationFileNameContainsInvalidCharacters`, `.configurationSchemaNotFoundInContainerSchema` |
| Container | `.loadIssueModelContainer` |
| Context | `.modelValidationFailure`, `.missingModelContext` |
| Migration | `.backwardMigration`, `.unknownSchema` |
| History (iOS 18+) | `.historyTokenExpired`, `.invalidTransactionFetchRequest` |
