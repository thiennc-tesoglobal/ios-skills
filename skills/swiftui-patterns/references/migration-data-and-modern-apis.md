# SwiftUI Data and Modern API Migrations

Read this reference only when the task matches the sections below.

## List Row Actions with EditButton, .onDelete, .onMove, and .swipeActions

### Basic Edit Mode Pattern

```swift
struct ItemList: View {
    @State private var items = ["A", "B", "C"]

    var body: some View {
        NavigationView {
            List {
                ForEach(items, id: \.self) { item in
                    Text(item)
                }
                .onDelete { items.remove(atOffsets: $0) }
                .onMove { items.move(fromOffsets: $0, toOffset: $1) }
            }
            .navigationTitle("Items")
            .toolbar { EditButton() }
        }
    }
}
```

### Contextual Swipe Actions

```swift
struct ItemList: View {
    @State private var items = ["A", "B", "C"]

    var body: some View {
        NavigationStack {
            List {
                ForEach(items, id: \.self) { item in
                    Text(item)
                        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                            Button("Delete", role: .destructive) {
                                if let index = items.firstIndex(of: item) {
                                    items.remove(at: index)
                                }
                            }
                        }
                        .swipeActions(edge: .leading) {
                            Button("Pin", systemImage: "pin") {
                                pinItem(item)
                            }
                            .tint(.orange)
                        }
                }
                .onMove { items.move(fromOffsets: $0, toOffset: $1) }
            }
            .navigationTitle("Items")
            .toolbar { EditButton() }
        }
    }
}
```

### Migration Notes

`.swipeActions` (iOS 15+) gives you per-row, multi-action swipe menus with custom tints and roles. `EditButton`, `.onDelete`, and `.onMove` remain valid for edit mode and reordering. Prefer `.swipeActions` when the desired interaction is a contextual row action, and keep edit mode when users need batch delete or reorder workflows.

---

## UIApplication.shared.open to `@Environment(\.openURL)`

### Before (App-Coupled Pattern)

```swift
Button("Open Website") {
    if let url = URL(string: "https://example.com") {
        UIApplication.shared.open(url)
    }
}
```

### After (Modern)

```swift
struct LinkButton: View {
    @Environment(\.openURL) private var openURL

    var body: some View {
        Button("Open Website") {
            openURL(URL(string: "https://example.com")!)
        }
    }
}
```

With a completion handler:

```swift
openURL(url) { accepted in
    if !accepted {
        // handle failure to open URL
    }
}
```

### Migration Notes

`@Environment(\.openURL)` works on all Apple platforms, not just iOS. It can be overridden in the environment for testing or to intercept URL opens. Avoid reaching for `UIApplication.shared` in SwiftUI views.

---

## `@FetchRequest` to `@Query` (SwiftData)

Core Data's `@FetchRequest` is superseded by SwiftData's `@Query` macro when you migrate to SwiftData models.

### Before (Core Data)

```swift
struct ItemListView: View {
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \CDItem.timestamp, ascending: false)],
        predicate: NSPredicate(format: "isCompleted == NO")
    ) private var items: FetchedResults<CDItem>

    var body: some View {
        List(items) { item in
            Text(item.title ?? "")
        }
    }
}
```

### After (SwiftData)

```swift
struct ItemListView: View {
    @Query(
        filter: #Predicate<Item> { !$0.isCompleted },
        sort: \.timestamp,
        order: .reverse
    ) private var items: [Item]

    var body: some View {
        List(items) { item in
            Text(item.title)
        }
    }
}
```

### Migration Notes

`@Query` uses type-safe `#Predicate` instead of string-based `NSPredicate`. Sort descriptors use key paths directly. The model container is injected via `.modelContainer(for:)` on an ancestor view. SwiftData models are plain Swift classes with the `@Model` macro rather than NSManagedObject subclasses.

---

## Opaque return types to some/any clarifications (Swift 5.7+)

### Before

```swift
func makeView() -> AnyView {
    AnyView(Text("Hello"))
}

protocol DataSource {
    func fetch() -> AnyPublisher<[Item], Error>
}
```

### After (Modern)

```swift
func makeView() -> some View {
    Text("Hello")
}

protocol DataSource {
    func fetch() async throws -> [Item]
}

// When you need a protocol-typed variable:
let source: any DataSource = RemoteDataSource()
```

### Migration Notes

Use `some` for opaque return types when the concrete type is fixed. Use `any` for existentials when you need to store heterogeneous conformances. Prefer `async throws` over Combine publishers for new code. Swift 5.7+ allows `some` in parameter position too:

```swift
func display(_ view: some View) { ... }
```

---

## .sheet(item:) with Optional Identifiable to Modern Pattern

### Before (Fragile Pattern)

```swift
@State private var selectedItem: Item?
@State private var showingSheet = false

Button {
    selectedItem = item
    showingSheet = true
} label: {
    ItemRow(item: item)
}
.buttonStyle(.plain)
.sheet(isPresented: $showingSheet) {
    if let item = selectedItem {
        DetailView(item: item)
    }
}
```

### After (Modern)

```swift
@State private var selectedItem: Item?

Button {
    selectedItem = item
} label: {
    ItemRow(item: item)
}
.buttonStyle(.plain)
.sheet(item: $selectedItem) { item in
    DetailView(item: item)
}
```

