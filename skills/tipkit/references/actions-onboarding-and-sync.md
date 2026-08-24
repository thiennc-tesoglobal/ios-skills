# TipKit Actions, Onboarding, and Sync

Read this reference only when the task matches the sections below.

## Tip with Action Buttons

Add action buttons that deep-link to a feature. Invalidate the tip when
the user taps the primary action.

```swift
struct NewEditorTip: Tip {
    var title: Text {
        Text("Try the New Editor")
    }

    var message: Text? {
        Text("A faster, more powerful editing experience awaits.")
    }

    var image: Image? {
        Image(systemName: "pencil.and.outline")
    }

    var actions: [Action] {
        Action(id: "open-editor", title: "Open Editor")
        Action(id: "later", title: "Maybe Later")
    }
}

struct HomeView: View {
    let editorTip = NewEditorTip()
    @State private var showEditor = false

    var body: some View {
        VStack {
            TipView(editorTip) { action in
                switch action.id {
                case "open-editor":
                    showEditor = true
                    editorTip.invalidate(reason: .actionPerformed)
                case "later":
                    editorTip.invalidate(reason: .tipClosed)
                default:
                    break
                }
            }

            MainContentView()
        }
        .sheet(isPresented: $showEditor) {
            EditorView()
        }
    }
}
```

## Integration with Onboarding Flow

Coordinate TipKit with a first-run onboarding flow. Invalidate welcome
tips after the user completes onboarding so they do not see redundant
information.

```swift
struct WelcomeTip: Tip {
    @Parameter
    static var hasCompletedOnboarding: Bool = false

    var title: Text { Text("Welcome to MyApp") }
    var message: Text? { Text("Swipe through to learn the basics.") }

    var rules: [Rule] {
        // Only show if onboarding was NOT completed (user skipped it)
        #Rule(Self.$hasCompletedOnboarding) { $0 == false }
    }
}

struct FeatureDiscoveryTip: Tip {
    @Parameter
    static var hasCompletedOnboarding: Bool = false

    var title: Text { Text("Discover Collections") }
    var message: Text? { Text("Organize your items into collections for easy access.") }

    var rules: [Rule] {
        // Only show after onboarding completes
        #Rule(Self.$hasCompletedOnboarding) { $0 == true }
    }
}

struct OnboardingView: View {
    @Binding var isPresented: Bool

    var body: some View {
        VStack {
            // Onboarding pages...

            Button("Get Started") {
                completeOnboarding()
            }
        }
    }

    func completeOnboarding() {
        // Invalidate welcome tips since onboarding covered the basics
        WelcomeTip.hasCompletedOnboarding = true
        FeatureDiscoveryTip.hasCompletedOnboarding = true

        // Explicitly invalidate any welcome-specific tips
        let welcomeTip = WelcomeTip()
        welcomeTip.invalidate(reason: .actionPerformed)

        isPresented = false
    }
}

struct ContentView: View {
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    @State private var showOnboarding = false

    let welcomeTip = WelcomeTip()
    let discoveryTip = FeatureDiscoveryTip()

    var body: some View {
        NavigationStack {
            VStack {
                TipView(welcomeTip)

                CollectionGrid()
                    .popoverTip(discoveryTip)
            }
        }
        .sheet(isPresented: $showOnboarding) {
            OnboardingView(isPresented: $showOnboarding)
        }
        .onAppear {
            if !hasCompletedOnboarding {
                showOnboarding = true
            }
        }
    }
}
```

## Reusable Tip Identifiers

Override `id` when one reusable `Tip` type should create separate persisted
records for different content. The ID controls status, display count, rules,
and invalidation state.

```swift
struct NewCollectionTip: Tip {
    let collection: CollectionSummary

    var id: String {
        "NewCollectionTip-\(collection.id)"
    }

    var title: Text {
        Text("Explore \(collection.name)")
    }

    var message: Text? {
        Text("A new collection is ready for browsing.")
    }
}

struct CollectionListView: View {
    let latestCollection: CollectionSummary

    var body: some View {
        TipView(NewCollectionTip(collection: latestCollection))
        CollectionGrid()
    }
}
```

