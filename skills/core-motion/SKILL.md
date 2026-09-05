---
name: core-motion
description: "Builds sensor workflows with Core Motion for accelerometer, gyroscope, device motion, pedometer, activity recognition, altitude, headphone motion, workout motion, and submersion/depth data. Use for motion interaction, steps, activity classification, AirPods tracking, or watchOS depth features."
---

# CoreMotion

Access accelerometer, gyroscope, attitude/device motion, pedometer, altitude, and specialized sensors using Core Motion. Targets Swift 6.3 / iOS 26+.

## Contents

- [Setup & Authorization](#setup--authorization)
- [Motion Manager & Raw Sensors](#motion-manager--raw-sensors)
- [Device Motion (Attitude & Gravity)](#device-motion-attitude--gravity)
- [Pedometer & Activity Recognition](#pedometer--activity-recognition)
- [Altimeter & Specialized Sensors](#altimeter--specialized-sensors)
- [Battery & Lifecycle](#battery--lifecycle)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Authorization

Add `NSMotionUsageDescription` to Info.plist explaining why the app accesses motion sensors.

Check authorization status for managers exposing privacy controls (`CMPedometer`, `CMMotionActivityManager`, `CMAltimeter`):

```swift
import CoreMotion

guard CMMotionActivityManager.authorizationStatus() != .denied else {
    // Prompt user to enable motion permissions in Settings
    return
}
```

Raw accelerometer/gyro streams under `CMMotionManager` do not prompt for permission directly but require the usage description and throw errors on unauthorized access.

## Motion Manager & Raw Sensors

Maintain exactly **one** shared `CMMotionManager` instance per application to avoid sensor contention:

```swift
final class MotionProvider {
    static let shared = MotionProvider()
    let manager = CMMotionManager()

    func startAccelerometer() {
        guard manager.isAccelerometerAvailable else { return }
        manager.accelerometerUpdateInterval = 1.0 / 60.0 // 60 Hz
        manager.startAccelerometerUpdates(to: .main) { data, error in
            guard let accel = data?.acceleration else { return }
            // Process acceleration: x, y, z
        }
    }

    func stop() {
        manager.stopAccelerometerUpdates()
    }
}
```

## Device Motion (Attitude & Gravity)

Prefer `CMDeviceMotion` over raw sensor data. It fuses accelerometer, gyro, and magnetometer data into clean attitude, user acceleration, and gravity vectors:

```swift
manager.deviceMotionUpdateInterval = 1.0 / 60.0
manager.startDeviceMotionUpdates(using: .xArbitraryZVertical, to: .main) { motion, error in
    guard let motion else { return }
    let roll = motion.attitude.roll
    let pitch = motion.attitude.pitch
    let yaw = motion.attitude.yaw
}
```

## Pedometer & Activity Recognition

Track steps, distance, and user movement state:

```swift
let pedometer = CMPedometer()
if CMPedometer.isStepCountingAvailable() {
    pedometer.startUpdates(from: .now) { data, error in
        guard let data else { return }
        print("Steps: \(data.numberOfSteps)")
    }
}

let activityManager = CMMotionActivityManager()
if CMMotionActivityManager.isActivityAvailable() {
    activityManager.startActivityUpdates(to: .main) { activity in
        guard let activity else { return }
        if activity.walking { print("Walking") }
        if activity.running { print("Running") }
    }
}
```

## Altimeter & Specialized Sensors

- **CMAltimeter**: Track relative altitude changes or absolute barometric pressure (`startRelativeAltitudeUpdates`).
- **CMHeadphoneMotionManager**: Track head pose from AirPods for spatial audio interactions.
- **CMBatchedSensorManager (iOS 17+)**: Receive batched high-frequency workout motion data with low CPU wake overhead.
- **CMWaterSubmersionManager**: Track depth, temperature, and submersion state on supported Apple Watch hardware.

## Battery & Lifecycle

- Stop updates (`stopDeviceMotionUpdates()`) when views disappear or when the app transitions to the background.
- Select the lowest sensor update frequency adequate for your feature (e.g. 10–20 Hz for tilt detection; 60 Hz only for real-time physics/gaming).

## Common Mistakes

- **Instantiating multiple CMMotionManager objects**: Degrades system update rates and increases battery drain. Use a single shared manager.
- **Missing NSMotionUsageDescription**: The app crashes immediately upon accessing activity, pedometer, or altimeter services.
- **Not stopping updates on backgrounding**: Running motion updates indefinitely drains battery and causes system termination.
- **Using raw accelerometer for orientation**: Raw data includes gravity and user movement noise. Use `CMDeviceMotion.attitude` instead.
- **Omitting availability checks**: Always check `isAvailable` flags before calling `startUpdates`.

## Review Checklist

- [ ] `NSMotionUsageDescription` present and descriptive in Info.plist
- [ ] Single shared `CMMotionManager` instance used app-wide
- [ ] Sensor availability checked before initiating streams
- [ ] Updates explicitly halted when views dismiss or background transitions occur
- [ ] `CMDeviceMotion` used for orientation and tilt calculations instead of raw accelerometer
- [ ] Update intervals chosen conservatively to preserve battery life

## References

- Extended patterns (SwiftUI integration, batched sensor manager, headphone motion, water submersion): [references/motion-patterns.md](references/motion-patterns.md)
- [CoreMotion framework](https://sosumi.ai/documentation/coremotion)
- [CMMotionManager](https://sosumi.ai/documentation/coremotion/cmmotionmanager)
- [CMPedometer](https://sosumi.ai/documentation/coremotion/cmpedometer)
- [CMMotionActivityManager](https://sosumi.ai/documentation/coremotion/cmmotionactivitymanager)
- [CMDeviceMotion](https://sosumi.ai/documentation/coremotion/cmdevicemotion)
- [CMAltimeter](https://sosumi.ai/documentation/coremotion/cmaltimeter)
- [CMAbsoluteAltitudeData](https://sosumi.ai/documentation/coremotion/cmabsolutealtitudedata)
- [CMBatchedSensorManager](https://sosumi.ai/documentation/coremotion/cmbatchedsensormanager)
- [CMHeadphoneMotionManager](https://sosumi.ai/documentation/coremotion/cmheadphonemotionmanager)
- [CMWaterSubmersionManager](https://sosumi.ai/documentation/coremotion/cmwatersubmersionmanager)
- [Accessing submersion data](https://sosumi.ai/documentation/coremotion/accessing-submersion-data)
- [Getting processed device-motion data](https://sosumi.ai/documentation/coremotion/getting-processed-device-motion-data)
