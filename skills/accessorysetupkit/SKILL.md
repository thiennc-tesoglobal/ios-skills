---
name: accessorysetupkit
description: "Discover and configure Bluetooth and Wi-Fi accessories using AccessorySetupKit. Use when presenting a privacy-preserving accessory picker, defining discovery descriptors for BLE or Wi-Fi devices, handling accessory session events, migrating from CoreBluetooth permission-based scanning, or setting up accessories without requiring broad Bluetooth permissions."
---

# AccessorySetupKit

Discover and pair Bluetooth and Wi-Fi accessories with privacy-preserving iOS 18+ system pickers. `ASAccessorySession` eliminates the need for broad system Bluetooth authorization prompts. After user authorization, hand off communication to CoreBluetooth or NetworkExtension.

## Contents

- [Setup & Entitlements](#setup--entitlements)
- [Discovery Descriptors](#discovery-descriptors)
- [Session Activation & Picker](#session-activation--picker)
- [Transport Handoff](#transport-handoff)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Entitlements

Add matching configuration keys to Info.plist:

| Key | Type | Purpose |
|---|---|---|
| `NSAccessorySetupSupports` | `[String]` | Required. Contains `Bluetooth` and/or `WiFi` |
| `NSAccessorySetupBluetoothServices` | `[String]` | Service UUIDs discovered by the app |
| `NSAccessorySetupBluetoothNames` | `[String]` | Accessory name substrings to match |
| `NSAccessorySetupBluetoothCompanyIdentifiers` | `[String]` | Two-byte Bluetooth company identifiers |

The Bluetooth-specific Info.plist values must strictly match the rules in `ASDiscoveryDescriptor`. If an accessory matches a descriptor not declared in Info.plist, the app crashes at runtime.

No user Bluetooth permission prompt is triggered; `CBCentralManager` transitions to `poweredOn` once at least one accessory is authorized via AccessorySetupKit.

## Discovery Descriptors

Define matching criteria for scanning nearby hardware:

```swift
import AccessorySetupKit
import CoreBluetooth

// Bluetooth Descriptor
var btDescriptor = ASDiscoveryDescriptor()
btDescriptor.bluetoothServiceUUID = CBUUID(string: "12345678-1234-1234-1234-123456789ABC")
btDescriptor.bluetoothNameSubstring = "SmartSensor"
btDescriptor.bluetoothRange = .immediate // Only nearby devices

// Wi-Fi Descriptor (provide either ssid OR ssidPrefix, not both)
var wifiDescriptor = ASDiscoveryDescriptor()
wifiDescriptor.ssidPrefix = "SmartSensor-"
```

## Session Activation & Picker

Activate an `ASAccessorySession` and present the system picker:

```swift
import AccessorySetupKit

final class AccessoryCoordinator {
    let session = ASAccessorySession()

    func start() {
        session.activate(on: .main) { [weak self] event in
            switch event.eventType {
            case .accessoryAdded, .accessoryChanged:
                if let accessory = event.accessory {
                    self?.handleAuthorizedAccessory(accessory)
                }
            case .accessoryRemoved:
                self?.handleRemovedAccessory(event.accessory)
            case .sessionReset:
                self?.session.activate(on: .main, eventHandler: { _ in })
            @unknown default:
                break
            }
        }
    }

    func presentPicker(descriptor: ASDiscoveryDescriptor) {
        let displayItem = ASPickerDisplayItem(
            name: "Smart Sensor",
            productImage: UIImage(named: "sensor")!,
            descriptor: descriptor
        )
        session.showPicker(for: [displayItem]) { error in
            if let error { print("Picker failed: \(error)") }
        }
    }
}
```

## Transport Handoff

After the user selects an accessory in the system picker:
- **Bluetooth**: Retrieve the peripheral using `CBCentralManager.retrievePeripherals(withIdentifiers: [accessory.bluetoothIdentifier])`. Do not run general scans.
- **Wi-Fi**: Connect to the authorized Wi-Fi network using NetworkExtension (`NEHotspotConfigurationManager`).

## Common Mistakes

- **Undeclared Info.plist properties**: Any UUID, name, or company ID used in an `ASDiscoveryDescriptor` must be declared in Info.plist or the app crashes.
- **Setting both ssid and ssidPrefix**: Wi-Fi descriptors must set either `ssid` or `ssidPrefix`, never both.
- **Triggering general CoreBluetooth scans**: AccessorySetupKit apps should never call `scanForPeripherals()`; retrieve authorized peripherals by identifier.
- **Ignoring `.sessionReset`**: The system can invalidate sessions during daemon restarts; recreate or reactivate the session upon `.sessionReset`.
- **Assuming immediate connection**: Picker completion indicates authorization, not active connection. Initiate the connection via CoreBluetooth after handoff.

## Review Checklist

- [ ] `NSAccessorySetupSupports` declared in Info.plist with `Bluetooth` / `WiFi`
- [ ] All descriptor UUIDs, names, and company IDs declared in Info.plist
- [ ] Wi-Fi descriptor specifies either `ssid` or `ssidPrefix`, not both
- [ ] Peripherals retrieved via `retrievePeripherals(withIdentifiers:)` without scanning
- [ ] Session events handled for `.accessoryAdded`, `.accessoryRemoved`, and `.sessionReset`

## References

- Extended patterns (custom filtering, batch setup, removal handling, error recovery): [references/accessorysetupkit-patterns.md](references/accessorysetupkit-patterns.md)
- [AccessorySetupKit framework](https://sosumi.ai/documentation/accessorysetupkit)
- [ASAccessorySession](https://sosumi.ai/documentation/accessorysetupkit/asaccessorysession)
- [ASDiscoveryDescriptor](https://sosumi.ai/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://sosumi.ai/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASAccessory](https://sosumi.ai/documentation/accessorysetupkit/asaccessory)
- [ASAccessoryEvent](https://sosumi.ai/documentation/accessorysetupkit/asaccessoryevent)
- [ASMigrationDisplayItem](https://sosumi.ai/documentation/accessorysetupkit/asmigrationdisplayitem)
- [Discovering and configuring accessories](https://sosumi.ai/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [Setting up and authorizing a Bluetooth accessory](https://sosumi.ai/documentation/accessorysetupkit/setting-up-and-authorizing-a-bluetooth-accessory)
- [Meet AccessorySetupKit — WWDC24](https://sosumi.ai/videos/play/wwdc2024/10203/)
