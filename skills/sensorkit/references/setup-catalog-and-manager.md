# SensorKit Setup, Catalog, and Manager

Overflow reference for the `sensorkit` skill. Contains delegate wiring,
multi-sensor management, and detailed sample type usage that exceed the main
skill file's scope.

## Entitlement and Usage-Detail Catalog

Use only values Apple approved for the study. The expanded value array covered
by this skill is:

```xml
<key>com.apple.developer.sensorkit.reader.allow</key>
<array>
    <string>ambient-light-sensor</string>
    <string>motion-accelerometer</string>
    <string>motion-rotation-rate</string>
    <string>device-usage</string>
    <string>keyboard-metrics</string>
    <string>messages-usage</string>
    <string>phone-usage</string>
    <string>visits</string>
    <string>pedometer</string>
    <string>on-wrist</string>
    <string>speech-metrics-siri</string>
    <string>speech-metrics-telephony</string>
    <string>ambient-pressure</string>
    <string>ecg</string>
    <string>ppg</string>
</array>
```

Map each requested sensor to its exact `NSSensorKitUsageDetail` key:

| Sensor family | Usage-detail key |
|---|---|
| Motion sensors | `SRSensorUsageMotion` |
| Ambient light | `SRSensorUsageAmbientLightSensor` |
| Ambient pressure | `SRSensorUsageElevation` |
| Electrocardiogram | `SRSensorUsageECG` |
| Photoplethysmogram | `SRSensorUsagePPG` |
| Heart rate | `SRSensorUsageHeartRate` |
| Wrist temperature | `SRSensorUsageWristTemperature` |

Verify newer or specialized sensors against their individual `SRSensor` pages.
ECG and PPG require both the `ecg` or `ppg` entitlement value and the matching
usage-detail entry.

## Sensor Catalog

| Category | Sensor | Sample Type |
|---|---|---|
| Device | `.deviceUsageReport` | `SRDeviceUsageReport` |
| Device | `.keyboardMetrics` | `SRKeyboardMetrics` |
| Device | `.onWristState` | `SRWristDetection` |
| Device | `.acousticSettings` | `SRAcousticSettings` |
| App activity | `.messagesUsageReport` | `SRMessagesUsageReport` |
| App activity | `.phoneUsageReport` | `SRPhoneUsageReport` |
| User activity | `.accelerometer` | `[CMRecordedAccelerometerData]` |
| User activity | `.rotationRate` | `[CMRecordedRotationRateData]` |
| User activity | `.pedometerData` | `CMPedometerData` |
| User activity | `.visits` | `SRVisit` |
| User activity | `.mediaEvents` | `SRMediaEvent` |
| User activity | `.faceMetrics` | `SRFaceMetrics` |
| User activity | `.heartRate` | `CMHighFrequencyHeartRateData` |
| User activity | `.odometer` | `CMOdometerData` |
| User activity | `.siriSpeechMetrics` | `SRSpeechMetrics` |
| User activity | `.telephonySpeechMetrics` | `SRSpeechMetrics` |
| User activity | `.wristTemperature` | `SRWristTemperatureSession` |
| User activity | `.sleepSessions` | `SRSleepSession` |
| User activity | `.photoplethysmogram` | `[SRPhotoplethysmogramSample]` |
| User activity | `.electrocardiogram` | `[SRElectrocardiogramSample]` |
| Environment | `.ambientLightSensor` | `SRAmbientLightSample` |
| Environment | `.ambientPressure` | `[CMRecordedPressureData]` |

## Delegate Method Catalog

| Delegate method | Purpose |
|---|---|
| `sensorReader(_:didChange:)` | Authorization status changed |
| `sensorReaderWillStartRecording(_:)` | Recording is about to start |
| `sensorReader(_:startRecordingFailedWithError:)` | Recording failed to start |
| `sensorReaderDidStopRecording(_:)` | Recording stopped |
| `sensorReader(_:stopRecordingFailedWithError:)` | Recording failed to stop |
| `sensorReader(_:didFetch:)` | Devices fetched |
| `sensorReader(_:fetchDevicesDidFailWithError:)` | Device fetch failed |
| `sensorReader(_:fetching:didFetchResult:)` | Sample received |
| `sensorReader(_:didCompleteFetch:)` | Fetch completed |
| `sensorReader(_:fetching:failedWithError:)` | Fetch failed |

