# SwiftUI View, Lifecycle, and Layout Migrations

Read this reference only when the task matches the sections below.

## foregroundColor(_:) to foregroundStyle(_:)

`foregroundColor(_:)` was deprecated in iOS 17. Its replacement, `foregroundStyle(_:)`, accepts any `ShapeStyle` -- not just `Color` -- enabling gradients, hierarchical styles, and materials directly.

### Before (Deprecated)

```swift
Text("Hello")
    .foregroundColor(.red)

Text("Secondary")
    .foregroundColor(.secondary)
```

### After (Modern)

```swift
Text("Hello")
    .foregroundStyle(.red)

Text("Secondary")
    .foregroundStyle(.secondary)

// Gradient -- not possible with foregroundColor
Text("Gradient")
    .foregroundStyle(
        .linearGradient(colors: [.blue, .purple],
                        startPoint: .leading, endPoint: .trailing)
    )
```

### Migration Notes

`foregroundStyle(_:)` is a drop-in replacement when passing a `Color`. The broader `ShapeStyle` conformance also accepts gradients, `.tint`, `.selection`, and hierarchical styles (`.primary`, `.secondary`, `.tertiary`, `.quaternary`). Multi-level variants `foregroundStyle(_:_:)` and `foregroundStyle(_:_:_:)` set hierarchical styles for child content in one call.

**Not to be confused with** `NSAttributedString.Key.foregroundColor` -- that is a UIKit/Foundation attributed-string key used for Core Text, `NSAttributedString`, and PDF rendering. It is not deprecated and has no SwiftUI equivalent.

---

## .onChange(of:perform:) to Modern onChange

The single-value `onChange` closure was deprecated in iOS 17. Modern overloads can run a zero-argument closure or provide both old and new values.

### Before (Deprecated)

```swift
.onChange(of: searchText) { newValue in
    performSearch(newValue)
}
```

### After (Modern: new value only)

```swift
.onChange(of: searchText) {
    performSearch(searchText)
}
```

### After (Modern: compare old and new)

```swift
.onChange(of: searchText) { oldValue, newValue in
    performSearch(newValue)
}
```

If you only need the new value, use `_` for the old value:

```swift
.onChange(of: searchText) { _, newValue in
    performSearch(newValue)
}
```

### Migration Notes

The two-value variant lets you compare old and new values inline without maintaining extra state. The `initial` parameter is also available if you need the callback to fire on first appearance:

```swift
.onChange(of: searchText, initial: true) { _, newValue in
    performSearch(newValue)
}
```

---

## ActionSheet to confirmationDialog

### Before (Deprecated)

```swift
.actionSheet(isPresented: $showingOptions) {
    ActionSheet(
        title: Text("Choose an action"),
        message: Text("Select one of the options below"),
        buttons: [
            .default(Text("Share")) { shareItem() },
            .destructive(Text("Delete")) { deleteItem() },
            .cancel()
        ]
    )
}
```

### After (Modern)

```swift
.confirmationDialog("Choose an action",
                     isPresented: $showingOptions,
                     titleVisibility: .visible) {
    Button("Share") { shareItem() }
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
} message: {
    Text("Select one of the options below")
}
```

### Migration Notes

`.confirmationDialog` uses standard SwiftUI `Button` views with roles instead of an array of `ActionSheet.Button`. The `titleVisibility` parameter controls whether the title appears (it is hidden by default on iOS). A cancel-role button is added automatically if you omit one.

---

## Alert (Legacy) to Modern .alert with Actions

### Before (Deprecated)

```swift
.alert(isPresented: $showingAlert) {
    Alert(
        title: Text("Delete Item?"),
        message: Text("This action cannot be undone."),
        primaryButton: .destructive(Text("Delete")) { deleteItem() },
        secondaryButton: .cancel()
    )
}
```

### After (Modern)

```swift
.alert("Delete Item?", isPresented: $showingAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) {}
} message: {
    Text("This action cannot be undone.")
}
```