Use stable model identifiers. Do not use localized copy, array indexes, dates
that change every launch, or random values.

## CloudKit Sync (iOS 18+)

CloudKit sync shares TipKit status, rules, parameters, events, display counts,
and display duration across devices signed into the same iCloud account.

Project setup:

- Enable iCloud and CloudKit in Signing & Capabilities.
- Enable Background Modes > Remote notifications.
- Prefer a dedicated CloudKit container with a `.tips` suffix.

```swift
@main
struct SyncedTipsApp: App {
    init() {
        do {
            try Tips.configure([
                .cloudKitContainer(.named("iCloud.com.example.MyApp.tips")),
                .displayFrequency(.daily)
            ])
        } catch {
            assertionFailure("TipKit configuration failed: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

Use `.cloudKitContainer(.automatic)` only when the entitlement list is
deliberately arranged so TipKit can choose the intended container. When sharing
tip state across app-group members or devices, keep option settings consistent
for the same tip IDs.

## Full App Integration Example

A complete example showing TipKit configuration, multiple tips with rules,
event donations, and proper invalidation.

```swift
import SwiftUI
import TipKit

// MARK: - Tips

struct SearchTip: Tip {
    var title: Text { Text("Search Your Library") }
    var message: Text? { Text("Tap to find any item by name, tag, or date.") }
    var image: Image? { Image(systemName: "magnifyingglass") }
}

struct CollectionTip: Tip {
    static let itemAddedEvent = Tips.Event(id: "itemAdded")

    var title: Text { Text("Create a Collection") }
    var message: Text? { Text("Group related items together for quick access.") }
    var image: Image? { Image(systemName: "folder.badge.plus") }

    var rules: [Rule] {
        #Rule(Self.itemAddedEvent) { $0.donations.count >= 3 }
    }
}

struct ShareTip: Tip {
    @Parameter
    static var hasCreatedCollection: Bool = false

    var title: Text { Text("Share Your Collection") }
    var message: Text? { Text("Invite others to view or collaborate on your collection.") }
    var image: Image? { Image(systemName: "square.and.arrow.up") }

    var rules: [Rule] {
        #Rule(Self.$hasCreatedCollection) { $0 == true }
    }
}

// MARK: - App

@main
struct LibraryApp: App {
    init() {
        do {
            #if DEBUG
            if ProcessInfo.processInfo.arguments.contains("--reset-tips") {
                try Tips.resetDatastore()
            }
            if ProcessInfo.processInfo.arguments.contains("--show-all-tips") {
                Tips.showAllTipsForTesting()
            }
            if ProcessInfo.processInfo.arguments.contains("--hide-all-tips") {
                Tips.hideAllTipsForTesting()
            }
            #endif

            try Tips.configure([
                .displayFrequency(.daily),
                .datastoreLocation(.applicationDefault)
            ])
        } catch {
            assertionFailure("TipKit configuration failed: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup { LibraryView() }
    }
}

// MARK: - Main View

struct LibraryView: View {
    let searchTip = SearchTip()
    let collectionTip = CollectionTip()
    let shareTip = ShareTip()

    @State private var items: [LibraryItem] = []

    var body: some View {
        NavigationStack {
            List {
                TipView(collectionTip)

                ForEach(items) { item in
                    Text(item.name)
                }
            }
            .navigationTitle("Library")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button("Search", systemImage: "magnifyingglass") {
                        showSearch()
                        searchTip.invalidate(reason: .actionPerformed)
                    }
                    .popoverTip(searchTip)
                }

                ToolbarItem(placement: .secondaryAction) {
                    Button("Share", systemImage: "square.and.arrow.up") {
                        shareCollection()
                        shareTip.invalidate(reason: .actionPerformed)
                    }
                    .popoverTip(shareTip)
                }

                ToolbarItem(placement: .secondaryAction) {
                    Button("Add Item", systemImage: "plus") {
                        addItem()
                        CollectionTip.itemAddedEvent.sendDonation()
                    }
                }
            }
        }
    }

    func addItem() { /* ... */ }
    func showSearch() { /* ... */ }
    func shareCollection() { /* ... */ }
}
```