## Full Delegate Implementation

A complete `SRSensorReaderDelegate` implementation covering all callbacks:

```swift
import SensorKit

final class SensorReaderHandler: NSObject, SRSensorReaderDelegate {

    // MARK: - Authorization

    func sensorReader(_ reader: SRSensorReader, didChange authorizationStatus: SRAuthorizationStatus) {
        switch authorizationStatus {
        case .authorized:
            reader.startRecording()
        case .denied:
            handleDenied(sensor: reader.sensor)
        case .notDetermined:
            break
        @unknown default:
            break
        }
    }

    // MARK: - Recording

    func sensorReaderWillStartRecording(_ reader: SRSensorReader) {
        print("Recording will start for \(reader.sensor)")
    }

    func sensorReader(_ reader: SRSensorReader, startRecordingFailedWithError error: any Error) {
        print("Recording failed for \(reader.sensor): \(error)")
    }

    func sensorReaderDidStopRecording(_ reader: SRSensorReader) {
        print("Recording stopped for \(reader.sensor)")
    }

    func sensorReader(_ reader: SRSensorReader, stopRecordingFailedWithError error: any Error) {
        print("Stop recording failed for \(reader.sensor): \(error)")
    }

    // MARK: - Device Fetching

    func sensorReader(_ reader: SRSensorReader, didFetch devices: [SRDevice]) {
        for device in devices {
            fetchData(for: reader, from: device)
        }
    }

    func sensorReader(_ reader: SRSensorReader, fetchDevicesDidFailWithError error: any Error) {
        print("Device fetch failed: \(error)")
    }

    // MARK: - Data Fetching

    func sensorReader(
        _ reader: SRSensorReader,
        fetching request: SRFetchRequest,
        didFetchResult result: SRFetchResult<AnyObject>
    ) -> Bool {
        processSample(result, for: reader.sensor)
        return true  // true = continue fetching, false = stop
    }

    func sensorReader(_ reader: SRSensorReader, didCompleteFetch request: SRFetchRequest) {
        print("Fetch complete for \(reader.sensor)")
    }

    func sensorReader(
        _ reader: SRSensorReader,
        fetching request: SRFetchRequest,
        failedWithError error: any Error
    ) {
        handleFetchError(error, sensor: reader.sensor)
    }

    // MARK: - Private

    private func fetchData(for reader: SRSensorReader, from device: SRDevice) {
        let request = SRFetchRequest()
        request.device = device
        // Fetch data from 3 days ago to 1 day ago (avoids 24-hour hold)
        request.from = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400 * 3)
        request.to = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400)
        reader.fetch(request)
    }

    private func handleDenied(sensor: SRSensor) {
        // Log or notify that the user denied this sensor
    }

    private func processSample(_ result: SRFetchResult<AnyObject>, for sensor: SRSensor) {
        // Route to sensor-specific processing
    }

    private func handleFetchError(_ error: any Error, sensor: SRSensor) {
        if let srError = error as? SRError {
            switch srError.code {
            case .invalidEntitlement:
                print("Missing entitlement for \(sensor)")
            case .noAuthorization:
                print("No authorization for \(sensor)")
            case .dataInaccessible:
                print("Data inaccessible for \(sensor) -- may be in holding period")
            case .fetchRequestInvalid:
                print("Invalid fetch request for \(sensor)")
            case .promptDeclined:
                print("User declined prompt for \(sensor)")
            @unknown default:
                print("Unknown error for \(sensor): \(error)")
            }
        }
    }
}
```

## Multi-Sensor Manager

Manage multiple sensors through a single coordinator:

