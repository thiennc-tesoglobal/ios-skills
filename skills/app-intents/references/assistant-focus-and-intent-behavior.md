# App Intents Assistant, Focus, and Intent Behavior

Read this reference only when the task matches the sections below.

## Assistant Schemas (iOS 18+)

Assistant schemas define domain-specific intents that Apple Intelligence
understands natively. Annotate conforming types with schema macros.

### Declaration

```swift
// Preferred macro (iOS 18+)
@AppIntent(schema: .photos.openAsset)
struct OpenPhotoIntent: AppIntent { ... }

// CORRECT: Using preferred macro
@AppIntent(schema: .photos.openAsset)
struct OpenPhotoIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Photo"

    @Parameter(title: "Asset")
    var target: PhotoEntity

    func perform() async throws -> some IntentResult {
        PhotoViewer.shared.open(target.id)
        return .result()
    }
}

@AppEntity(schema: .photos.asset)
struct PhotoEntity: AppEntity {
    var id: String
    static let defaultQuery = PhotoQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Photo"
    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }
    var name: String
}

@AppEnum(schema: .photos.assetType)
enum PhotoType: String, AppEnum {
    case photo, video, livePhoto
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Photo Type"
    static var caseDisplayRepresentations: [PhotoType: DisplayRepresentation] = [
        .photo: "Photo",
        .video: "Video",
        .livePhoto: "Live Photo"
    ]
}
```

Avoid the deprecated `AssistantIntent(schema:)`, `AssistantEntity(schema:)`, and
`AssistantEnum(schema:)` macros in new code.

### Domain catalog

Use Xcode completion and the current domain docs for exact schema cases. The
major Apple domains are:

| Domain | Example actions | Example content |
|---|---|---|
| Assistant | side-button conversational app launch | -- |
| Books | open book, create bookmark | book, audiobook |
| Browser | open tab, create bookmark, search web | tab, bookmark, window |
| Camera | capture photo, capture video | -- |
| File management | open, create, move, rename, delete file | file |
| Journaling | create, update, delete, search entry | journal entry |
| Mail | open mailbox, send draft | account, draft, mailbox, message |
| Photos | open asset, create album, search assets | album, asset, person |
| Presentations | open document, add slide | document, slide, template |
| Reader | open document, go to page | document, page |
| Spreadsheet | open document, add sheet | document, sheet, template |
| System and in-app search | search | -- |
| Visual intelligence | semantic content search | -- |
| Whiteboard | open board, create item | board, item |
| Word processor | open document, add page | document, page, template |

### isAssistantOnly

Control whether a schema-conforming type is exclusive to Apple Intelligence or
also available through other system surfaces:

```swift
@AppIntent(schema: .photos.openAsset)
struct OpenPhotoIntent: AppIntent {
    static let isAssistantOnly = false  // Also available in Shortcuts
    // ...
}
```

## Focus Filter Intents

Customize app behavior when a Focus mode activates.

```swift
struct WorkFocusFilter: SetFocusFilterIntent {
    static var title: LocalizedStringResource = "Work Focus"
    static var description = IntentDescription("Configure app for work mode.")

    @Parameter(title: "Show Only Work Projects", default: true)
    var workOnly: Bool

    @Parameter(title: "Mute Notifications", default: false)
    var muteNotifications: Bool

    var displayRepresentation: DisplayRepresentation {
        "Work Mode"
    }

    func perform() async throws -> some IntentResult {
        AppSettings.shared.workModeEnabled = workOnly
        AppSettings.shared.notificationsMuted = muteNotifications
        return .result()
    }
}
```

### Access current focus filter

```swift
let currentFilter = try? SetFocusFilterIntent.current
if let workFilter = currentFilter as? WorkFocusFilter {
    // Apply work-mode behavior
}
```

### Suggest filters for a focus context

```swift
extension WorkFocusFilter {
    static func suggestedFocusFilters(
        for context: FocusFilterSuggestionContext
    ) async -> [WorkFocusFilter] {
        [WorkFocusFilter(workOnly: true, muteNotifications: true)]
    }
}
```

## SiriKit Migration (CustomIntentMigratedAppIntent)

Replace SiriKit custom intents (`.intentdefinition` files) while preserving
existing user shortcuts and donations.

```swift
struct OrderSoupIntent: CustomIntentMigratedAppIntent {
    // Map to the old SiriKit intent class name -- must match exactly
    static var intentClassName: String = "OrderSoupIntent"

    static var title: LocalizedStringResource = "Order Soup"

    @Parameter(title: "Soup")
    var soup: SoupEntity

    @Parameter(title: "Quantity", default: 1)
    var quantity: Int

    func perform() async throws -> some IntentResult {
        let order = try await OrderService.shared.place(
            soup: soup.id,
            quantity: quantity
        )
        return .result(dialog: "Ordered \(quantity) bowls.")
    }
}
```

### Migration steps

1. Create a new `AppIntent` struct conforming to `CustomIntentMigratedAppIntent`.
2. Set `intentClassName` to the old SiriKit intent class name (exact match).
3. Recreate parameters using `@Parameter` instead of `.intentdefinition` props.
4. Implement `perform()` with async/await.
5. Existing user shortcuts and donations continue working via the class name.
6. Remove the `.intentdefinition` file once migration is verified.

