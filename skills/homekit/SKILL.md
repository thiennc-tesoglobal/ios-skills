---
name: homekit
description: "Control smart-home accessories and commission Matter devices using HomeKit and MatterSupport. Use when managing homes/rooms/accessories, creating action sets or triggers, reading accessory characteristics, onboarding Matter devices, or building a third-party smart-home ecosystem app."
---

# HomeKit

Control home automation accessories and commission Matter devices into an app ecosystem. HomeKit manages the home/room/accessory hierarchy, characteristics, and automation triggers; MatterSupport handles ecosystem device commissioning.

## Contents

- [Setup & Framework Boundaries](#setup--framework-boundaries)
- [HomeKit Data Model](#homekit-data-model)
- [Accessories & Characteristics](#accessories--characteristics)
- [Action Sets & Triggers](#action-sets--triggers)
- [Matter Device Commissioning](#matter-device-commissioning)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Framework Boundaries

### Entitlements & Info.plist
1. Enable the **HomeKit** capability in Xcode.
2. Add `NSHomeKitUsageDescription` to Info.plist.
3. For MatterSupport commissioning: add a MatterSupport Extension target, declare Bonjour services (`_matter._tcp`, `_matterc._udp`, `_matterd._udp`), and set the extension's principal class to `MatterAddDeviceExtensionRequestHandler`.

### Boundary Division
- **HomeKit**: Homes, rooms, accessory control, characteristics, scenes, triggers.
- **MatterSupport**: Commissioning Matter hardware into a third-party ecosystem.
- **AccessorySetupKit**: Selecting/pairing nearby Bluetooth/Wi-Fi devices without broad permissions.
- **CoreBluetooth / NetworkExtension**: Raw data transport after device authorization.

## HomeKit Data Model

HomeKit loads asynchronously. Maintain a single `HMHomeManager` instance and await the `homeManagerDidUpdateHomes(_:)` delegate callback before accessing `homes` or `primaryHome`.

```text
HMHomeManager -> HMHome -> HMRoom -> HMAccessory -> HMService -> HMCharacteristic
```

```swift
import HomeKit

final class HomeStore: NSObject, HMHomeManagerDelegate {
    let manager = HMHomeManager()

    override init() {
        super.init()
        manager.delegate = self
    }

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        // Safe to read homes and accessories
        let primary = manager.primaryHome
    }
}
```

## Accessories & Characteristics

Interact with accessory services (e.g. lights, thermostats) via `HMCharacteristic`:

```swift
func setLightPower(_ characteristic: HMCharacteristic, isOn: Bool) async throws {
    guard characteristic.characteristicType == HMCharacteristicTypePowerState else { return }
    try await characteristic.writeValue(isOn)
}

func readTemperature(_ characteristic: HMCharacteristic) async throws -> Double? {
    try await characteristic.readValue()
    return characteristic.value as? Double
}
```

## Action Sets & Triggers

Group changes into scenes and automate execution:

```swift
// Create an action set (scene)
func createNightScene(home: HMHome, lightAction: HMCharacteristicWriteAction<Bool>) async throws {
    let actionSet = try await home.addActionSet(withName: "Good Night")
    try await actionSet.addAction(lightAction)
}

// Event-based automation
func addTrigger(home: HMHome, trigger: HMEventTrigger) async throws {
    try await home.addTrigger(trigger)
    try await trigger.enable(true)
}
```

## Matter Device Commissioning

Use `MatterSupport` to onboard Matter devices into your ecosystem:

```swift
import MatterSupport

let topology = MatterAddDeviceRequest.Topology(ecosystemName: "MyHome", homes: [home])
let request = MatterAddDeviceRequest(topology: topology)
try await request.perform()
```

The system invokes your `MatterAddDeviceExtensionRequestHandler` subclass in the extension target to complete pairing.

## Common Mistakes

- **Accessing `homes` synchronously at launch**: `manager.homes` is empty until `homeManagerDidUpdateHomes` fires.
- **Missing Bonjour services for Matter**: Commissioning fails silently without `_matter._tcp`, `_matterc._udp`, and `_matterd._udp` in `NSBonjourServices`.
- **Directly modifying characteristic values**: Always call asynchronous `characteristic.writeValue(_:)` rather than mutating state locally.
- **Creating multiple HMHomeManager instances**: Instantiate one shared manager to prevent duplicate notifications and sync conflicts.
- **Confusing HomeKit with AccessorySetupKit**: Use HomeKit for smart-home accessories; use AccessorySetupKit for proprietary BLE/Wi-Fi peripherals.

## Review Checklist

- [ ] `NSHomeKitUsageDescription` present in target Info.plist
- [ ] `HMHomeManager` instantiated once and guarded until `homeManagerDidUpdateHomes` fires
- [ ] Characteristic mutations performed via `writeValue(_:)` with error handling
- [ ] MatterSupport extension target configured with Bonjour service declarations
- [ ] Triggers explicitly enabled via `trigger.enable(true)` after creation

## References

- Extended patterns (Matter extension, delegate wiring, SwiftUI): [references/matter-commissioning.md](references/matter-commissioning.md)
- [HomeKit framework](https://sosumi.ai/documentation/homekit)
- [HMHomeManager](https://sosumi.ai/documentation/homekit/hmhomemanager)
- [HMHome](https://sosumi.ai/documentation/homekit/hmhome)
- [HMAccessory](https://sosumi.ai/documentation/homekit/hmaccessory)
- [HMRoom](https://sosumi.ai/documentation/homekit/hmroom)
- [HMActionSet](https://sosumi.ai/documentation/homekit/hmactionset)
- [HMTrigger](https://sosumi.ai/documentation/homekit/hmtrigger)
- [MatterSupport framework](https://sosumi.ai/documentation/mattersupport)
- [MatterAddDeviceRequest](https://sosumi.ai/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceExtensionRequestHandler](https://sosumi.ai/documentation/mattersupport/matteradddeviceextensionrequesthandler)
- [Enabling HomeKit in your app](https://sosumi.ai/documentation/homekit/enabling-homekit-in-your-app)
- [Adding Matter support to your ecosystem](https://sosumi.ai/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
