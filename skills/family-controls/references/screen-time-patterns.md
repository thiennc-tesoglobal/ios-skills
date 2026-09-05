# Screen Time Patterns and Recipes

Detailed recipes for `DeviceActivityMonitor`, custom shield UI styling, shield actions, and inter-process sharing in Screen Time apps.

## DeviceActivityMonitor Extension

The monitor runs in a separate app extension process triggered by the system `DeviceActivity` daemon.

```swift
import DeviceActivity
import ManagedSettings
import Foundation

class MyDeviceActivityMonitor: DeviceActivityMonitor {
    private let store = ManagedSettingsStore(named: .init("ScheduledShield"))

    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)

        guard let groupDefaults = UserDefaults(suiteName: "group.com.example.screentime"),
              let data = groupDefaults.data(forKey: "ShieldedSelection"),
              let selection = try? PropertyListDecoder().decode(FamilyActivitySelection.self, from: data) else {
            return
        }

        // Apply shields when the schedule begins
        store.shield.applications = selection.applicationTokens
        store.shield.webDomains = selection.webDomainTokens
    }

    override func intervalDidEnd(for activity: DeviceActivityName) {
        super.intervalDidEnd(for: activity)

        // Clear shields when the scheduled window ends
        store.clearAllSettings()
    }

    override func eventDidReachThreshold(for activity: DeviceActivityName, event: DeviceActivityEvent.Name) {
        super.eventDidReachThreshold(for: activity, event: event)
        // User exceeded daily quota: lock selected apps
        if let groupDefaults = UserDefaults(suiteName: "group.com.example.screentime"),
           let data = groupDefaults.data(forKey: "ShieldedSelection"),
           let selection = try? PropertyListDecoder().decode(FamilyActivitySelection.self, from: data) {
            store.shield.applications = selection.applicationTokens
        }
    }
}
```

## Shield Configuration Extension

Customize the shield screen title, body, icon, and button styling displayed when a user opens a shielded application:

```swift
import ManagedSettingsUI
import UIKit

class ShieldConfigurationExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemUltraThinMaterial,
            backgroundColor: UIColor.systemBackground,
            title: ShieldConfiguration.Label(text: "Focus Session Active", color: .label),
            subtitle: ShieldConfiguration.Label(text: "This app is shielded during your scheduled focus time.", color: .secondaryLabel),
            primaryButtonLabel: ShieldConfiguration.Label(text: "Take a Break", color: .white),
            primaryButtonBackgroundColor: .systemIndigo,
            secondaryButtonLabel: ShieldConfiguration.Label(text: "Dismiss", color: .systemIndigo)
        )
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        ShieldConfiguration(
            title: ShieldConfiguration.Label(text: "Domain Blocked", color: .label),
            subtitle: ShieldConfiguration.Label(text: "Web access is restricted during focus hours.", color: .secondaryLabel),
            primaryButtonLabel: ShieldConfiguration.Label(text: "Close", color: .white),
            primaryButtonBackgroundColor: .systemBlue
        )
    }
}
```

## Shield Action Delegate Extension

Handle taps on the custom primary and secondary shield buttons:

```swift
import ManagedSettings

class ShieldActionExtension: ShieldActionDelegate {
    override func handle(
        action: ShieldAction,
        for application: ApplicationToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        switch action {
        case .primaryButtonPressed:
            // Custom logic (e.g. grant temporary emergency snooze)
            completionHandler(.defer)
        case .secondaryButtonPressed:
            // Close the shield UI
            completionHandler(.close)
        @unknown default:
            completionHandler(.close)
        }
    }
}
```

## Monitoring Threshold Events

Create cumulative time limit monitors with `DeviceActivityEvent`:

```swift
import DeviceActivity
import FamilyControls

final class UsageThresholdService {
    private let center = DeviceActivityCenter()

    func scheduleTimeLimit(selection: FamilyActivitySelection, limitMinutes: Int) throws {
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 0, minute: 0),
            intervalEnd: DateComponents(hour: 23, minute: 59),
            repeats: true
        )

        let eventName = DeviceActivityEvent.Name("DailyLimitEvent")
        let event = DeviceActivityEvent(
            applications: selection.applicationTokens,
            categories: selection.categoryTokens,
            webDomains: selection.webDomainTokens,
            threshold: DateComponents(minute: limitMinutes)
        )

        let activityName = DeviceActivityName("DailyLimitMonitoring")
        try center.startMonitoring(activityName, during: schedule, events: [eventName: event])
    }
}
```
