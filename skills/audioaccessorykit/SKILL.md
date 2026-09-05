---
name: audioaccessorykit
description: "Integrate third-party audio accessories with Apple audio switching and spatial placement using AudioAccessoryKit. Use when configuring AccessoryControlDevice, handling device capabilities, monitoring accessory placement, or participating in automatic audio routing."
---

# AudioAccessoryKit

Participate in Apple's seamless audio ecosystem, automatic audio routing, and head/ear placement detection for third-party audio accessories. Targets Swift 6.3 / iOS 26+.

> **Prerequisite:** Audio accessories must be paired and authorized via `AccessorySetupKit` before configuring with `AudioAccessoryKit`.

## Contents

- [Core Concepts & Prerequisites](#core-concepts--prerequisites)
- [Registering Accessory Control Devices](#registering-accessory-control-devices)
- [Device Capabilities & Configuration](#device-capabilities--configuration)
- [Monitoring Placement State](#monitoring-placement-state)
- [Audio Routing Coordination](#audio-routing-coordination)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Core Concepts & Prerequisites

`AudioAccessoryKit` bridges authorized Bluetooth accessories into iOS system audio management:
1. Discover and pair the hardware using `AccessorySetupKit`.
2. Wrap the authorized peripheral in an `AccessoryControlDevice`.
3. Register device capabilities (ANC, spatial audio, ear detection).
4. Update live placement state (in-ear, in-case, on-head) so iOS can dynamically switch audio routes.

## Registering Accessory Control Devices

Register an `AccessoryControlDevice` for an authorized accessory:

```swift
import AudioAccessoryKit
import AccessorySetupKit

func configureAudioAccessory(accessory: ASAccessory) async throws {
    guard let btIdentifier = accessory.bluetoothIdentifier else { return }

    var config = AccessoryControlDevice.Configuration()
    config.capabilities = [.earDetection, .noiseControl, .spatialAudio]

    let device = try await AccessoryControlDevice.register(
        identifier: btIdentifier,
        configuration: config
    )
}
```

## Device Capabilities & Configuration

Configure active hardware capabilities and audio listening modes:

```swift
var capabilities = AccessoryControlDevice.Capabilities()
capabilities.insert(.noiseControl)
capabilities.insert(.spatialAudio)

// Update listening mode
func setListeningMode(_ mode: AccessoryControlDevice.ListeningMode, on device: AccessoryControlDevice) async throws {
    try await device.updateListeningMode(mode)
}
```

## Monitoring Placement State

Report hardware placement transitions (e.g. user inserts earbud) to trigger automatic audio switching:

```swift
func reportEarPlacement(inEar: Bool, device: AccessoryControlDevice) async throws {
    let placement: AccessoryControlDevice.Placement = inEar ? .inEar : .outOfEar
    try await device.updatePlacement(placement)
}
```

## Audio Routing Coordination

When earbuds are placed in-ear, iOS automatically activates the audio route if automatic switching is enabled by the user in Settings.

## Common Mistakes

- **Calling AudioAccessoryKit before AccessorySetupKit authorization**: An accessory must be paired through `ASAccessorySession` first.
- **Reporting placement changes without hardware confirmation**: Speculative placement updates disrupt active phone calls or media playback.
- **Failing to register supported capabilities**: Features like Spatial Audio or ANC fail to appear in Control Center if omitted from `Configuration.capabilities`.
- **Assuming simulator execution**: Audio accessory hardware integration requires physical testing on supported devices.

## Review Checklist

- [ ] Hardware successfully paired via `AccessorySetupKit` before registration
- [ ] `AccessoryControlDevice.Configuration` accurately declares hardware capabilities
- [ ] Ear/head placement updates sent immediately upon hardware state change
- [ ] Audio route switching tested alongside active media playback

## References

- Extended patterns (registration flow, placement monitoring, multi-device coordination): [references/audioaccessorykit-patterns.md](references/audioaccessorykit-patterns.md)
- [AudioAccessoryKit framework](https://sosumi.ai/documentation/audioaccessorykit)
- [Supporting automatic audio switching](https://sosumi.ai/documentation/audioaccessorykit/supporting-automatic-audio-switching)
- [AccessoryControlDevice](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice)
- [AccessoryControlDevice registration](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/register%28_%3A_%3A%29)
- [AccessoryControlDevice lookup](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/current%28for%3A%29)
- [AccessoryControlDevice update](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/update%28_%3A%29)
- [AccessoryControlDevice.Configuration](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/configuration-swift.struct)
- [AccessoryControlDevice.Capabilities](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/capabilities)
- [AccessoryControlDevice.Placement](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/placement)
- [AccessorySetupKit framework](https://sosumi.ai/documentation/accessorysetupkit) (prerequisite for pairing)