### DeprecatedAppIntent (versioning within AppIntents)

Replace an old `AppIntent` with a newer version:

```swift
struct OldSearchIntent: DeprecatedAppIntent {
    typealias ReplacementIntent = NewSearchIntent
    static var deprecation: IntentDeprecation {
        .init(message: "Use the new search intent.")
    }
    static var title: LocalizedStringResource = "Search (Deprecated)"
    func perform() async throws -> some IntentResult { .result() }
}
```

## Error Handling and Dialog

### Standard error types (iOS 18+)

```swift
func perform() async throws -> some IntentResult {
    guard await PermissionManager.hasPhotoAccess else {
        throw AppIntentError.PermissionRequired.photos
    }

    guard let item = try await fetchItem() else {
        throw AppIntentError.Unrecoverable.entityNotFound
    }

    guard !requiresManualSetup else {
        throw AppIntentError.UserActionRequired.accountSetup
    }

    return .result()
}
```

| Error Type | When to Use |
|---|---|
| `AppIntentError.PermissionRequired` | Missing OS-level permission |
| `AppIntentError.Unrecoverable` | Fatal state with no immediate remedy |
| `AppIntentError.UserActionRequired` | User must sign in, confirm, or set up an account |

### Parameter-level errors

```swift
// Re-prompt for a value
throw $quantity.needsValueError("How many items?")

// Force disambiguation
throw $size.needsDisambiguation(among: [.small, .medium, .large])
```

### Foreground continuation

```swift
func perform() async throws -> some IntentResult {
    if needsUserInteraction {
        try await continueInForeground("Open the app to finish.")
    }
    // ...
    return .result()
}
```

### Dialog in results

```swift
func perform() async throws -> some IntentResult & ProvidesDialog {
    return .result(dialog: "Your soup order has been placed.")
}

func perform() async throws -> some IntentResult & ProvidesDialog & ReturnsValue<OrderEntity> {
    let order = try await placeOrder()
    return .result(
        value: OrderEntity(from: order),
        dialog: "Order #\(order.number) is confirmed."
    )
}
```

## Confirmation Flows

### Basic confirmation

```swift
func perform() async throws -> some IntentResult {
    try await requestConfirmation(
        actionName: .send,
        dialog: "Send \(quantity) messages?"
    )
    // User confirmed -- proceed
    return .result()
}
```

### Conditional confirmation

```swift
func perform() async throws -> some IntentResult {
    try await requestConfirmation(
        conditions: .always,
        actionName: .order,
        dialog: "Place order for \(quantity) \(soup.name)?"
    )
    return .result()
}
```

### Confirmation with SwiftUI content

```swift
func perform() async throws -> some IntentResult {
    try await requestConfirmation(
        actionName: .buy,
        dialog: "Purchase \(item.name) for \(item.price)?",
        view: OrderPreviewView(item: item)
    )
    return .result()
}
```

### User choice

```swift
func perform() async throws -> some IntentResult {
    let chosen = try await requestChoice(
        between: availableOptions,
        dialog: "Which option would you like?"
    )
    // Use chosen value
    return .result()
}
```

### ConfirmationActionName options

Built-in: `.add`, `.buy`, `.call`, `.create`, `.send`, `.share`, `.start`,
`.toggle`, `.turnOn`, `.turnOff`, `.open`, `.play`, `.post`, `.search`,
`.book`, `.download`, `.pay`, `.order`, `.run`, `.get`, `.go`, `.log`,
`.set`, `.view`, `.find`, `.filter`, `.continue`, `.do`, `.addData`,
`.checkIn`, `.request`, `.playSound`, `.startNavigation`.

Custom:

```swift
.custom(
    acceptLabel: "Confirm Purchase",
    acceptAlternatives: ["Yes", "Buy it"],
    denyLabel: "Cancel",
    denyAlternatives: ["No", "Never mind"],
    destructive: false
)
```

## Authentication Policies

Control when device authentication is required:

```swift
struct TransferMoneyIntent: AppIntent {
    static var authenticationPolicy: IntentAuthenticationPolicy = .requiresAuthentication
    static var title: LocalizedStringResource = "Transfer Money"

    func perform() async throws -> some IntentResult {
        // Device must be unlocked before this runs
        return .result()
    }
}
```

| Policy | Behavior |
|---|---|
| `.alwaysAllowed` | No authentication required |
| `.requiresAuthentication` | Device must be unlocked |
| `.requiresLocalDeviceAuthentication` | Face ID / Touch ID required |

```swift
// WRONG: Sensitive action without authentication
struct DeleteAccountIntent: AppIntent {
    // Missing authenticationPolicy -- runs on locked device
    func perform() async throws -> some IntentResult { ... }
}

// CORRECT: Require authentication for sensitive actions
struct DeleteAccountIntent: AppIntent {
    static var authenticationPolicy: IntentAuthenticationPolicy = .requiresLocalDeviceAuthentication
    static var title: LocalizedStringResource = "Delete Account"
    func perform() async throws -> some IntentResult { ... }
}
```