With a data item:

```swift
.alert("Delete Item?", isPresented: $showingAlert, presenting: itemToDelete) { item in
    Button("Delete", role: .destructive) { delete(item) }
} message: { item in
    Text("Delete \"\(item.title)\"? This cannot be undone.")
}
```

### Migration Notes

The modern alert API accepts a `presenting` parameter to pass data directly into the alert closures, eliminating the need for separate optional state tracking.

---

## AnyView to `@ViewBuilder` and Concrete Types

### Before (Type-Erased Pattern)

```swift
func destination(for route: Route) -> AnyView {
    switch route {
    case .home: return AnyView(HomeView())
    case .profile: return AnyView(ProfileView())
    case .settings: return AnyView(SettingsView())
    }
}
```

### After (Modern)

```swift
@ViewBuilder
func destination(for route: Route) -> some View {
    switch route {
    case .home: HomeView()
    case .profile: ProfileView()
    case .settings: SettingsView()
    }
}
```

### Migration Notes

`AnyView` erases type information and hides useful view structure from SwiftUI. `@ViewBuilder` preserves concrete types, helping the framework reason about identity, updates, and transitions. Avoid `AnyView` unless interfacing with APIs that genuinely require heterogeneous view storage.

---

## .onAppear + Manual Task to .task

### Before (Manual Lifecycle Pattern)

```swift
struct FeedView: View {
    @State private var posts: [Post] = []

    var body: some View {
        List(posts) { post in
            PostRow(post: post)
        }
        .onAppear {
            Task {
                posts = try await fetchPosts()
            }
        }
    }
}
```

### After (Modern)

```swift
struct FeedView: View {
    @State private var posts: [Post] = []

    var body: some View {
        List(posts) { post in
            PostRow(post: post)
        }
        .task {
            do {
                posts = try await fetchPosts()
            } catch {
                // handle error
            }
        }
    }
}
```

### Migration Notes

`.task` automatically cancels the async work when the view disappears, preventing retain cycles and stale updates. Use `.task(id:)` to re-run the task when a dependency changes:

```swift
.task(id: selectedCategory) {
    posts = try? await fetchPosts(for: selectedCategory)
}
```

---

## `@Environment(\.presentationMode)` to `@Environment(\.dismiss)`

### Before (Deprecated)

```swift
struct DetailView: View {
    @Environment(\.presentationMode) var presentationMode

    var body: some View {
        Button("Done") {
            presentationMode.wrappedValue.dismiss()
        }
    }
}
```

### After (Modern)

```swift
struct DetailView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        Button("Done") {
            dismiss()
        }
    }
}
```

### Migration Notes

`dismiss` is a callable `DismissAction`. Call it directly -- no `.wrappedValue` needed. Works for sheets, full-screen covers, and navigation push destinations.

---

## GeometryReader Overuse to Layout Protocol and containerRelativeFrame

GeometryReader has performance costs and complicates layout. iOS 16 introduced the Layout protocol, and iOS 17 added `containerRelativeFrame` for proportional sizing.

### Before (Fragile Layout Pattern)

```swift
GeometryReader { proxy in
    HStack(spacing: 0) {
        SidePanel()
            .frame(width: proxy.size.width * 0.3)
        MainContent()
            .frame(width: proxy.size.width * 0.7)
    }
}
```

### After (Modern) -- containerRelativeFrame (iOS 17+)

```swift
HStack(spacing: 0) {
    SidePanel()
        .containerRelativeFrame(.horizontal) { length, _ in
            length * 0.3
        }
    MainContent()
        .containerRelativeFrame(.horizontal) { length, _ in
            length * 0.7
        }
}
```

### After (Modern) -- Custom Layout (iOS 16+)

