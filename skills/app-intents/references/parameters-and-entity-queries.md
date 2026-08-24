# App Intents Parameters and Entity Queries

Extended App Intents patterns beyond the basics covered in the main skill.
Covers `@Parameter` variants, EntityPropertyQuery, assistant schemas, focus
filters, SiriKit migration, error handling, confirmation flows, authentication,
URL-representable types, and Spotlight indexing.

## `@Parameter` Initializer Variants

### 1. Basic (String, Bool, URL, Date)

```swift
@Parameter(title: "Name")
var name: String

@Parameter(title: "Name", description: "The user's full name")
var name: String

@Parameter(title: "Enabled", default: true)
var enabled: Bool

@Parameter(title: "Website")
var url: URL?
```

### 2. Numeric with Range and Control Style

```swift
@Parameter(title: "Volume", controlStyle: .slider, inclusiveRange: (0.0, 100.0))
var volume: Double

@Parameter(title: "Rating", controlStyle: .stepper, inclusiveRange: (1, 5))
var rating: Int

@Parameter(title: "Temperature", default: 72.0, inclusiveRange: (60.0, 90.0))
var temperature: Double
```

Numeric controls default to `.stepper`. `Int` supports `.stepper` and `.field`;
`Double` also supports `.slider`.

### 3. With Options Provider (Dynamic List)

Provide a dynamic set of options at runtime:

```swift
struct CategoryOptionsProvider: DynamicOptionsProvider {
    func results() async throws -> [String] {
        await CategoryStore.shared.allNames()
    }
}

@Parameter(title: "Category", optionsProvider: CategoryOptionsProvider())
var category: String
```

### 4. With Disambiguation Dialog

Request clarification when the system cannot resolve a value:

```swift
@Parameter(
    title: "Size",
    requestValueDialog: "What size would you like?",
    requestDisambiguationDialog: "Which size did you mean?"
)
var size: CupSize
```

### 5. With Resolvers

Transform raw input into the target type:

```swift
@Parameter(title: "Contact", resolvers: [ContactResolver()])
var contact: ContactEntity
```

### 6. Entity Parameter with Query

Specify one custom query for entity resolution when the entity's `defaultQuery`
is not the right search behavior:

```swift
@Parameter(title: "Trail", query: TrailStringQuery())
var trail: TrailEntity
```

### 7. Array Parameters

Use the current iOS 18+ `size:` overload when the system UI should enforce a
fixed or bounded number of entity values:

```swift
@Parameter(title: "Items", size: .init(exactly: 3))
var items: [ItemEntity]
```

Apple deprecated the original iOS 17 entity-array `size:` overloads, then added
replacement overloads in iOS 18. Do not treat the argument itself as deprecated.
Use `IntentCollectionSize(min:max:)` for a range, or omit `size:` only when the
system UI should allow an unconstrained array.

Validate the count again in `perform()` at the execution boundary:

```swift
guard items.count == 3 else {
    throw $items.needsValueError("Choose exactly three items.")
}
```

Apple references:

