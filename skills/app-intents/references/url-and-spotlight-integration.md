# App Intents URL and Spotlight Integration

Read this reference only when the task matches the sections below.

## URLRepresentableIntent / Entity / Enum (iOS 18+)

Represent intents, entities, and enums as URLs for deep linking.

### URLRepresentableIntent

```swift
struct OpenRecipeIntent: URLRepresentableIntent {
    static var title: LocalizedStringResource = "Open Recipe"

    @Parameter(title: "Recipe")
    var target: RecipeEntity

    static var parameterSummary: some ParameterSummary {
        Summary("Open \(\.$target)")
    }

    func perform() async throws -> some IntentResult & OpensIntent {
        return .result()
    }
}

extension OpenRecipeIntent {
    static var urlRepresentation: URLRepresentation {
        "https://myapp.com/recipes/\(\.$target)"
    }
}
```

### URLRepresentableEntity

```swift
struct RecipeEntity: URLRepresentableEntity {
    // ... standard AppEntity members ...

    static var urlRepresentation: URLRepresentation {
        "https://myapp.com/recipes/\(.id)"
    }
}
```

### URLRepresentableEnum

```swift
enum RecipeCategory: String, URLRepresentableEnum {
    case breakfast, lunch, dinner

    static var urlRepresentation: URLRepresentation {
        "https://myapp.com/category/\(.rawValue)"
    }

    // ... standard AppEnum members ...
}
```

URL representations must be universal links, not custom URL schemes.

## IndexedEntity for Spotlight (iOS 18+)

Conform to `IndexedEntity` to make entities searchable in Spotlight.

```swift
struct ArticleEntity: IndexedEntity {
    static let defaultQuery = ArticleQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Article"

    var id: String

    @Property(title: "Title")
    var title: String

    @Property(title: "Author")
    var author: String

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)", subtitle: "\(author)")
    }

    // Start with defaultAttributeSet to keep displayRepresentation metadata
    var attributeSet: CSSearchableItemAttributeSet {
        let attrs = defaultAttributeSet
        attrs.authorNames = [author]
        return attrs
    }
}
```

After creating entities, add instances to a named Spotlight index:

```swift
try await CSSearchableIndex(name: "Articles").indexAppEntities(articleEntities)
```

If you return a fresh `CSSearchableItemAttributeSet` from `attributeSet`, add
the contents of `defaultAttributeSet` yourself when you still need the title,
subtitle, or image from `displayRepresentation`.

If your app already creates `CSSearchableItem` values, call
`associateAppEntity(_:priority:)` on the item's attribute set and provide an
`OpenIntent` for the entity type so Spotlight results can open the right app
content.

### Hide specific entities from Spotlight UI

```swift
extension ArticleEntity {
    var hideInSpotlight: Bool {
        isDraft  // Draft articles should not appear in search
    }
}
```

## `@ComputedProperty(indexingKey:)` for Spotlight (iOS 26+)

Use indexing keys on `@Property` and `@ComputedProperty` for structured
Spotlight metadata. The value is a Swift key path into
`CSSearchableItemAttributeSet`.

```swift
struct RecipeEntity: IndexedEntity {
    static let defaultQuery = RecipeQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Recipe"

    var id: String

    @Property(title: "Name", indexingKey: \.title)
    var name: String

    @Property(title: "Cuisine")
    var cuisine: String

    @ComputedProperty(indexingKey: \.contentDescription)
    var summary: String {
        "\(name) -- \(cuisine) cuisine"
    }

    @ComputedProperty(indexingKey: \.thumbnailURL)
    var imageURL: URL? {
        URL(string: "https://myapp.com/images/\(id).jpg")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)", subtitle: "\(cuisine)")
    }
}
```

```swift
// Avoid duplicating a wrapped property's indexing key in attributeSet
struct RecipeEntity: IndexedEntity {
    @Property(title: "Name", indexingKey: \.title)
    var name: String

    var attributeSet: CSSearchableItemAttributeSet {
        let attrs = CSSearchableItemAttributeSet(contentType: .text)
        attrs.title = name  // Redundant: @Property already supplies this key
        return attrs
    }
}

// Prefer indexingKey for metadata already exposed on the entity
struct RecipeEntity: IndexedEntity {
    @Property(title: "Name", indexingKey: \.title)
    var name: String
}
```

### Available indexing keys

