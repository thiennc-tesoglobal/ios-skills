# AppMigrationKit Core Implementation Details

Read this reference when the task needs concrete setup, API wiring, or implementation recipes. Keep scope, workflow, non-obvious invariants, mistakes, and review gates in the parent `SKILL.md`.

## Architecture Overview

AppMigrationKit operates through three layers:

1. **App extension** -- An `AppMigrationExtension` conforming type that the
   system invokes during migration. It handles data export and import.
2. **System orchestration** -- The OS manages the device-to-device session,
   transport, and scheduling. The extension does not control when it runs.
3. **Containing app** -- After migration completes, the app checks
   `MigrationStatus.importStatus` on first launch to determine whether
   migration occurred and whether it succeeded.

Key types:

| Type | Role |
|---|---|
| `AppMigrationExtension` | Protocol for the app extension entry point |
| `ResourcesExportingWithOptions` | Protocol for exporting files via archiver |
| `ResourcesExporting` | Simplified export protocol (no custom options) |
| `ResourcesImporting` | Protocol for importing files on the destination |
| `ResourcesArchiver` | Streams files into the export archive |
| `MigrationDataContainer` | Access to the containing app's data directories |
| `MigrationStatus` | Check import result from the containing app |
| `MigrationPlatform` | Identifies the other device's platform (e.g., `.android`) |
| `MigrationAppIdentifier` | Identifies the source app by store and bundle ID |
| `AppMigrationTester` | Test-only actor for validating export/import logic |

## Setup and Entitlements

### Entitlement

The app extension requires the `com.apple.developer.app-migration.data-container-access`
entitlement. Its value is a single-element string array containing the bundle
identifier of the containing app:

```xml
<key>com.apple.developer.app-migration.data-container-access</key>
<array>
    <string>com.example.myapp</string>
</array>
```

No other values are valid. This entitlement grants the extension read access
to the containing app's data container during export and write access during
import. The entitlement itself is available on iOS 26.1+, iPadOS 26.1+,
and Mac Catalyst 26.1+, even though the core AppMigrationKit APIs are
available on iOS 26.0+ and iPadOS 26.0+.

### Extension Target

Add a new App Extension target to the Xcode project. The extension conforms
to one or more of the migration protocols (`ResourcesExportingWithOptions`,
`ResourcesExporting`, `ResourcesImporting`).

## App Migration Extension

The extension entry point conforms to `AppMigrationExtension`. During
migration, the system prevents launching the containing app and its other
extensions to ensure exclusive data access.

### Accessing the Data Container

The extension accesses the containing app's files through `appContainer`:

```swift
import AppMigrationKit

struct MyMigrationExtension: ResourcesExporting {
    var resourcesSizeEstimate: Int { estimateTotalExportSize() }
    var resourcesVersion: String { "1.0" }
    var resourcesCompressible: Bool { true }

    func exportResources(
        to archiver: sending ResourcesArchiver,
        request: MigrationRequest
    ) async throws {
        let container = appContainer

        // container.bundleIdentifier     -- app's bundle ID
        // container.containerRootDirectory -- root of the app container
        // container.documentsDirectory    -- Documents/
        // container.applicationSupportDirectory -- Application Support/
    }
}
```

`MigrationDataContainer` provides `containerRootDirectory`, `documentsDirectory`,
and `applicationSupportDirectory` as `URL` values pointing into the containing
app's sandbox.

## Exporting Resources

Conform to `ResourcesExportingWithOptions` (or `ResourcesExporting` for no
custom options) to package files for transfer. The system calls
`exportResources(to:request:)` with a `ResourcesArchiver` and a
`MigrationRequestWithOptions`.

### Declaring Export Properties

```swift
struct MyMigrationExtension: ResourcesExportingWithOptions {
    typealias OptionsType = MigrationDefaultSupportedOptions

    var resourcesSizeEstimate: Int {
        // Return estimated total bytes of exported data
        calculateExportSize()
    }

    var resourcesVersion: String {
        "1.0"
    }

    var resourcesCompressible: Bool {
        true  // Let the system compress during transport
    }
}
```

- `resourcesSizeEstimate` -- Estimated total bytes. The system uses this for
  progress UI and free-space checks.
- `resourcesVersion` -- Format version string. The import side receives this
  to handle versioned data formats.
- `resourcesCompressible` -- When `true`, the archiver may compress files
  during transport.

### Implementing Export

```swift
func exportResources(
    to archiver: sending ResourcesArchiver,
    request: MigrationRequestWithOptions<MigrationDefaultSupportedOptions>
) async throws {
    let docsDir = appContainer.documentsDirectory

    // Check destination platform if needed
    if request.destinationPlatform == .android {
        // Platform-specific export logic
    }

    // Append files one at a time -- make continuous progress
    let userDataURL = docsDir.appending(path: "user_data.json")
    try await archiver.appendItem(at: userDataURL)

    // Append with a custom archive path
    let settingsURL = docsDir.appending(path: "settings.plist")
    try await archiver.appendItem(at: settingsURL, pathInArchive: "preferences/settings.plist")

    // Append a directory
    let photosDir = docsDir.appending(path: "photos")
    try await archiver.appendItem(at: photosDir, pathInArchive: "media/photos")
}
```

