---
name: sensorkit
description: "Access ambient, motion, biometric, and interaction research data using SensorKit. Use when configuring sensor readers, handling authorization and study onboarding, fetching sample streams, managing user data deletion, or building research and clinical studies."
---

# SensorKit

Access granular ambient, motion, biometric, and interaction sensor streams for approved research and clinical studies using `SRSensorReader`. Targets Swift 6.3 / iOS 26+.

> **Entitlement Warning:** SensorKit requires Apple entitlement approval (`com.apple.developer.sensorkit.reader.allow`). SensorKit cannot be tested on standard consumer apps or simulators without approved research provisioning.

## Contents

- [Setup & Entitlements](#setup--entitlements)
- [Sensor Reader Lifecycle](#sensor-reader-lifecycle)
- [Fetching Sensor Data](#fetching-sensor-data)
- [Available Sensor Categories](#available-sensor-categories)
- [Data Deletion & User Privacy](#data-deletion--user-privacy)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Entitlements

1. Obtain the research entitlement `com.apple.developer.sensorkit.reader.allow` from Apple.
2. Add sensor usage descriptions to Info.plist corresponding to each queried sensor (e.g. `NSSensorKitUsageDescription`, `NSSensorKitUsageDescriptionAmbientLightSensor`).
3. Request authorization explicitly before instantiating readers:

```swift
import SensorKit

func requestSensorAccess(for sensors: Set<SRSensor>) async {
    let status = await SRSensorReader.requestAuthorization(for: sensors)
    // Handle authorization response
}
```

## Sensor Reader Lifecycle

Create an `SRSensorReader` per sensor type and assign an `SRSensorReaderDelegate`:

```swift
final class AmbientLightCollector: NSObject, SRSensorReaderDelegate {
    private let reader = SRSensorReader(sensor: .ambientLightSensor)

    override init() {
        super.init()
        reader.delegate = self
    }

    func start() {
        guard reader.authorizationStatus == .authorized else { return }
        reader.startRecording()
    }

    func stop() {
        reader.stopRecording()
    }
}
```

## Fetching Sensor Data

Query historical recorded samples by date interval:

```swift
func fetchSamples(from start: SRAbsoluteTime, to end: SRAbsoluteTime) {
    let request = SRFetchRequest()
    request.from = start
    request.to = end

    reader.fetch(request)
}

// SRSensorReaderDelegate
func sensorReader(_ reader: SRSensorReader, fetching request: SRFetchRequest, didFetchResult result: SRFetchResult) -> Bool {
    if let sample = result.sample as? SRAmbientLightSample {
        // Process sensor sample
    }
    return true // Return true to continue fetching remaining results
}

func sensorReader(_ reader: SRSensorReader, didCompleteFetch request: SRFetchRequest) {
    // Finished fetch
}
```

## Available Sensor Categories

- **Motion & Environment**: `.ambientLightSensor`, `.accelerometer`, `.rotationRate`, `.elevation`.
- **User Interactions**: `.keyboardMetrics`, `.deviceUsageReport`, `.messagesUsageReport`, `.phoneUsageReport`.
- **Physiological & Health**: `.speechMetrics`, `.faceMetrics`, `.wristTemperature`, `.heartRate`.

## Data Deletion & User Privacy

Research participants can delete recorded data. Honor deletion requests via `SRSensorReader`:

```swift
func purgeData(before timestamp: SRAbsoluteTime) async throws {
    let request = SRDeletionRequest()
    request.endTime = timestamp
    try await reader.delete(request)
}
```

## Common Mistakes

- **Shipping without Apple entitlement approval**: SensorKit APIs fail immediately unless signed with an approved provisioning profile.
- **Returning false in fetch delegate prematurely**: Returning `false` from `didFetchResult` halts subsequent sample delivery.
- **Forgetting per-sensor usage descriptions**: Each sensor type requires its dedicated Info.plist explanation key.
- **Querying unbounded time intervals**: Always constrain `SRFetchRequest` to bounded start and end timestamps to avoid memory exhaustion.
- **Assuming simulator support**: SensorKit does not record or simulate hardware sensor streams on iOS Simulator.

## Review Checklist

- [ ] `com.apple.developer.sensorkit.reader.allow` entitlement confirmed active
- [ ] Required sensor usage descriptions declared in Info.plist
- [ ] `requestAuthorization(for:)` called before starting reader recording
- [ ] `didFetchResult` returns `true` while iterating batch samples
- [ ] Deletion requests supported for participant privacy compliance

## References

- [Setup, sensor/delegate catalogs, and multi-sensor manager](references/setup-catalog-and-manager.md)
- [Keyboard, device, phone, visit, media, and wrist samples](references/usage-and-environment-samples.md)
- [Speech, face, temperature, ECG/PPG, deletion, and testing](references/speech-face-and-health-samples.md)
- [SensorKit framework](https://sosumi.ai/documentation/sensorkit)
- [SRSensorReader](https://sosumi.ai/documentation/sensorkit/srsensorreader)
- [SRSensor](https://sosumi.ai/documentation/sensorkit/srsensor)
- [SRDevice](https://sosumi.ai/documentation/sensorkit/srdevice)
- [SRFetchRequest](https://sosumi.ai/documentation/sensorkit/srfetchrequest)
- [Configuring your project for sensor reading](https://sosumi.ai/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [com.apple.developer.sensorkit.reader.allow](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.sensorkit.reader.allow)
