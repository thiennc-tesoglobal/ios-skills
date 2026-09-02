# Core Haptics Patterns

Load this reference when implementing engine ownership, custom events, live
modulation, parameter curves, or AHAP playback.

## Contents

- [Retained Engine Owner](#retained-engine-owner)
- [Transient Event](#transient-event)
- [Continuous Gesture Feedback](#continuous-gesture-feedback)
- [Parameter Curve](#parameter-curve)
- [AHAP Playback](#ahap-playback)
- [Verification Notes](#verification-notes)

## Retained Engine Owner

Keep the engine and reusable players together. Engine callbacks are not guaranteed to
arrive on the main thread, so hop to the owner before changing its state.

```swift
import CoreHaptics

@MainActor
final class HapticEngineController {
    private var engine: CHHapticEngine?
    private var continuousPlayer: (any CHHapticPatternPlayer)?

    var isSupported: Bool {
        CHHapticEngine.capabilitiesForHardware().supportsHaptics
    }

    func prepare() throws {
        guard isSupported, engine == nil else { return }

        let newEngine = try CHHapticEngine()
        newEngine.isAutoShutdownEnabled = true
        newEngine.stoppedHandler = { reason in
            Task { @MainActor [weak self] in
                self?.handleStop(reason)
            }
        }
        newEngine.resetHandler = {
            Task { @MainActor [weak self] in
                try? self?.recoverAfterReset()
            }
        }

        engine = newEngine
        try newEngine.start()
    }

    func stop() {
        continuousPlayer = nil
        engine?.stop()
        engine = nil
    }

    private func handleStop(_ reason: CHHapticEngine.StoppedReason) {
        continuousPlayer = nil
    }

    private func recoverAfterReset() throws {
        guard let engine else { return }
        continuousPlayer = nil
        try engine.start()
        // Recreate players and re-register audio resources needed by active UI.
    }
}
```

If automatic shutdown conflicts with precise media timing, leave it disabled and
explicitly start/stop the engine at the experience boundary.

## Transient Event

Use a transient event for a custom impulse that a standard feedback generator cannot
represent.

```swift
extension HapticEngineController {
    func playTap(intensity: Float, sharpness: Float) throws {
        guard isSupported else { return }
        try prepare()
        guard let engine else { return }

        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [
                .init(parameterID: .hapticIntensity, value: intensity),
                .init(parameterID: .hapticSharpness, value: sharpness),
            ],
            relativeTime: 0
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        let player = try engine.makePlayer(with: pattern)
        try player.start(atTime: CHHapticTimeImmediate)
    }
}
```

Clamp values derived from app state to the valid range before constructing parameters.

## Continuous Gesture Feedback

Start one player and modulate it. Recreating the pattern for every pointer update adds
latency and loses playback continuity.

```swift
extension HapticEngineController {
    func beginContinuousFeedback() throws {
        guard isSupported else { return }
        try prepare()
        guard let engine else { return }

        let event = CHHapticEvent(
            eventType: .hapticContinuous,
            parameters: [
                .init(parameterID: .hapticIntensity, value: 1),
                .init(parameterID: .hapticSharpness, value: 0.5),
            ],
            relativeTime: 0,
            duration: 30
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        continuousPlayer = try engine.makePlayer(with: pattern)
        try continuousPlayer?.start(atTime: CHHapticTimeImmediate)
    }

    func updateContinuousFeedback(intensity: Float, sharpness: Float) throws {
        let parameters = [
            CHHapticDynamicParameter(
                parameterID: .hapticIntensityControl,
                value: max(0, min(1, intensity)),
                relativeTime: 0
            ),
            CHHapticDynamicParameter(
                parameterID: .hapticSharpnessControl,
                value: max(-1, min(1, sharpness)),
                relativeTime: 0
            ),
        ]
        try continuousPlayer?.sendParameters(parameters, atTime: CHHapticTimeImmediate)
    }

    func endContinuousFeedback() throws {
        try continuousPlayer?.stop(atTime: CHHapticTimeImmediate)
        continuousPlayer = nil
    }
}
```

The long event duration is only a ceiling. Always stop on gesture end, cancellation,
view disappearance, and ownership teardown.

## Parameter Curve

Use a curve when the modulation is known in advance and should interpolate smoothly.

```swift
let event = CHHapticEvent(
    eventType: .hapticContinuous,
    parameters: [
        .init(parameterID: .hapticIntensity, value: 1),
        .init(parameterID: .hapticSharpness, value: 0.2),
    ],
    relativeTime: 0,
    duration: 1
)

let fade = CHHapticParameterCurve(
    parameterID: .hapticIntensityControl,
    controlPoints: [
        .init(relativeTime: 0, value: 1),
        .init(relativeTime: 0.7, value: 0.5),
        .init(relativeTime: 1, value: 0),
    ],
    relativeTime: 0
)

let pattern = try CHHapticPattern(events: [event], parameterCurves: [fade])
```

For a value that depends on live touch or physics, send dynamic parameters instead.

## AHAP Playback

AHAP is appropriate for reusable designer-tuned patterns and synchronized custom
audio. Treat it as a bundled input that can fail to load.

```swift
extension HapticEngineController {
    func playAHAP(named name: String, bundle: Bundle = .main) throws {
        guard isSupported else { return }
        try prepare()
        guard let engine else { return }

        guard let url = bundle.url(forResource: name, withExtension: "ahap") else {
            throw CocoaError(.fileNoSuchFile)
        }
        try engine.playPattern(from: url)
    }
}
```

Use an advanced player when AHAP playback needs looping, pause/resume, seeking, or a
completion callback. After an engine reset, recreate the player and any registered
custom audio resources.

## Verification Notes

- Confirm the target contains each `.ahap` and referenced audio resource.
- Compile against the minimum supported SDK and the current beta SDK separately.
- Run the capability-off path even if the primary test phone supports haptics.
- Test interruptions, backgrounding, rapid repetition, cancellation, and teardown.
- Compare at least the weakest and strongest supported device in product scope.
- Record tactile acceptance as device evidence; Simulator is compile/UI evidence only.