The archiver streams files incrementally. Call `appendItem(at:pathInArchive:)`
repeatedly as each resource is ready. The system may terminate the extension
if it appears hung, so avoid long gaps between append calls.

### Cancellation

`ResourcesArchiver` handles task cancellation automatically by throwing
cancellation errors. Do not catch these errors -- doing so causes the system
to kill the extension.

### Migration Platform

`MigrationRequestWithOptions` exposes `destinationPlatform` as a
`MigrationPlatform` value. Use this to tailor exported data:

```swift
if request.destinationPlatform == .android {
    // Export in a format the Android app expects
}
```

`MigrationPlatform` provides `.android` as a static constant. Custom
platforms can be created with `MigrationPlatform("customPlatform")`.

## Importing Resources

Conform to `ResourcesImporting` to receive transferred files on the
destination device. The system calls `importResources(at:request:)` after
app installation but before the app is launchable.

```swift
struct MyMigrationExtension: ResourcesImporting {
    func importResources(
        at importedDataURL: URL,
        request: ResourcesImportRequest
    ) async throws {
        let sourceVersion = request.sourceVersion
        let sourceApp = request.sourceAppIdentifier

        // sourceApp.platform        -- e.g., .android
        // sourceApp.bundleIdentifier -- source app's bundle ID
        // sourceApp.storeIdentifier  -- e.g., .googlePlay

        // Copy imported files into the app container
        let docsDir = appContainer.documentsDirectory

        let userData = importedDataURL.appending(path: "user_data.json")
        if FileManager.default.fileExists(atPath: userData.path()) {
            try FileManager.default.copyItem(
                at: userData,
                to: docsDir.appending(path: "user_data.json")
            )
        }
    }
}
```

### Error Handling During Import

On import error, the system clears the containing app's data container to
prevent partial state. However, app group containers are not cleared. The
import implementation should clear any app group containers before writing
imported content:

```swift
func importResources(
    at importedDataURL: URL,
    request: ResourcesImportRequest
) async throws {
    // Clear shared app group data first
    let groupURL = FileManager.default.containerURL(
        forSecurityApplicationGroupIdentifier: "group.com.example.myapp"
    )
    if let groupURL {
        try? FileManager.default.removeItem(at: groupURL.appending(path: "shared_data"))
    }

    // Then import
    try await performImport(from: importedDataURL)
}
```

### Source App Identifier

`ResourcesImportRequest` provides `sourceAppIdentifier` as a
`MigrationAppIdentifier` with three properties:

- `platform` -- The source device's platform (e.g., `.android`)
- `bundleIdentifier` -- The source app's bundle identifier
- `storeIdentifier` -- The app store (e.g., `.googlePlay`)

## Migration Status

After migration completes, the containing app checks the result on first
launch:

```swift
import AppMigrationKit

func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    if let status = MigrationStatus.importStatus {
        switch status {
        case .success:
            showMigrationSuccessUI()
            MigrationStatus.clearImportStatus()
        case .failure(let error):
            showMigrationFailureUI(error: error)
            MigrationStatus.clearImportStatus()
        }
    }
    return true
}
```

- `MigrationStatus.importStatus` is `nil` if no migration occurred.
- Call `clearImportStatus()` after handling the result to prevent showing
  the notification on subsequent launches.
- The enum has two cases: `.success` and `.failure(any Error)`.

## Progress Tracking

The import side exposes a `Progress` object via `resourcesImportProgress`.
The system uses this to display transfer progress to the user. Update
`completedUnitCount` incrementally during import:

```swift
struct MyMigrationExtension: ResourcesImporting {
    private let importProgress = Progress(totalUnitCount: 100)

    var resourcesImportProgress: Progress { importProgress }

    func importResources(
        at importedDataURL: URL,
        request: ResourcesImportRequest
    ) async throws {
        let files = try FileManager.default.contentsOfDirectory(
            at: importedDataURL, includingPropertiesForKeys: nil
        )
        let increment = Int64(100 / max(files.count, 1))
        for file in files {
            try processFile(file)
            importProgress.completedUnitCount += increment
        }
        importProgress.completedUnitCount = 100
    }
}
```

## Testing

`AppMigrationTester` is a test-only actor for validating migration logic
in unit tests hosted by the containing app. Do not use it in production.

```swift
import Testing
import AppMigrationKit

@Test func testExportImportRoundTrip() async throws {
    let tester = try await AppMigrationTester(platform: .android)

    // Export
    let result = try await tester.exportController.exportResources(
        request: nil, progress: nil
    )
    #expect(result.exportProperties.uncompressedBytes > 0)

    // Import the exported data
    try await tester.importController.importResources(
        from: result.extractedResourcesURL,
        importRequest: nil, progress: nil
    )
    try await tester.importController.registerImportCompletion(with: .success)
}
```

`DeviceToDeviceExportProperties` on the result exposes `uncompressedBytes`,
`compressedBytes` (nil if not compressible), `sizeEstimate`, and `version`.

See [references/appmigrationkit-patterns.md](appmigrationkit-patterns.md) for additional test patterns.
