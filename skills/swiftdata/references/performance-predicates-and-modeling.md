# SwiftData Performance, Predicates, and Modeling

Read this reference only when the task matches the sections below.

## Batch Operations and Performance

### Batch Enumeration

Process large result sets without loading all objects into memory:

```swift
try modelContext.enumerate(
    FetchDescriptor<Trip>(),
    batchSize: 5000,
    allowEscapingMutations: false
) { trip in
    trip.isProcessed = true
}
```

- `batchSize`: Number of objects loaded per batch (default 5000).
- `allowEscapingMutations`: Set to `true` only if mutations need to persist
  beyond the enumeration block.

### Batch Delete

```swift
try modelContext.delete(
    model: Trip.self,
    where: #Predicate { $0.isArchived == true },
    includeSubclasses: true  // iOS 26+ with inheritance
)
```

### Fetching Only Identifiers

When full objects are not needed (e.g., for counting or cross-actor references):

```swift
let ids = try modelContext.fetchIdentifiers(FetchDescriptor<Trip>())
```

### Fetch Count

```swift
let count = try modelContext.fetchCount(
    FetchDescriptor<Trip>(predicate: #Predicate { $0.isFavorite == true })
)
```

### Partial Property Fetch

Fetch only specific properties to reduce memory:

```swift
var descriptor = FetchDescriptor<Trip>()
descriptor.propertiesToFetch = [\.name, \.startDate]
let trips = try modelContext.fetch(descriptor)
```

### Relationship Prefetching

Avoid N+1 query problems by prefetching related objects:

```swift
var descriptor = FetchDescriptor<Trip>()
descriptor.relationshipKeyPathsForPrefetching = [\.accommodation, \.tags]
let trips = try modelContext.fetch(descriptor)
```

### Performance Tips

- Use `fetchLimit` and `fetchOffset` for pagination.
- Use `enumerate` instead of `fetch` for processing large datasets.
- Use `fetchCount` when only the count is needed.
- Use `fetchIdentifiers` when only IDs are needed.
- Use `propertiesToFetch` to limit loaded data.
- Use `@Attribute(.externalStorage)` for large `Data` payloads such as images
  and blobs.
- Disable `includePendingChanges` if unsaved data is not needed in results.
- Call `modelContext.save()` periodically during large imports to flush memory.

---

## Complex #Predicate Patterns

### Nested Collection Predicates

```swift
// Trips with at least one high-priority tag
#Predicate<Trip> { trip in
    trip.tags.contains { tag in
        tag.priority > 5
    }
}

// Trips where all items are packed
#Predicate<Trip> { trip in
    trip.packingList.allSatisfy { item in
        item.isPacked == true
    }
}
```

### Optional Chaining

```swift
// Trips with accommodation in a specific city
#Predicate<Trip> { trip in
    trip.accommodation?.city == "Paris"
}

// Nil coalescing
#Predicate<Trip> { trip in
    (trip.accommodation?.rating ?? 0) >= 4
}
```

### String Operations

```swift
// Case-insensitive search
#Predicate<Trip> { trip in
    trip.destination.localizedStandardContains(searchText)
}

// Prefix matching
#Predicate<Trip> { trip in
    trip.name.starts(with: "Summer")
}
```

### Date and Numeric Ranges

```swift
let startOfYear = Calendar.current.date(from: DateComponents(year: 2026, month: 1, day: 1))!
let endOfYear = Calendar.current.date(from: DateComponents(year: 2026, month: 12, day: 31))!

#Predicate<Trip> { trip in
    trip.startDate >= startOfYear && trip.startDate <= endOfYear
}

// Arithmetic
#Predicate<Trip> { trip in
    trip.budget - trip.spent > 100.0
}
```

### Ternary Expressions

```swift
#Predicate<Trip> { trip in
    (trip.isFavorite ? trip.name : trip.destination).localizedStandardContains(searchText)
}
```

### Combining Multiple Predicates

Build predicates incrementally using captured variables:

```swift
func buildPredicate(
    searchText: String,
    onlyFavorites: Bool,
    minDate: Date?
) -> Predicate<Trip> {
    #Predicate<Trip> { trip in
        (searchText.isEmpty || trip.name.localizedStandardContains(searchText))
        && (!onlyFavorites || trip.isFavorite == true)
        && (minDate == nil || trip.startDate >= (minDate ?? .distantPast))
    }
}
```

### Type Casting in Predicates (iOS 26+, with Inheritance)

```swift
// Filter for business trips only
#Predicate<Trip> { trip in
    trip is BusinessTrip
}
```

---

## Composite Attributes and Codable Values

Compatible `Codable` structs can be represented as composite attributes in the
SwiftData schema. Current Apple docs expose `Schema.CompositeAttribute` on
iOS 17+, while the explicit `@Attribute(.codable)` option is iOS 27 beta.
Do not describe `Codable` value storage as an iOS 18-only feature.

```swift
struct Address: Codable {
    var street: String
    var city: String
    var state: String
    var zip: String
}

@Model
class Person {
    var name: String
    var homeAddress: Address   // Stored as composite attribute
    var workAddress: Address?

    init(name: String, homeAddress: Address) {
        self.name = name
        self.homeAddress = homeAddress
    }
}
```

Composite attributes appear as `Schema.CompositeAttribute` in the schema.
Sub-properties are stored inline in the same table. Query individual fields
via key-path navigation in `#Predicate`:

```swift
#Predicate<Person> { person in
    person.homeAddress.city == "San Francisco"
}
```

---

## Model Inheritance (iOS 26+)

### Base and Subclass Pattern

```swift
@Model
class Trip {
    var name: String
    var destination: String
    var startDate: Date
    var endDate: Date

    init(name: String, destination: String, startDate: Date, endDate: Date) {
        self.name = name
        self.destination = destination
        self.startDate = startDate
        self.endDate = endDate
    }
}

@Model
class PersonalTrip: Trip {
    var companion: String?
}

@Model
class BusinessTrip: Trip {
    var company: String
    var expenseReport: Data?

    init(name: String, destination: String, startDate: Date, endDate: Date,
         company: String) {
        self.company = company
        super.init(name: name, destination: destination,
                   startDate: startDate, endDate: endDate)
    }
}
```

### Querying with Inheritance

```swift
// Fetch all trips (includes PersonalTrip and BusinessTrip)
let allTrips = try modelContext.fetch(FetchDescriptor<Trip>())

// Fetch only business trips
let businessTrips = try modelContext.fetch(FetchDescriptor<BusinessTrip>())

// Delete with subclass inclusion
try modelContext.delete(
    model: Trip.self,
    where: #Predicate { $0.destination == "Cancelled" },
    includeSubclasses: true
)
```

### Container Registration

Register the base class; subclasses are included automatically:

```swift
let container = try ModelContainer(for: Trip.self)
// PersonalTrip and BusinessTrip are included via inheritance
```

---