- [Current entity-array initializer with `size:` (iOS 18+)](https://sosumi.ai/documentation/appintents/intentparameter/init(title:description:default:size:inputconnectionbehavior:)-7i2i4)
- [`IntentCollectionSize`](https://sosumi.ai/documentation/appintents/intentcollectionsize)

### 8. File Parameters

```swift
@Parameter(title: "Document", supportedContentTypes: [.pdf, .plainText])
var document: IntentFile

@Parameter(title: "Image", supportedContentTypes: [.png, .jpeg])
var image: IntentFile?
```

### 9. Measurement Parameters

```swift
@Parameter(
    title: "Distance",
    defaultUnit: .miles,
    defaultUnitAdjustForLocale: true,
    supportsNegativeNumbers: false
)
var distance: Measurement<UnitLength>

@Parameter(title: "Weight", defaultUnit: .kilograms)
var weight: Measurement<UnitMass>

@Parameter(title: "Temperature", defaultUnit: .fahrenheit)
var temp: Measurement<UnitTemperature>
```

### 10. Input Connection Behavior

Control how parameters connect to Shortcuts input:

```swift
@Parameter(title: "Text", inputConnectionBehavior: .connectToPreviousIntentResult)
var text: String

@Parameter(title: "File", inputConnectionBehavior: .optionalIfProvided)
var file: IntentFile?
```

### Runtime Parameter Methods

Request values, disambiguation, and confirmation at runtime inside `perform()`:

```swift
func perform() async throws -> some IntentResult {
    // Request a missing value
    if quantity == nil {
        throw $quantity.needsValueError("How many would you like?")
    }

    // Disambiguate among options
    let resolved = try await $size.requestDisambiguation(
        among: [.small, .medium, .large],
        dialog: "Which size?"
    )

    // Confirm a value
    try await $amount.requestConfirmation(for: amount, dialog: "Charge \(amount)?")

    return .result()
}
```

## Dependent Options and Intentional Defaults

Use `@IntentParameterDependency` when an upstream intent parameter changes the
valid options for another parameter. It is available in iOS 17+ for
`DynamicOptionsProvider` implementations, including the `EntityQuery` family.

```swift
struct ConfigureProjectWidget: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Project"

    @Parameter(title: "Workspace")
    var workspace: WorkspaceEntity?

    @Parameter(title: "Project")
    var project: ProjectEntity?
}

struct ProjectQuery: EntityQuery {
    @IntentParameterDependency<ConfigureProjectWidget>(\.$workspace)
    private var configuration

    func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
        try await ProjectStore.shared.projects(identifiedBy: identifiers)
            .map(ProjectEntity.init)
    }

    func suggestedEntities() async throws -> [ProjectEntity] {
        guard let workspaceID = configuration?.workspace?.id else {
            return []
        }
        return try await ProjectStore.shared.projects(in: workspaceID)
            .map(ProjectEntity.init)
    }

    func defaultResult() async -> ProjectEntity? {
        guard let workspaceID = configuration?.workspace?.id else {
            return nil
        }
        return try? await ProjectStore.shared.recentProject(in: workspaceID)
            .map(ProjectEntity.init)
    }
}
```

The dependency can be `nil` while the system is asking for options before the
upstream value is configured. Handle that state deliberately: return an empty list,
or return a small unfiltered set only when those choices remain valid. Dependencies
may read multiple parameters when an option requires more than one parent choice.

`EntityQuery` inherits `defaultResult()` through `DynamicOptionsProvider`. Implement
it only when the app has a stable, helpful default such as a current workspace or a
recent project. Do not silently choose the first fetched entity merely to avoid an
unconfigured parameter.

Apple references:

- [`IntentParameterDependency`](https://sosumi.ai/documentation/appintents/intentparameterdependency)
- [`DynamicOptionsProvider`](https://sosumi.ai/documentation/appintents/dynamicoptionsprovider)

## EntityPropertyQuery (Filter and Sort)

The most powerful query variant. Declare filterable properties and sortable
fields for structured Siri and Shortcuts queries.

```swift
enum TrailComparator: Sendable {
    case nameContains(String)
    case nameEquals(String)
    case lengthGreaterThan(Measurement<UnitLength>)
    case lengthLessThan(Measurement<UnitLength>)
    case lengthEquals(Measurement<UnitLength>)
}

struct TrailPropertyQuery: EntityPropertyQuery {
    typealias ComparatorMappingType = TrailComparator

    static var properties = QueryProperties {
        Property(\TrailEntity.$name) {
            ContainsComparator { TrailComparator.nameContains($0) }
            EqualToComparator { TrailComparator.nameEquals($0) }
        }
        Property(\TrailEntity.$trailLength) {
            GreaterThanComparator { TrailComparator.lengthGreaterThan($0) }
            LessThanComparator { TrailComparator.lengthLessThan($0) }
            EqualToComparator { TrailComparator.lengthEquals($0) }
        }
    }

    static var sortingOptions = SortingOptions {
        SortableBy(\TrailEntity.$name)
        SortableBy(\TrailEntity.$trailLength)
    }

    func entities(
        matching comparators: [TrailComparator],
        mode: ComparatorMode,
        sortedBy: [EntityQuerySort<TrailEntity>],
        limit: Int?
    ) async throws -> [TrailEntity] {
        var results = TrailStore.shared.allTrails.map { TrailEntity(from: $0) }

        results = results.filter { trail in
            let matches = comparators.map { comparator in
                switch comparator {
                case .nameContains(let value):
                    trail.name.localizedCaseInsensitiveContains(value)
                case .nameEquals(let value):
                    trail.name.localizedStandardCompare(value) == .orderedSame
                case .lengthGreaterThan(let value):
                    trail.trailLength > value
                case .lengthLessThan(let value):
                    trail.trailLength < value
                case .lengthEquals(let value):
                    trail.trailLength == value
                }
            }
            guard !matches.isEmpty else { return true }
            return mode == .and ? matches.allSatisfy { $0 } : matches.contains(true)
        }

        if let limit {
            results = Array(results.prefix(limit))
        }

        return results
    }

    func entities(for identifiers: [Trail.ID]) async throws -> [TrailEntity] {
        TrailStore.shared.allTrails
            .filter { identifiers.contains($0.id) }
            .map { TrailEntity(from: $0) }
    }

    func suggestedEntities() async throws -> [TrailEntity] {
        TrailStore.shared.featured.map { TrailEntity(from: $0) }
    }
}
```

The comparator closures map user-supplied values into a query-specific
`ComparatorMappingType`; `entities(matching:)` receives those mapped values, not
raw `EntityQueryComparator` objects.

### Available comparators

| Comparator | Supported Types |
|---|---|
| `EqualToComparator` | Equatable properties |
| `NotEqualToComparator` | Equatable properties |
| `ContainsComparator` | Sequence properties |
| `HasPrefixComparator` | `String` |
| `HasSuffixComparator` | `String` |
| `GreaterThanComparator` | Comparable properties |
| `LessThanComparator` | Comparable properties |
| `GreaterThanOrEqualToComparator` | Comparable properties |
| `LessThanOrEqualToComparator` | Comparable properties |
| `IsBetweenComparator` | Comparable properties supported by Shortcuts |
