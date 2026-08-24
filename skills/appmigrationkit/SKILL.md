---
name: appmigrationkit
description: "Builds one-time cross-platform app-data transfers with AppMigrationKit. Use for AppMigrationExtension setup, ResourcesArchiver export/import, transportable resources, progress, cancellation, MigrationStatus, app-group cleanup, recovery, or AppMigrationTester verification."
---

# AppMigrationKit

One-time cross-platform data transfer for app resources. Enables apps to
export data to or import data from another platform (for example, Android)
during device setup or onboarding. AppMigrationKit APIs are iOS 26.0+ /
iPadOS 26.0+; the data-container entitlement is iOS 26.1+ / iPadOS 26.1+ /
Mac Catalyst 26.1+. Swift 6.3.

> **Beta-sensitive.** AppMigrationKit is new in iOS 26 and may change before GM.
> Re-check current Apple documentation before relying on specific API details.

AppMigrationKit uses an app extension model. The system orchestrates the
transfer between devices. The app provides an extension conforming to export
and import protocols, and the system calls that extension at the appropriate
time. The app itself never manages the network connection between devices.

## Workflow

1. Confirm platform availability, migration entitlement, extension target, and shared-container layout.
2. Inventory transportable resources, stable paths, size limits, versioning, and source-app identity.
3. Export directly through `ResourcesArchiver` with bounded gaps, progress, and cancellation propagation.
4. Import transactionally, validate every resource, preserve recoverable evidence, and clean app-group state after success or failure.
5. Verify with `AppMigrationTester`, cancellation, partial archives, version skew, low storage, retry, and status clearing.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for architecture, entitlements, export/import, status, progress, testing, and error recovery.
- Read [extended AppMigrationKit patterns](references/appmigrationkit-patterns.md) for combined extensions, versioned migration, enumeration, and complex recovery flows.

## Core Decisions

- Archive original resources directly instead of converting them during export.
- Propagate archiver cancellation and avoid long pauses between append operations.
- Validate imported paths and content before committing destination state.
- Clear migration/import status only after the app has durably handled the result.

## Common Mistakes

### DON'T: Catch cancellation errors from ResourcesArchiver

```swift
// WRONG -- system kills the extension if cancellation is swallowed
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    do {
        try await archiver.appendItem(at: fileURL)
    } catch is CancellationError {
        // Swallowing this causes termination
    }
}

// CORRECT -- let cancellation propagate
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    try await archiver.appendItem(at: fileURL)
}
```

### DON'T: Leave long gaps between archiver append calls

```swift
// WRONG -- system may assume the extension is hung and terminate it
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    let allFiles = gatherAllFiles()  // Takes 30 seconds
    for file in allFiles {
        try await archiver.appendItem(at: file)
    }
}

// CORRECT -- interleave file preparation with archiving
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    for file in knownFilePaths() {
        try await archiver.appendItem(at: file)
    }
}
```

### DON'T: Convert files to intermediate format during export

```swift
// WRONG -- may exhaust disk space creating temporary copies
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    let converted = try convertToJSON(originalDatabase)  // Doubles disk usage
    try await archiver.appendItem(at: converted)
}

// CORRECT -- export files as-is, convert on import side if needed
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    try await archiver.appendItem(at: originalDatabase)
}
```

### DON'T: Ignore app group containers during import error recovery

```swift
// WRONG -- system clears app container but not app groups on error
func importResources(at url: URL, request: ResourcesImportRequest) async throws {
    try writeToAppGroup(data)
    try writeToAppContainer(data)  // If this throws, app group has stale data
}

// CORRECT -- clear app group data before importing
func importResources(at url: URL, request: ResourcesImportRequest) async throws {
    try clearAppGroupData()
    try writeToAppGroup(data)
    try writeToAppContainer(data)
}
```

### DON'T: Forget to clear import status after handling it

```swift
// WRONG -- migration UI shows every launch
if let status = MigrationStatus.importStatus {
    showMigrationResult(status)
    // Missing clearImportStatus()
}

// CORRECT
if let status = MigrationStatus.importStatus {
    showMigrationResult(status)
    MigrationStatus.clearImportStatus()
}
```

## Review Checklist

- [ ] Extension target added with `com.apple.developer.app-migration.data-container-access` entitlement
- [ ] Entitlement array contains exactly one string: the containing app's bundle identifier
- [ ] Extension conforms to `ResourcesExportingWithOptions` or `ResourcesExporting` for export
- [ ] Extension conforms to `ResourcesImporting` for import
- [ ] `resourcesSizeEstimate` returns a reasonable byte estimate
- [ ] `resourcesVersion` is set and will be checked on import for format compatibility
- [ ] Export calls `appendItem` incrementally without long pauses
- [ ] Cancellation errors from `ResourcesArchiver` are not caught
- [ ] Import clears app group containers before writing new data
- [ ] Containing app checks `MigrationStatus.importStatus` on first launch
- [ ] `clearImportStatus()` called after handling the migration result
- [ ] `AppMigrationTester` used in unit tests to validate export and import
- [ ] Files are exported as-is without intermediate format conversion on the export side
- [ ] `sourceVersion` from import request used to handle versioned data formats

## References

- Extended patterns (combined extension, versioned migration, file enumeration, error recovery): [references/appmigrationkit-patterns.md](references/appmigrationkit-patterns.md)
- [AppMigrationKit framework](https://sosumi.ai/documentation/appmigrationkit)
- [AppMigrationExtension](https://sosumi.ai/documentation/appmigrationkit/appmigrationextension)
- [ResourcesExportingWithOptions](https://sosumi.ai/documentation/appmigrationkit/resourcesexportingwithoptions)
- [ResourcesImporting](https://sosumi.ai/documentation/appmigrationkit/resourcesimporting)
- [ResourcesArchiver](https://sosumi.ai/documentation/appmigrationkit/resourcesarchiver)
- [MigrationStatus](https://sosumi.ai/documentation/appmigrationkit/migrationstatus)
- [MigrationDataContainer](https://sosumi.ai/documentation/appmigrationkit/migrationdatacontainer)
- [AppMigrationTester](https://sosumi.ai/documentation/appmigrationkit/appmigrationtester)
- [Data container entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.app-migration.data-container-access)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
