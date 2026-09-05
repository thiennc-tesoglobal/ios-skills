# DockKit Error Handling and Testing Patterns

Use this reference when handling DockKit error states, rate limit backoffs, and writing unit tests with mock dock accessories in Swift.

## Contents

- [Error Handling](#error-handling)
- [Testing Patterns](#testing-patterns)

---

## Error Handling

### DockKitError Cases

| Error | Cause | Recovery |
|---|---|---|
| `.notConnected` | No accessory is docked | Wait for `.docked` state |
| `.notSupported` | Operation not available | Check framework availability |
| `.notSupportedByDevice` | Device lacks DockKit support | Degrade gracefully |
| `.invalidParameter` | Bad input value | Validate before calling |
| `.cameraTCCMissing` | Camera terms or authorization missing | Explain the camera access requirement |
| `.frameRateTooHigh` | `track()` exceeds 30 fps, or `animate` / `setOrientation` exceeds 2 calls per second | Reduce call frequency |
| `.frameRateTooLow` | Observations below 10 fps | Increase call frequency |
| `.noSubjectFound` | No trackable subject detected | Show user guidance |

### Guarding API Calls

```swift
func safeTrack(
    observations: [DockAccessory.Observation],
    cameraInfo: DockAccessory.CameraInformation,
    accessory: DockAccessory
) async {
    do {
        try await accessory.track(observations, cameraInformation: cameraInfo)
    } catch let error as DockKitError {
        switch error {
        case .notConnected:
            // Accessory disconnected, stop tracking loop
            break
        case .frameRateTooHigh:
            // Throttle observation delivery
            break
        case .frameRateTooLow:
            // Speed up frame processing
            break
        case .noSubjectFound:
            // No subject in observations, continue
            break
        default:
            break
        }
    } catch {
        // Unexpected error
    }
}
```

## Testing Patterns

### Conditional DockKit Integration

DockKit requires physical hardware. Use conditional compilation or
runtime checks to keep the app functional without a dock:

```swift
#if canImport(DockKit)
import DockKit
#endif

final class DockController {
    var isDockKitAvailable: Bool {
        #if canImport(DockKit)
        return true
        #else
        return false
        #endif
    }

    func startTracking() async {
        #if canImport(DockKit)
        do {
            for await stateChange in try DockAccessoryManager.shared.accessoryStateChanges {
                // Handle state changes
            }
        } catch {
            // DockKit not available on this device
        }
        #endif
    }
}
```

### Mock Accessory for UI Development

When building UI without hardware, mock the accessory state:

```swift
@Observable
final class MockDockViewModel {
    var isConnected = true
    var accessoryName: String? = "Mock DockKit Stand"
    var batteryLevel: Double? = 0.75
    var isCharging = false
    var trackingMode = "System"

    // Use in SwiftUI previews
    func simulateDisconnect() {
        isConnected = false
        accessoryName = nil
        batteryLevel = nil
    }
}
```
