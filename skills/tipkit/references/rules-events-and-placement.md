# TipKit Rules, Events, and Placement

Complete implementation patterns for TipKit including custom styles, event-based
rules, tip groups, testing strategies, onboarding flows, and SwiftUI previews.
Examples target iOS 17+ with Swift 6.3 conventions unless a section explicitly
calls out a newer availability requirement.

## Availability Notes

- TipKit core APIs are iOS 17+.
- `TipGroup`, `.cloudKitContainer(...)`, and `MaxDisplayDuration` are iOS 18+.
- `resetEligibility()` is iOS 26+.
- `Tips.resetDatastore()` must run before `Tips.configure(_:)`.

## Complete Tip with Rules and Events

A full-featured tip combining parameter-based and event-based rules. The tip
appears only after the user has logged in and opened the app at least three
times, ensuring they are familiar with the basics before seeing advanced
feature discovery.

```swift
import TipKit

struct AdvancedSearchTip: Tip {
    // Parameter rule: user must be logged in
    @Parameter
    static var isLoggedIn: Bool = false

    // Event rule: user must have performed searches
    static let searchPerformed = Tips.Event(id: "searchPerformed")

    var title: Text {
        Text("Try Advanced Search")
    }

    var message: Text? {
        Text("Filter results by date, category, and location for faster discovery.")
    }

    var image: Image? {
        Image(systemName: "magnifyingglass")
    }

    // All rules must pass before the tip becomes eligible
    var rules: [Rule] {
        #Rule(Self.$isLoggedIn) { $0 == true }
        #Rule(Self.searchPerformed) { $0.donations.count >= 3 }
    }

    var options: [any TipOption] {
        MaxDisplayCount(5)
    }
}
```

### Donating to Events

Place event donations at the point where the user action occurs. Each
donation increments the internal counter that rules evaluate against.

```swift
struct SearchView: View {
    @State private var query = ""

    var body: some View {
        SearchBar(text: $query, onSubmit: {
            performSearch(query)
            // Donate each time the user searches
            AdvancedSearchTip.searchPerformed.sendDonation()
        })
    }
}
```

### Setting Parameters

Set parameter values when the relevant app state changes. Parameters persist
across launches via the TipKit datastore.

```swift
func handleLoginSuccess() {
    AdvancedSearchTip.isLoggedIn = true
}
```

## TipView and popoverTip Placement

### Inline TipView in a List

Place a `TipView` as a list row for contextual inline discovery. The tip
appears as part of the list content and animates away when dismissed or
invalidated.

```swift
struct ItemListView: View {
    let filterTip = FilterTip()
    @State private var items: [Item] = []

    var body: some View {
        List {
            TipView(filterTip)

            ForEach(items) { item in
                ItemRow(item: item)
            }
        }
        .navigationTitle("Items")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    showFilters()
                    filterTip.invalidate(reason: .actionPerformed)
                } label: {
                    Image(systemName: "line.3.horizontal.decrease.circle")
                }
                .popoverTip(filterTip, arrowEdge: .top)
            }
        }
    }
}
```

### Popover on Navigation Bar Button

Attach a popover tip to a toolbar button. The popover arrow points to the
button, drawing the user's attention to the exact control.

```swift
struct EditorView: View {
    let undoTip = UndoShortcutTip()

    var body: some View {
        TextEditor(text: $text)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button("Undo", systemImage: "arrow.uturn.backward") {
                        undoLastAction()
                        undoTip.invalidate(reason: .actionPerformed)
                    }
                    .popoverTip(undoTip, arrowEdge: .top)
                }
            }
    }
}
```

### Popover on Tab Bar Item

Use `popoverTip` on a `Tab` label view inside a `TabView` to highlight a
new tab.

```swift
struct MainTabView: View {
    let newTabTip = NewFeatureTabTip()

    var body: some View {
        TabView {
            Tab("Home", systemImage: "house") {
                HomeView()
            }

            Tab("Discover", systemImage: "sparkles") {
                DiscoverView()
            }
            .popoverTip(newTabTip)
        }
    }
}
```

## Event-Based Rule with Donation Counting

Track how many times the user performs an action, then show a tip suggesting
a more efficient alternative. This pattern is effective for progressive
disclosure: let users learn the basic workflow first, then reveal shortcuts.

```swift
struct KeyboardShortcutTip: Tip {
    static let manualSaveEvent = Tips.Event(id: "manualSave")

    var title: Text {
        Text("Save Faster with Command-S")
    }

    var message: Text? {
        Text("Press Command-S instead of using the menu to save your work instantly.")
    }

    var image: Image? {
        Image(systemName: "keyboard")
    }

    var rules: [Rule] {
        // Show after user has manually saved 5 times via button
        #Rule(Self.manualSaveEvent) { $0.donations.count >= 5 }
    }
}

struct DocumentView: View {
    let shortcutTip = KeyboardShortcutTip()

    var body: some View {
        VStack {
            TipView(shortcutTip)
            DocumentEditor(document: $document)
        }
        .toolbar {
            ToolbarItem {
                Button("Save") {
                    saveDocument()
                    KeyboardShortcutTip.manualSaveEvent.sendDonation()
                }
            }
        }
    }
}
```

### Event Donations with Associated Values

Attach a `DonationValue` to event donations for richer rule evaluation.
Use `Codable`-conforming types to provide context about each donation.

```swift
struct DetailedTip: Tip {
    struct DonationInfo: Codable, Sendable {
        let category: String
        let timestamp: Date
    }

    static let itemViewed = Tips.Event<DonationInfo>(id: "itemViewed")

    var rules: [Rule] {
        #Rule(Self.itemViewed) {
            $0.donations.filter {
                $0.category == "premium"
            }.count >= 3
        }
    }

    var title: Text { Text("Unlock Premium Content") }
}

// Donate with associated value
DetailedTip.itemViewed.sendDonation(
    DetailedTip.DonationInfo(category: "premium", timestamp: .now)
)
```
