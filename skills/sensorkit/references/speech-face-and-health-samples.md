# SensorKit Speech, Face, and Health Samples

Read this reference only when the task matches the sections below.

## Speech Metrics

`SRSpeechMetrics` provides audio level, speech recognition, sound classification,
and speech expression data from Siri and phone calls:

```swift
func processSpeechMetrics(_ result: SRFetchResult<AnyObject>) {
    guard let metrics = result.sample as? SRSpeechMetrics else { return }

    let sessionID = metrics.sessionIdentifier
    let timestamp = metrics.timestamp
    let timeSinceStart = metrics.timeSinceAudioStart

    // Audio level
    if let audioLevel = metrics.audioLevel {
        let loudness = audioLevel.loudness
        let timeRange = audioLevel.timeRange
        print("Audio level: \(loudness) dB")
    }

    // Speech expression (mood/valence analysis)
    if let expression = metrics.speechExpression {
        let confidence = expression.confidence
        let mood = expression.mood
        let valence = expression.valence
        let activation = expression.activation
        let dominance = expression.dominance
        print("Expression -- mood: \(mood), valence: \(valence), confidence: \(confidence)")
    }

    // Speech recognition results
    if let recognition = metrics.speechRecognition {
        let text = recognition.bestTranscription.formattedString
        print("Recognized: \(text)")
    }

    // Sound classification
    if let classification = metrics.soundClassification {
        for result in classification.classifications {
            print("Sound: \(result.identifier) (\(result.confidence))")
        }
    }
}
```

## Face Metrics

`SRFaceMetrics` provides face anchor data and expression analysis. Requires
a device with a TrueDepth camera (Face ID).

```swift
func processFaceMetrics(_ result: SRFetchResult<AnyObject>) {
    guard let face = result.sample as? SRFaceMetrics else { return }

    let sessionID = face.sessionIdentifier
    let context = face.context

    // Context indicates what triggered the capture
    if context.contains(.deviceUnlock) {
        print("Face captured during device unlock")
    }
    if context.contains(.messagingAppUsage) {
        print("Face captured during messaging")
    }

    // Face expressions
    for expression in face.wholeFaceExpressions {
        print("Expression \(expression.identifier): \(expression.value)")
    }

    for expression in face.partialFaceExpressions {
        print("Partial \(expression.identifier): \(expression.value)")
    }

    // ARKit face anchor (full blend shapes)
    let anchor = face.faceAnchor
    let blendShapes = anchor.blendShapes
    if let smile = blendShapes[.mouthSmileLeft] {
        print("Left smile: \(smile)")
    }
}
```

## Wrist Temperature

The `.wristTemperature` stream returns `SRWristTemperatureSession` samples.
Each session contains `SRWristTemperature` readings.

```swift
func processWristTemperature(_ result: SRFetchResult<AnyObject>) {
    guard let session = result.sample as? SRWristTemperatureSession else { return }

    print("Temperature session: \(session.startDate), duration: \(session.duration)s")

    for temp in session.temperatures {
        let timestamp = temp.timestamp
        let value = temp.value         // Measurement<UnitTemperature>, in Celsius
        let error = temp.errorEstimate // Measurement<UnitTemperature>

        // Check conditions that affect accuracy
        let condition = temp.condition
        if condition.contains(.offWrist) {
            print("Off wrist -- skip reading")
            continue
        }
        if condition.contains(.onCharger) {
            print("On charger -- reduced accuracy")
        }
        if condition.contains(.inMotion) {
            print("In motion -- reduced accuracy")
        }

        let celsius = value.converted(to: .celsius).value
        let errorC = error.converted(to: .celsius).value
        print("Temp at \(timestamp): \(celsius)C +/- \(errorC)C")
    }
}
```

## Electrocardiogram and PPG

### ECG Data

```swift
func processECG(_ result: SRFetchResult<AnyObject>) {
    guard let samples = result.sample as? [SRElectrocardiogramSample] else { return }

    for sample in samples {
        let frequency = sample.frequency
        let session = sample.session
        let isGuided = session.sessionGuidance == .guided

        // ECG voltage data points -- skip invalid readings
        for dataPoint in sample.data {
            guard !dataPoint.flags.contains(.signalInvalid) else { continue }
            let microvolts = dataPoint.value.converted(to: .microvolts).value
            print("ECG: \(microvolts) uV, guided: \(isGuided), crown: \(dataPoint.flags.contains(.crownTouched))")
        }
    }
}
```

### PPG Data

```swift
func processPPG(_ result: SRFetchResult<AnyObject>) {
    guard let samples = result.sample as? [SRPhotoplethysmogramSample] else { return }

    for sample in samples {
        // Usage: .foregroundHeartRate, .foregroundBloodOxygen, .deepBreathing, .backgroundSystem
        for usage in sample.usage {
            print("PPG usage: \(usage)")
        }

        // Optical sensor data with signal quality checks
        for optical in sample.opticalSamples {
            let wavelength = optical.nominalWavelength
            let reflectance = optical.normalizedReflectance
            let hasIssues = optical.conditions.contains {
                $0 == .signalSaturation || $0 == .unreliableNoise
            }
            if !hasIssues, let reflectance {
                print("Reflectance: \(reflectance) at \(wavelength)")
            }
        }
    }
}
```

## SRAbsoluteTime Utilities

`SRAbsoluteTime` wraps `CFAbsoluteTime` for SensorKit time ranges:

```swift
let now = SRAbsoluteTime.current()
let twoDaysAgo = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400 * 2)
let cfTime = now.toCFAbsoluteTime()
let date = Date(timeIntervalSinceReferenceDate: cfTime)

func buildWeekFetchRequest(for device: SRDevice) -> SRFetchRequest {
    let request = SRFetchRequest()
    request.device = device
    request.from = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400 * 7)
    request.to = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400)
    return request
}
```

## Deletion Records

The framework deletes sensor data for various reasons. Handle `SRDeletionRecord`
in the fetch results delegate:

```swift
func processDeletionRecord(_ result: SRFetchResult<AnyObject>) {
    guard let deletion = result.sample as? SRDeletionRecord else { return }
    // Reasons: .userInitiated, .systemInitiated, .lowDiskSpace, .ageLimit, .noInterestedClients
    print("Data deleted (\(deletion.reason)): \(deletion.startTime) to \(deletion.endTime)")
}
```

## Testing Considerations

SensorKit has significant constraints for testing:

- **No Simulator support.** SensorKit requires physical hardware. All testing
  must happen on device.
- **Entitlement required.** Without the Apple-granted entitlement, the framework
  returns `SRError.invalidEntitlement` for all operations.
- **24-hour data delay.** Newly recorded data is unavailable for 24 hours.
  Automated test flows must account for this holding period.
- **User interaction required.** Authorization requires the user to interact with
  the Research Sensor & Usage Data sheet. This cannot be automated.
- **Conditional sensor availability.** Some sensors (wrist temperature, ECG, PPG)
  require Apple Watch. Others (face metrics) require TrueDepth camera. Test on
  devices that have the sensors the study uses.
- **Data volume.** Keyboard metrics and device usage reports can be large. Profile
  memory usage when processing bulk fetches.
- **Background execution.** SensorKit recording continues in the background
  without special background mode configuration. The framework manages sensor
  activation independently of app lifecycle.
