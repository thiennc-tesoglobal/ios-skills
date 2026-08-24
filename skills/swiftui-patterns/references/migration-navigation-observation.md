# SwiftUI Navigation and Observation Migrations

A comprehensive mapping of deprecated, legacy, or fragile SwiftUI and iOS patterns to modern defaults from iOS 15 through iOS 26. Each section shows the old pattern, the modern replacement, and migration notes. Target iOS 26 with Swift 6.3; backward-compatible to iOS 16 unless noted.

## NavigationView to NavigationStack

NavigationView was deprecated in iOS 16. Use NavigationStack for push-based navigation with a single column, or NavigationSplitView for multi-column layouts.

### Before (Deprecated)

```swift
struct ContentView: View {
    var body: some View {
        NavigationView {
            List(items) { item in
                NavigationLink(destination: DetailView(item: item)) {
                    Text(item.title)
                }
            }
            .navigationTitle("Items")
        }
        .navigationViewStyle(.stack)
    }
}
```

### After (Modern)

```swift
struct ContentView: View {
    @State private var path: [Item] = []

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    Text(item.title)
                }
            }
            .navigationTitle("Items")
            .navigationDestination(for: Item.self) { item in
                DetailView(item: item)
            }
        }
    }
}
```

### Migration Notes

NavigationStack gives you programmatic control over the navigation path via a binding. Value-based NavigationLink separates the trigger from the destination, keeping list rows lightweight. The `.navigationViewStyle(.stack)` modifier is no longer needed.

---

## NavigationView Sidebar to NavigationSplitView

### Before (Deprecated)

```swift
struct SidebarApp: View {
    var body: some View {
        NavigationView {
            SidebarList()
            DetailPlaceholder()
        }
        .navigationViewStyle(.columns)
    }
}
```

### After (Modern)

```swift
struct SidebarApp: View {
    @State private var selectedCategory: Category?
    @State private var selectedItem: Item?

    var body: some View {
        NavigationSplitView {
            List(categories, selection: $selectedCategory) { category in
                Label(category.name, systemImage: category.icon)
            }
            .navigationTitle("Categories")
        } content: {
            if let category = selectedCategory {
                List(category.items, selection: $selectedItem) { item in
                    Text(item.title)
                }
            } else {
                ContentUnavailableView("Select a Category",
                                       systemImage: "sidebar.left")
            }
        } detail: {
            if let item = selectedItem {
                DetailView(item: item)
            } else {
                ContentUnavailableView("Select an Item",
                                       systemImage: "doc.text")
            }
        }
    }
}
```

### Migration Notes

NavigationSplitView explicitly models two-column and three-column layouts. Column visibility is controlled via `NavigationSplitViewVisibility` and `columnVisibility` bindings. On compact size classes the split view collapses into a NavigationStack automatically.

---

## ObservableObject / `@Published` / `@StateObject` to `@Observable` / `@State`

The Observation framework (iOS 17+) replaces Combine-based observation. Classes annotated with `@Observable` track property access automatically -- no `@Published` wrappers needed.

### Before (Superseded)

```swift
class UserSettings: ObservableObject {
    @Published var username: String = ""
    @Published var notificationsEnabled: Bool = true
    @Published var theme: Theme = .system

    func resetToDefaults() {
        username = ""
        notificationsEnabled = true
        theme = .system
    }
}

struct SettingsView: View {
    @StateObject private var settings = UserSettings()

    var body: some View {
        Form {
            TextField("Username", text: $settings.username)
            Toggle("Notifications", isOn: $settings.notificationsEnabled)
            Picker("Theme", selection: $settings.theme) {
                ForEach(Theme.allCases) { theme in
                    Text(theme.rawValue).tag(theme)
                }
            }
        }
    }
}
```

### After (Modern)

```swift
@Observable
class UserSettings {
    var username: String = ""
    var notificationsEnabled: Bool = true
    var theme: Theme = .system

    func resetToDefaults() {
        username = ""
        notificationsEnabled = true
        theme = .system
    }
}

struct SettingsView: View {
    @State private var settings = UserSettings()

    var body: some View {
        Form {
            TextField("Username", text: $settings.username)
            Toggle("Notifications", isOn: $settings.notificationsEnabled)
            Picker("Theme", selection: $settings.theme) {
                ForEach(Theme.allCases) { theme in
                    Text(theme.rawValue).tag(theme)
                }
            }
        }
    }
}
```

### Migration Notes

- Replace `ObservableObject` conformance with the `@Observable` macro.
- Remove all `@Published` property wrappers -- observation is automatic.
- Replace `@StateObject` with `@State` for owned instances.
- Computed properties that depend on stored properties are tracked automatically.
- The view only re-evaluates when properties it actually reads change, so fine-grained observation is free.
- **Requires iOS 17+ minimum deployment target.** `ObservableObject` is not formally deprecated (no compiler warning) -- it is superseded. Do not rewrite working `ObservableObject` code if the project targets iOS 16 or earlier.

---

## `@ObservedObject` to let / `@Bindable`

### Before (Superseded)

```swift
struct ProfileEditor: View {
    @ObservedObject var profile: ProfileModel

    var body: some View {
        TextField("Name", text: $profile.name)
        Toggle("Public", isOn: $profile.isPublic)
    }
}
```

### After (Modern)

When you only need to read properties, use a plain `let`:

```swift
struct ProfileDisplay: View {
    let profile: ProfileModel  // @Observable class

    var body: some View {
        Text(profile.name)
        Text(profile.isPublic ? "Public" : "Private")
    }
}
```

When you need to create bindings, use `@Bindable`:

```swift
struct ProfileEditor: View {
    @Bindable var profile: ProfileModel

    var body: some View {
        TextField("Name", text: $profile.name)
        Toggle("Public", isOn: $profile.isPublic)
    }
}
```

### Migration Notes

With `@Observable`, you no longer need `@ObservedObject` to subscribe to changes. A plain `let` constant already triggers view updates when read properties change. Use `@Bindable` only when you need two-way bindings via `$` syntax.

---

## `@EnvironmentObject` to `@Environment`

### Before (Superseded)

```swift
// Injection
ContentView()
    .environmentObject(authManager)

// Usage
struct ContentView: View {
    @EnvironmentObject var auth: AuthManager

    var body: some View {
        if auth.isLoggedIn {
            HomeView()
        } else {
            LoginView()
        }
    }
}
```

### After (Modern)

```swift
// Injection
ContentView()
    .environment(authManager)

// Usage
struct ContentView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        if auth.isLoggedIn {
            HomeView()
        } else {
            LoginView()
        }
    }
}
```

### Migration Notes

With `@Observable`, use `.environment(_:)` (the type-keyed overload) instead of `.environmentObject(_:)`. Read with `@Environment(Type.self)`. If you need bindings from an environment-injected object, pull it into a local `@Bindable`:

```swift
struct ContentView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        @Bindable var auth = auth
        Toggle("Remember Me", isOn: $auth.rememberMe)
    }
}
```

---