```swift
struct ProportionalHStack: Layout {
    var ratios: [CGFloat]

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        proposal.replacingUnspecifiedDimensions()
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        guard subviews.count == ratios.count else { return }
        var x = bounds.minX
        for (index, subview) in subviews.enumerated() {
            let width = bounds.width * ratios[index]
            subview.place(at: CGPoint(x: x, y: bounds.minY),
                          proposal: ProposedViewSize(width: width, height: bounds.height))
            x += width
        }
    }
}

// Usage
ProportionalHStack(ratios: [0.3, 0.7]) {
    SidePanel()
    MainContent()
}
```

### Migration Notes

GeometryReader is still appropriate when you genuinely need to read the proposed size and cannot express the layout declaratively. For proportional sizing, prefer `containerRelativeFrame`. For custom arrangements, prefer the Layout protocol. Both avoid the bottom-up sizing behavior that makes GeometryReader tricky to compose.

---

## PreviewProvider to #Preview Macro

### Before (Legacy)

```swift
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .previewDevice("iPhone 15 Pro")

        ContentView()
            .preferredColorScheme(.dark)
    }
}
```

### After (Modern)

```swift
#Preview("Light Mode") {
    ContentView()
}

#Preview("Dark Mode") {
    ContentView()
        .preferredColorScheme(.dark)
}
```

Widget and UIKit previews:

```swift
#Preview("Timeline Entry", as: .systemSmall) {
    MyWidget()
} timeline: {
    SimpleEntry(date: .now)
}

#Preview("UIKit Controller") {
    let vc = MyViewController()
    vc.title = "Preview"
    return vc
}
```

### Migration Notes

The `#Preview` macro (iOS 17+) is less boilerplate and supports naming each preview directly. It works with SwiftUI views, UIKit view controllers, and WidgetKit timelines. For modern targets, replace `PreviewProvider` structs with `#Preview` blocks.

---

## XCTest to Swift Testing

Swift Testing (Xcode 16+) provides a modern, expressive test framework that coexists with XCTest.

### Before (XCTest)

```swift
import XCTest
@testable import MyApp

final class CartTests: XCTestCase {
    var cart: Cart!

    override func setUp() {
        cart = Cart()
    }

    override func tearDown() {
        cart = nil
    }

    func testAddItem() throws {
        cart.add(Item(name: "Widget", price: 9.99))
        XCTAssertEqual(cart.items.count, 1)
        XCTAssertEqual(cart.total, 9.99, accuracy: 0.01)
    }

    func testEmptyCartTotal() {
        XCTAssertEqual(cart.total, 0)
    }

    func testDiscountCodes() throws {
        let codes = ["SAVE10", "SAVE20", "SAVE50"]
        for code in codes {
            cart.applyDiscount(code: code)
            XCTAssertTrue(cart.hasDiscount)
        }
    }
}
```

### After (Swift Testing)

```swift
import Testing
@testable import MyApp

@Suite("Cart Tests")
struct CartTests {
    let cart = Cart()

    @Test("Adding an item updates count and total")
    func addItem() {
        cart.add(Item(name: "Widget", price: 9.99))
        #expect(cart.items.count == 1)
        #expect(cart.total.isApproximatelyEqual(to: 9.99))
    }

    @Test("Empty cart has zero total")
    func emptyCartTotal() {
        #expect(cart.total == 0)
    }

    @Test("Discount codes", arguments: ["SAVE10", "SAVE20", "SAVE50"])
    func discountCodes(code: String) {
        cart.applyDiscount(code: code)
        #expect(cart.hasDiscount)
    }
}
```

### Migration Notes

- Replace `XCTestCase` subclass with a plain struct annotated with `@Suite`.
- Replace `setUp` / `tearDown` with an initializer and deinit (or just inline setup).
- Replace `XCTAssert*` macros with `#expect(...)` and `#require(...)`.
- Use `@Test("description", arguments:)` for parameterized tests instead of manual loops.
- Swift Testing and XCTest targets can coexist in the same project during migration.
- Use `@Test(.disabled("reason"))` instead of `XCTSkip`.

---
