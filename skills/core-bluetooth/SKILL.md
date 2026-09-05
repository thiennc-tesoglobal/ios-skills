---
name: core-bluetooth
description: "Build direct Bluetooth Low Energy central or peripheral workflows with Core Bluetooth, including GATT discovery, state restoration, MTU sizing, and background modes. Use for BLE scanning, peripheral connection, characteristic reads/writes/notifications, or peripheral advertisement."
---

# Core Bluetooth

Implement Bluetooth Low Energy (BLE) communication on iOS using `CBCentralManager` (connecting to accessories) and `CBPeripheralManager` (advertising as an accessory). Targets Swift 6.3 / iOS 26+.

## Contents

- [Permissions and Background Modes](#permissions-and-background-modes)
- [Central vs Peripheral Roles](#central-vs-peripheral-roles)
- [Core Communication Contract](#core-communication-contract)
- [State Restoration and MTU](#state-restoration-and-mtu)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Permissions and Background Modes

Declare `NSBluetoothAlwaysUsageDescription` in `Info.plist`. For background execution, enable capabilities in Signing & Capabilities > Background Modes:
- **Uses Bluetooth LE accessories**: Central role in background (`bluetooth-central`)
- **Acts as a Bluetooth LE accessory**: Peripheral role in background (`bluetooth-peripheral`)

```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app requires Bluetooth to connect to external fitness sensors.</string>
<key>UIBackgroundModes</key>
<array>
    <string>bluetooth-central</string>
</array>
```

## Central vs Peripheral Roles

| Feature | Central (`CBCentralManager`) | Peripheral (`CBPeripheralManager`) |
|---|---|---|
| Primary Task | Scans, connects, and consumes GATT services | Publishes services, advertises, responds to requests |
| Discovery | `scanForPeripherals(withServices:options:)` | `startAdvertising(_:)` |
| Data Read/Write | `readValue(for:)` / `writeValue(_:for:type:)` | `respond(to:withResult:)` |
| Updates | Subscribes with `setNotifyValue(true, for:)` | `updateValue(_:for:onSubscribedCentrals:)` |
| Queue | Dedicated serial `DispatchQueue` | Dedicated serial `DispatchQueue` |

## Core Communication Contract

1. **Wait for `.poweredOn`**: Never call scan, connect, or advertise until `centralManagerDidUpdateState(_:)` reports `.poweredOn`.
2. **Retain discovered peripherals**: You must store a strong reference to `CBPeripheral` instances returned in `didDiscover`. If released, connection drops immediately.
3. **Scan with service UUIDs**: In background mode, scanning without explicit `CBUUID` filters is disabled by iOS to preserve battery.
4. **Discover narrowly**: Pass specific `[CBUUID]` arrays to `discoverServices` and `discoverCharacteristics` rather than `nil` to avoid slow full-GATT enumeration.
5. **Honor write types**: Use `.withResponse` for acknowledged writes (`peripheral(_:didWriteValueFor:error:)`); use `.withoutResponse` only when `canSendWriteWithoutResponse` is verified.

## State Restoration and MTU

- **State Restoration**: Pass `CBCentralManagerOptionRestoreIdentifierKey` during manager initialization to allow iOS to relaunch the app in the background when a Bluetooth event occurs. Handle restoration in `centralManager(_:willRestoreState:)`.
- **MTU & Packet Sizing**: Check `peripheral.maximumWriteValueLength(for:)` before sending large payloads. The default BLE MTU is 23 bytes (20 payload bytes). Do not assume 512-byte MTU without checking.

## Route by Task

- For a complete SwiftUI-ready `@Observable` BLE manager, read [SwiftUI BLE Integration](references/ble-patterns.md#swiftui-ble-integration).
- For exponential backoff and automatic peripheral reconnection, read [Reconnection Strategies](references/ble-patterns.md#reconnection-strategies).
- For byte buffers and binary data parsing helpers, read [Data Parsing Helpers](references/ble-patterns.md#data-parsing-helpers).
- For congestion control and packet flow management, read [Write Flow Control](references/ble-patterns.md#write-flow-control).
- For managing multiple simultaneous peripherals, read [Multiple Peripheral Management](references/ble-patterns.md#multiple-peripheral-management).
- For high-speed raw streaming without GATT overhead, read [L2CAP Channels](references/ble-patterns.md#l2cap-channels).
- For peripheral role request handling and subscription updates, read [Peripheral Role: Responding to Requests](references/ble-patterns.md#peripheral-role-responding-to-requests).

## Common Mistakes

- Initiating Bluetooth scanning before `centralManagerDidUpdateState(_:)` transitions to `.poweredOn`.
- Failing to retain the `CBPeripheral` reference during connection, leading to silent drops.
- Scanning without explicit service `CBUUID`s in background mode (system ignores unfiltered background scans).
- Ignoring `canSendWriteWithoutResponse`, causing silent packet drops during burst writes.
- Performing heavy parsing or UI operations on the Core Bluetooth dispatch queue.

## Review Checklist

- [ ] `NSBluetoothAlwaysUsageDescription` provided in `Info.plist`
- [ ] Required `UIBackgroundModes` configured (`bluetooth-central` / `bluetooth-peripheral`)
- [ ] State checked for `.poweredOn` before issuing commands
- [ ] Connected peripherals strongly referenced by the manager
- [ ] Service and characteristic discovery scoped to specific `[CBUUID]`
- [ ] Write type matches characteristic properties (`.withResponse` vs `.withoutResponse`)
- [ ] State restoration identifier configured and handled in `willRestoreState`
- [ ] Core Bluetooth delegate runs on a dedicated serial queue, with UI updates dispatched to `@MainActor`
- [ ] Maximum packet size validated with `maximumWriteValueLength`

## References

- [Core Bluetooth extended patterns and L2CAP guide](references/ble-patterns.md)
- [Core Bluetooth documentation](https://sosumi.ai/documentation/corebluetooth)
- [CBCentralManager](https://sosumi.ai/documentation/corebluetooth/cbcentralmanager)
- [CBPeripheral](https://sosumi.ai/documentation/corebluetooth/cbperipheral)
- [CBPeripheralManager](https://sosumi.ai/documentation/corebluetooth/cbperipheralmanager)
