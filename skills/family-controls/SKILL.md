---
name: family-controls
description: "Request Screen Time authorization with FamilyControls, pick apps and web domains with FamilyActivityPicker, apply shields via ManagedSettings, and monitor usage schedules with DeviceActivity in iOS."
---

# FamilyControls & Screen Time

Build parental control, focus, and digital wellbeing features on iOS and iPadOS using `FamilyControls`, `ManagedSettings`, and `DeviceActivity`.

## Contents

- [Authorization & Capabilities](#authorization--capabilities)
- [Selecting Apps with FamilyActivityPicker](#selecting-apps-with-familyactivitypicker)
- [Enforcing Restrictions with ManagedSettings](#enforcing-restrictions-with-managedsettings)
- [Monitoring Usage with DeviceActivity](#monitoring-usage-with-deviceactivity)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

---

## Authorization & Capabilities

FamilyControls requires the Family Controls Entitlement (`com.apple.developer.family-controls`). Request authorization via `AuthorizationCenter.shared` before presenting pickers or configuring stores.

```swift
import FamilyControls

@MainActor
final class ScreenTimeAuthManager {
    static let shared = ScreenTimeAuthManager()

    func requestAuthorization(for memberType: FamilyControlsMember = .individual) async throws {
        // Options: .individual (user's own device) or .child (parental device managing child)
        try await AuthorizationCenter.shared.requestAuthorization(for: memberType)
    }

    var authorizationStatus: AuthorizationStatus {
        AuthorizationCenter.shared.authorizationStatus
    }
}
```

---

## Selecting Apps with FamilyActivityPicker

Allow users to select apps, categories, or web domains using SwiftUI's `familyActivityPicker`. Store the opaque `FamilyActivitySelection` securely in `UserDefaults` via an App Group container.

```swift
import SwiftUI
import FamilyControls

struct AppRestrictionPickerView: View {
    @State private var selection = FamilyActivitySelection()
    @State private var isPickerPresented = false

    var body: some View {
        Button("Select Apps to Shield") {
            isPickerPresented = true
        }
        .familyActivityPicker(
            isPresented: $isPickerPresented,
            selection: $selection
        )
        .onChange(of: selection) { _, newSelection in
            saveSelection(newSelection)
        }
    }

    private func saveSelection(_ selection: FamilyActivitySelection) {
        guard let groupDefaults = UserDefaults(suiteName: "group.com.example.app.screentime") else { return }
        if let encoded = try? PropertyListEncoder().encode(selection) {
            groupDefaults.set(encoded, forKey: "ShieldedSelection")
        }
    }
}
```

---

## Enforcing Restrictions with ManagedSettings

Use `ManagedSettingsStore` to apply app shields, block application installs, restrict web domains, or enforce safari filter policies.

```swift
import ManagedSettings
import FamilyControls

@MainActor
final class ShieldManager {
    static let shared = ShieldManager()
    private let store = ManagedSettingsStore(named: .init("FocusShield"))

    func applyShield(to selection: FamilyActivitySelection) {
        // Shield specific applications
        store.shield.applications = selection.applicationTokens.isEmpty ? nil : selection.applicationTokens

        // Shield categories with optional exclusions
        store.shield.applicationCategories = selection.categoryTokens.isEmpty ? nil : .specific(selection.categoryTokens)

        // Shield web domains
        store.shield.webDomains = selection.webDomainTokens.isEmpty ? nil : selection.webDomainTokens
    }

    func clearShield() {
        store.clearAllSettings()
    }
}
```

---

## Monitoring Usage with DeviceActivity

Schedule background monitoring thresholds with `DeviceActivitySchedule` and `DeviceActivityCenter`. Time limit events invoke the separate `DeviceActivityMonitor` extension target.

```swift
import DeviceActivity

final class DeviceScheduleManager {
    static let shared = DeviceScheduleManager()
    private let center = DeviceActivityCenter()

    func startSchedule() throws {
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 9, minute: 0),
            intervalEnd: DateComponents(hour: 17, minute: 0),
            repeats: true,
            warningTime: DateComponents(minute: 5)
        )

        let activityName = DeviceActivityName("WorkHoursSchedule")
        try center.startMonitoring(activityName, during: schedule)
    }

    func stopSchedule() {
        center.stopMonitoring([DeviceActivityName("WorkHoursSchedule")])
    }
}
```

---

## Common Mistakes

- **Missing Family Controls Entitlement:** Calling `AuthorizationCenter.requestAuthorization` without approval and provisioning profile entitlement fails immediately.
- **Reading application tokens directly:** `ApplicationToken` and `WebDomainToken` are deliberately opaque tokens for user privacy; apps cannot read bundle identifiers or URLs from them.
- **Putting monitor logic in main app process:** `DeviceActivityMonitor` runs in a separate extension process triggered by the system daemon; do not expect the main app to receive delegate calls directly.
- **Failing to clear ManagedSettingsStore:** Shield policies persist across app restarts and uninstalls if not cleared by calling `clearAllSettings()` or explicitly resetting properties.
- **Using default UserDefaults for extensions:** Main app and DeviceActivity extensions must use an App Group `UserDefaults(suiteName:)` to share serialized `FamilyActivitySelection`.

---

## Review Checklist

- [ ] Has the `com.apple.developer.family-controls` entitlement been declared and provisioned?
- [ ] Is `AuthorizationCenter.shared.requestAuthorization()` invoked before opening the picker or modifying settings?
- [ ] Are `FamilyActivitySelection` instances serialized with `PropertyListEncoder` / `PropertyListDecoder` into an App Group suite?
- [ ] Are shields applied using `ManagedSettingsStore` rather than private APIs?
- [ ] Is `clearAllSettings()` provided to allow users to release shields?
- [ ] Does the `DeviceActivityMonitor` extension handle `intervalDidStart`, `intervalDidEnd`, and `eventDidReachThreshold`?

---

## References

- [Screen Time Patterns](references/screen-time-patterns.md) — Custom shield configurations, DeviceActivityMonitor extensions, and persistence.
- [FamilyControls Documentation](https://sosumi.ai/documentation/familycontrols) — Authorization and opaque activity selection tokens.
- [ManagedSettings Documentation](https://sosumi.ai/documentation/managedsettings) — Setting shields, media restrictions, and Safari filters.
- [DeviceActivity Documentation](https://sosumi.ai/documentation/deviceactivity) — Usage monitoring schedules, events, and background monitors.
