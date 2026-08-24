# TipKit Styles, Groups, and Testing

Read this reference only when the task matches the sections below.

## Custom TipViewStyle

Create a branded tip appearance that matches the app's design language.
The `Configuration` provides access to the tip's title, message, image,
and actions.

```swift
struct BrandedTipStyle: TipViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack(alignment: .top) {
            configuration.image?
                .font(.system(size: 24))
                .foregroundStyle(.white)
                .frame(width: 44, height: 44)
                .background(.blue.gradient, in: RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading) {
                configuration.title?
                    .font(.headline)

                configuration.message?
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                if !configuration.actions.isEmpty {
                    HStack {
                        ForEach(configuration.actions) { action in
                            Button(action: action.handler) {
                                action.label()
                                    .font(.subheadline.bold())
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                    .padding(.top)
                }
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}
```

### Applying the Custom Style

Apply the style to individual `TipView` instances or set it as the
environment default.

```swift
// Per view
TipView(myTip)
    .tipViewStyle(BrandedTipStyle())

// Environment-wide (apply to a parent container)
NavigationStack {
    ContentView()
}
.tipViewStyle(BrandedTipStyle())
```

### Minimal Compact Style

A stripped-down style for tips in tight layouts like toolbars or sidebars.

```swift
struct CompactTipStyle: TipViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.image?
                .foregroundStyle(.tint)

            configuration.title?
                .font(.caption.bold())
        }
        .padding(.horizontal)
        .padding(.vertical)
        .background(.tint.opacity(0.1), in: Capsule())
    }
}
```

## TipGroup Sequencing (iOS 18+)

Use `TipGroup` to present related tips. `TipGroup` defaults to
`.firstAvailable`, which shows the first eligible tip in the group without
requiring a strict sequence. Pass `.ordered` only when each later tip must wait
until all previous tips have been invalidated.

For ordered coach-mark flows, only the current tip displays. When the user
dismisses or acts on it, invalidate that tip so the next tip in the group can
become current.

```swift
struct OnboardingTipA: Tip {
    var title: Text { Text("Welcome to the App") }
    var message: Text? { Text("Let's take a quick tour of the main features.") }
    var image: Image? { Image(systemName: "hand.wave") }
}

struct OnboardingTipB: Tip {
    var title: Text { Text("Browse Your Feed") }
    var message: Text? { Text("Swipe through curated content tailored for you.") }
    var image: Image? { Image(systemName: "rectangle.stack") }
}

struct OnboardingTipC: Tip {
    var title: Text { Text("Customize Your Profile") }
    var message: Text? { Text("Tap your avatar to set your name and preferences.") }
    var image: Image? { Image(systemName: "person.crop.circle") }
}

struct HomeView: View {
    @State private var tipGroup = TipGroup(.ordered) {
        OnboardingTipA()
        OnboardingTipB()
        OnboardingTipC()
    }

    var body: some View {
        VStack {
            if let currentTip = tipGroup.currentTip {
                TipView(currentTip) { action in
                    currentTip.invalidate(reason: .actionPerformed)
                }
            }

            FeedView()
        }
        .padding()
    }
}
```

### Tip Group with Popover

Attach the group's current tip as a popover that moves between controls
as tips advance.

```swift
struct ToolbarGroupView: View {
    @State private var group = TipGroup(.ordered) {
        SearchTip()
        FilterTip()
        SortTip()
    }

    var body: some View {
        HStack {
            Button("Search", systemImage: "magnifyingglass") { search() }
                .popoverTip(group.currentTip as? SearchTip)

            Button("Filter", systemImage: "line.3.horizontal.decrease") { filter() }
                .popoverTip(group.currentTip as? FilterTip)

            Button("Sort", systemImage: "arrow.up.arrow.down") { sort() }
                .popoverTip(group.currentTip as? SortTip)
        }
    }
}
```

## Testing Strategies

### Previewing Tips in SwiftUI Previews

Configure TipKit in the preview body so tips display in Xcode previews.
Use `showAllTipsForTesting()` to bypass rules. Reset the datastore before
configuration; `Tips.resetDatastore()` must not run after `Tips.configure()`.

```swift
#Preview {
    ContentView()
        .task {
            try? Tips.resetDatastore()
            Tips.showAllTipsForTesting()
            try? Tips.configure([.displayFrequency(.immediate)])
        }
}
```

### Previewing a Specific Tip

Show only one tip in a focused preview.

```swift
#Preview("Favorite Tip") {
    VStack {
        TipView(FavoriteTip())
        Spacer()
    }
    .padding()
    .task {
        try? Tips.resetDatastore()
        Tips.showTipsForTesting([FavoriteTip.self])
        try? Tips.configure([.displayFrequency(.immediate)])
    }
}
```

### Unit Testing Tip Rules

Verify that parameter and event rules correctly control tip eligibility.
Reset the datastore before each test to ensure a clean state.
TipKit configuration is process-level, so prefer isolated UI-test launches for
full lifecycle coverage. If using unit tests, reset before configuring.

```swift
import XCTest
import TipKit

final class TipRuleTests: XCTestCase {
    override func setUp() async throws {
        try Tips.resetDatastore()
        try Tips.configure([.displayFrequency(.immediate)])
    }

    func testAdvancedSearchTipRequiresLogin() async {
        let tip = AdvancedSearchTip()

        // Tip should not be eligible before login
        AdvancedSearchTip.isLoggedIn = false
        // Verify tip status

        // Tip should become eligible after login + enough events
        AdvancedSearchTip.isLoggedIn = true
        for _ in 0..<3 {
            AdvancedSearchTip.searchPerformed.sendDonation()
        }
        // Verify tip status
    }

    func testTipInvalidation() async {
        let tip = FavoriteTip()
        tip.invalidate(reason: .actionPerformed)
        // Tip should no longer be eligible after invalidation
    }
}
```

### UI Testing with Forced Tips

Pass launch arguments to control tip visibility in UI tests. This ensures
tests that verify tip UI always see the tip, regardless of rules.

```swift
// In UI test setUp
let app = XCUIApplication()
app.launchArguments += [
    "-com.apple.TipKit.ResetDatastore", "1",
    "-com.apple.TipKit.ShowAllTips", "1"
]
app.launch()
```

```swift
// Optional custom wrappers in App.init
init() {
    if ProcessInfo.processInfo.arguments.contains("--show-all-tips") {
        Tips.showAllTipsForTesting()
    }
    if ProcessInfo.processInfo.arguments.contains("--hide-all-tips") {
        Tips.hideAllTipsForTesting()
    }
    try? Tips.configure()
}
```

### UI Testing Without Tips

Suppress all tips in UI tests that are not about tip behavior, so tips
do not interfere with other test flows.

```swift
// In UI test setUp for non-tip tests
let app = XCUIApplication()
app.launchArguments += ["-com.apple.TipKit.HideAllTips", "1"]
app.launch()
```