| Key | Property Type | Purpose |
|---|---|---|
| `\.title` | `String` | Primary searchable title |
| `\.contentDescription` | `String` | Detailed description |
| `\.thumbnailURL` | `URL?` | Thumbnail image |
| `\.keywords` | `[String]` | Additional search terms |
| `\.contentURL` | `URL?` | Content location |

## Onscreen Content for Siri (iOS 26+)

Make onscreen content available to Siri and Apple Intelligence without an
assistant schema:

```swift
struct ArticleEntity: AppEntity, Transferable {
    // Standard AppEntity conformance...

    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .article)
    }
}

// In your view controller or SwiftUI view:
let activity = NSUserActivity(activityType: "com.myapp.article")
activity.appEntityIdentifier = AppEntityIdentifier(article)
// Set as current activity
```

## Parameter Summary Builder

Use `When`, `Switch`, `Case`, and `DefaultCase` for conditional parameter
summaries that change based on parameter values:

```swift
struct ConfigureWidgetIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Configure Widget"

    @Parameter(title: "Style")
    var style: WidgetStyle

    @Parameter(title: "Show Details", default: false)
    var showDetails: Bool

    @Parameter(title: "Refresh Interval", default: .hourly)
    var interval: RefreshInterval

    static var parameterSummary: some ParameterSummary {
        When(\.$showDetails, .equalTo, true) {
            Summary("Show \(\.$style) widget") {
                \.$showDetails
                \.$interval
            }
        } otherwise: {
            Summary("Show \(\.$style) widget") {
                \.$showDetails
            }
        }
    }
}
```

### Switch/Case for multiple conditions

```swift
static var parameterSummary: some ParameterSummary {
    Switch(\.$style) {
        Case(.compact) {
            Summary("Compact widget")
        }
        Case(.detailed) {
            Summary("Detailed widget") {
                \.$interval
            }
        }
        DefaultCase {
            Summary("Widget") {
                \.$style
            }
        }
    }
}
```

## Core Spotlight Direct Usage

Use Core Spotlight directly when you need full control over indexing without
adopting App Intents, or when targeting iOS versions before IndexedEntity
(pre-iOS 18). For apps already using App Intents, prefer `IndexedEntity`
(iOS 18+) plus `@Property(indexingKey:)` / `@ComputedProperty(indexingKey:)`
(iOS 26+) where possible.

### When to Use Core Spotlight Directly vs IndexedEntity

| Approach | When to Use |
|---|---|
| `IndexedEntity` (iOS 18+) | App already uses App Intents; entities are also Siri/Shortcuts-visible |
| `@ComputedProperty(indexingKey:)` (iOS 26+) | Adds derived metadata to an `IndexedEntity` |
| Core Spotlight directly | No App Intents adoption; pre-iOS 18 targets; standalone indexing; fine-grained control over expiration, domain grouping, or batch operations |

### CSSearchableItem and CSSearchableItemAttributeSet

A `CSSearchableItem` uniquely identifies searchable content. Attach a
`CSSearchableItemAttributeSet` to describe the item's metadata.