### Migration Notes

Using `.sheet(item:)` eliminates the dual-state problem where `showingSheet` and `selectedItem` can become out of sync. The sheet presents when the binding becomes non-nil and dismisses when it becomes nil. The unwrapped value is passed directly into the closure.

---

## Resolving SwiftUI Color for Interop (iOS 17+)

### Before

```swift
let color = UIColor.link
let swiftUIColor = Color(uiColor: color)
```

### After (Modern)

`Color(uiColor:)` is still valid when bridging an existing UIKit color. For concrete RGBA values from SwiftUI colors, resolve the color in the current environment:

```swift
// Custom colors via asset catalogs (always preferred)
let brand = Color("BrandBlue")

// Resolved colors for interop (iOS 17+)
@Environment(\.self) var environment

let resolved = Color.blue.resolve(in: environment)
// resolved.red, resolved.green, resolved.blue, resolved.opacity
```

### Migration Notes

`Color.resolve(in:)` (iOS 17+) gives you concrete RGBA values in the current environment. Use it for custom runtime color manipulations or lower-level interop. For static brand colors, use asset catalogs; for UIKit colors you already have, keep `Color(uiColor:)`.

---

## ForEach with Range to ForEach with Identifiable / indices

### Before (Fragile Pattern)

```swift
ForEach(0..<items.count) { index in
    Text(items[index].name)
}
```

### After (Modern)

```swift
// Identifiable models
ForEach(items) { item in
    Text(item.name)
}

// When you need the index
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
    Text("\(index + 1). \(item.name)")
}

// Subranges with bindable access
ForEach($items) { $item in
    TextField("Name", text: $item.name)
}
```

### Migration Notes

Constant-range `ForEach(0..<n)` is only safe when the range never changes. For dynamic data, always use identifiable collections. `ForEach($items)` provides direct bindings to each element without index arithmetic.

---

## Toolbar Placement Names (iOS 16+)

### Before

```swift
.toolbar {
    ToolbarItem(placement: .navigationBarLeading) {
        Button("Back") { dismiss() }
    }
    ToolbarItem(placement: .navigationBarTrailing) {
        Button("Edit") { isEditing.toggle() }
    }
    ToolbarItem(placement: .bottomBar) {
        Button("Add") { addItem() }
    }
}
```

### After (Modern)

```swift
.toolbar {
    ToolbarItem(placement: .topBarLeading) {
        Button("Back") { dismiss() }
    }
    ToolbarItem(placement: .topBarTrailing) {
        Button("Edit") { isEditing.toggle() }
    }
    ToolbarItem(placement: .bottomBar) {
        Button("Add") { addItem() }
    }
}
```

### Migration Notes

Prefer `.topBarLeading` and `.topBarTrailing` (iOS 16+) in modern `NavigationStack` and `NavigationSplitView` contexts. The names describe placement without tying the item to a specific navigation-bar implementation.

---

## cornerRadius to clipShape(.rect(cornerRadius:))

`.cornerRadius(_:)` was deprecated in iOS 17.

### Before (Deprecated)

```swift
RoundedRectangle(cornerRadius: 12)
    .cornerRadius(12)

Image("photo")
    .cornerRadius(8)
```

### After (Modern)

```swift
RoundedRectangle(cornerRadius: 12)
    .clipShape(.rect(cornerRadius: 12))

Image("photo")
    .clipShape(.rect(cornerRadius: 8))
```

### Migration Notes

`clipShape(.rect(cornerRadius:))` uses `RoundedRectangle` under the hood and also supports `cornerRadii` for per-corner control (iOS 16+):

```swift
.clipShape(.rect(cornerRadii: .init(topLeading: 12, bottomTrailing: 12)))
```

---

## tabItem to Tab (iOS 18+)

The `tabItem` modifier approach was superseded by the `Tab` type inside `TabView` (iOS 18+).

### Before (Legacy)

```swift
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }
    SettingsView()
        .tabItem {
            Label("Settings", systemImage: "gear")
        }
}
```

### After (Modern — iOS 18+)

```swift
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }
    Tab("Settings", systemImage: "gear") {
        SettingsView()
    }
}
```

### Migration Notes

`Tab` provides a cleaner API and is required for the new tab sidebar on iPadOS 18+. The `tabItem` modifier still works but does not support the sidebar presentation. Use `Tab` with a `value` parameter and `@State` selection for programmatic tab switching. `TabSection` groups tabs in the sidebar.

---

## scrollIndicators(.hidden) Replaces showsIndicators Parameter

The `showsIndicators` parameter on `ScrollView` is available but the `scrollIndicators` modifier (iOS 16+) is preferred for consistency.

### Before

```swift
ScrollView(.vertical, showsIndicators: false) {
    content
}
```

### After (Modern)

```swift
ScrollView {
    content
}
.scrollIndicators(.hidden)
```

### Migration Notes

`.scrollIndicators(_:axes:)` accepts `.automatic`, `.visible`, `.hidden`, and `.never`. It also works on `List` and `TextEditor`. The `axes` parameter lets you control horizontal and vertical indicators independently.