```swift
import SensorKit

final class SensorKitManager: NSObject, SRSensorReaderDelegate {

    private var readers: [SRSensor: SRSensorReader] = [:]
    private var collectedSamples: [SRSensor: [Any]] = [:]

    private let studySensors: Set<SRSensor> = [
        .ambientLightSensor,
        .accelerometer,
        .keyboardMetrics,
        .deviceUsageReport,
        .visits
    ]

    // MARK: - Setup

    func configure() {
        for sensor in studySensors {
            let reader = SRSensorReader(sensor: sensor)
            reader.delegate = self
            readers[sensor] = reader
        }
    }

    func requestAuthorization() {
        SRSensorReader.requestAuthorization(sensors: studySensors) { error in
            if let error {
                print("Authorization failed: \(error)")
            }
        }
    }

    // MARK: - Recording

    func startAllRecording() {
        for (sensor, reader) in readers {
            guard reader.authorizationStatus == .authorized else {
                print("Skipping \(sensor) -- not authorized")
                continue
            }
            reader.startRecording()
        }
    }

    func stopAllRecording() {
        for reader in readers.values {
            reader.stopRecording()
        }
    }

    // MARK: - Fetching

    func fetchAllData(daysBack: Int = 3) {
        for reader in readers.values {
            guard reader.authorizationStatus == .authorized else { continue }
            reader.fetchDevices()
        }
    }

    // MARK: - SRSensorReaderDelegate

    func sensorReader(_ reader: SRSensorReader, didChange authorizationStatus: SRAuthorizationStatus) {
        if authorizationStatus == .authorized {
            reader.startRecording()
        }
    }

    func sensorReader(_ reader: SRSensorReader, didFetch devices: [SRDevice]) {
        for device in devices {
            let request = SRFetchRequest()
            request.device = device
            request.from = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400 * 3)
            request.to = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400)
            reader.fetch(request)
        }
    }

    func sensorReader(
        _ reader: SRSensorReader,
        fetching request: SRFetchRequest,
        didFetchResult result: SRFetchResult<AnyObject>
    ) -> Bool {
        var samples = collectedSamples[reader.sensor] ?? []
        samples.append(result.sample)
        collectedSamples[reader.sensor] = samples
        return true
    }

    func sensorReader(_ reader: SRSensorReader, didCompleteFetch request: SRFetchRequest) {
        let count = collectedSamples[reader.sensor]?.count ?? 0
        print("Fetched \(count) samples for \(reader.sensor)")
    }

    func sensorReader(
        _ reader: SRSensorReader,
        fetching request: SRFetchRequest,
        failedWithError error: any Error
    ) {
        print("Fetch error for \(reader.sensor): \(error)")
    }

    func sensorReader(_ reader: SRSensorReader, fetchDevicesDidFailWithError error: any Error) {
        print("Device fetch error for \(reader.sensor): \(error)")
    }
}
```

## Ambient Light Samples

`SRAmbientLightSample` provides lux, chromaticity, and sensor placement:

```swift
func processAmbientLight(_ result: SRFetchResult<AnyObject>) {
    guard let sample = result.sample as? SRAmbientLightSample else { return }

    // Illuminance in lux
    let luxValue = sample.lux.value  // Double
    let luxUnit = sample.lux.unit    // UnitIlluminance

    // Chromaticity coordinates (CIE 1931 xy)
    let chromX = sample.chromaticity.x  // Float32
    let chromY = sample.chromaticity.y  // Float32

    // Sensor placement relative to light source
    switch sample.placement {
    case .frontTop:
        print("Light from above front")
    case .frontBottom:
        print("Light from below front")
    case .frontLeft, .frontRight:
        print("Light from side")
    case .frontTopLeft, .frontTopRight:
        print("Light from upper corner")
    case .frontBottomLeft, .frontBottomRight:
        print("Light from lower corner")
    case .unknown:
        print("Unknown placement")
    @unknown default:
        break
    }

    print("Ambient light: \(luxValue) lux, chromaticity: (\(chromX), \(chromY))")
}
```