Docs: [CSSearchableItem](https://sosumi.ai/documentation/corespotlight/cssearchableitem),
[CSSearchableItemAttributeSet](https://sosumi.ai/documentation/corespotlight/cssearchableitemattributeset)

```swift
import CoreSpotlight
import UniformTypeIdentifiers

func makeSearchableItem(
    id: String,
    title: String,
    description: String,
    thumbnailData: Data? = nil
) -> CSSearchableItem {
    let attributes = CSSearchableItemAttributeSet(contentType: .text)
    attributes.title = title
    attributes.contentDescription = description
    attributes.thumbnailData = thumbnailData

    // Optional: improve search ranking and categorization
    attributes.keywords = ["recipe", "cooking"]
    attributes.displayName = title
    attributes.contentURL = URL(string: "myapp://recipes/\(id)")

    let item = CSSearchableItem(
        uniqueIdentifier: id,
        domainIdentifier: "com.myapp.recipes",
        attributeSet: attributes
    )
    // Set an expiration date when the default automatic expiration is wrong
    item.expirationDate = Date.now.addingTimeInterval(60 * 60 * 24 * 90)
    return item
}
```

### CSSearchableIndex — Indexing and Deletion

Use `CSSearchableIndex` to add, update, and remove items. Use a named index in
production, and add a protection class when indexing sensitive content. Reserve
`default()` for prototyping and testing.

Docs: [CSSearchableIndex](https://sosumi.ai/documentation/corespotlight/cssearchableindex)

```swift
import CoreSpotlight

// Index a single item (add or update)
func indexItem(_ item: CSSearchableItem) async throws {
    let index = CSSearchableIndex(name: "recipes")
    try await index.indexSearchableItems([item])
}

// Delete specific items by identifier
func deleteItems(identifiers: [String]) async throws {
    let index = CSSearchableIndex(name: "recipes")
    try await index.deleteSearchableItems(
        withIdentifiers: identifiers
    )
}

// Delete all items in a domain (e.g., after user deletes a category)
func deleteItemsInDomain(_ domain: String) async throws {
    let index = CSSearchableIndex(name: "recipes")
    try await index.deleteSearchableItems(
        withDomainIdentifiers: [domain]
    )
}

// Delete everything (e.g., on logout)
func deleteAllItems() async throws {
    let index = CSSearchableIndex(name: "recipes")
    try await index.deleteAllSearchableItems()
}
```

### Batch Indexing Patterns

For large data sets, index in batches to minimize memory pressure and handle
errors gracefully. Use `beginBatch()` / `endBatch(withClientState:)` to
track progress and resume after crashes.

```swift
import CoreSpotlight

func batchIndexRecipes(_ recipes: [Recipe]) async throws {
    let index = CSSearchableIndex(name: "recipes")

    // Simple batched approach -- chunk into groups
    let batchSize = 100
    for batch in stride(from: 0, to: recipes.count, by: batchSize) {
        let end = min(batch + batchSize, recipes.count)
        let items = recipes[batch..<end].map { recipe in
            makeSearchableItem(
                id: recipe.id,
                title: recipe.name,
                description: recipe.summary,
                thumbnailData: recipe.thumbnailData
            )
        }
        try await index.indexSearchableItems(items)
    }
}

// Client-state-based batching for crash recovery
func batchIndexWithState(_ recipes: [Recipe]) async throws {
    let index = CSSearchableIndex(name: "recipes")

    // Check where we left off
    let lastState = try? await index.fetchLastClientState()
    let startOffset = lastState
        .flatMap { String(data: $0, encoding: .utf8) }
        .flatMap(Int.init) ?? 0

    let batchSize = 100
    for batch in stride(from: startOffset, to: recipes.count, by: batchSize) {
        let end = min(batch + batchSize, recipes.count)
        let items = recipes[batch..<end].map { recipe in
            makeSearchableItem(
                id: recipe.id,
                title: recipe.name,
                description: recipe.summary
            )
        }

        index.beginBatch()
        try await index.indexSearchableItems(items)

        let stateData = "\(end)".data(using: .utf8)!
        try await index.endBatch(withClientState: stateData)
    }
}
```

### Protected Index for Sensitive Content

Use a named index with a data protection class to encrypt indexed content:

```swift
let protectedIndex = CSSearchableIndex(
    name: "secure-notes",
    protectionClass: .complete  // Only accessible when device is unlocked
)

try await protectedIndex.indexSearchableItems(sensitiveItems)
```

### Handling Search Results (NSUserActivity)

When a user taps a Spotlight result, the system delivers an `NSUserActivity`
with `activityType` set to `CSSearchableItemActionType`. Extract the item
identifier from `userInfo` to navigate to the correct content.

```swift
import CoreSpotlight
import UIKit

// UIKit: In AppDelegate or SceneDelegate
func application(
    _ application: UIApplication,
    continue userActivity: NSUserActivity,
    restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
) -> Bool {
    if userActivity.activityType == CSSearchableItemActionType,
       let identifier = userActivity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
        navigateToItem(withIdentifier: identifier)
        return true
    }
    return false
}

// SwiftUI: Use onContinueUserActivity
struct ContentView: View {
    var body: some View {
        NavigationStack {
            RecipeListView()
        }
        .onContinueUserActivity(CSSearchableItemActionType) { activity in
            if let id = activity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
                navigateToRecipe(id: id)
            }
        }
    }
}
```

### Query Continuation

When a user taps "Search in App" from Spotlight, handle the query string:

```swift
// activityType == CSQueryContinuationActionType
.onContinueUserActivity(CSQueryContinuationActionType) { activity in
    if let query = activity.userInfo?[CSSearchQueryString] as? String {
        searchViewModel.searchText = query
    }
}
```
