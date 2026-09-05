---
name: avfoundation-audio
description: "Configure AVAudioSession categories, modes, route changes, interruptions, and build low-latency AVAudioEngine node graphs for recording, mixing, and audio processing in iOS and iPadOS apps."
---

# AVFoundation Audio

Configure `AVAudioSession` and construct `AVAudioEngine` node graphs for playback, recording, real-time DSP, and multi-track audio pipelines in iOS and iPadOS.

## Contents

- [Audio Session Configuration](#audio-session-configuration)
- [Interruption & Route Change Handling](#interruption--route-change-handling)
- [AVAudioEngine Architecture](#avaudioengine-architecture)
- [Live Microphone Capture & Taps](#live-microphone-capture--taps)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

---

## Audio Session Configuration

`AVAudioSession` coordinates app audio with the system audio subsystem. Defer activation until playback or recording begins to avoid prematurely silencing background audio.

```swift
import AVFAudio

@MainActor
final class AudioSessionManager {
    static let shared = AudioSessionManager()

    func configurePlayback() throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playback, mode: .moviePlayback, options: [])
        try session.setActive(true)
    }

    func configureRecording() throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(
            .playAndRecord,
            mode: .measurement,
            options: [.defaultToSpeaker, .allowBluetoothHFP]
        )
        try session.setActive(true)
    }

    func deactivate() throws {
        try AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}
```

### Key Categories and Modes

- `.playback`: Media playback that continues when the Ring/Silent switch is set to silent or screen locks.
- `.record`: Pure recording without playback; silences background audio.
- `.playAndRecord`: Bidirectional audio (VoIP, chat, audio recording while monitoring). Use `.defaultToSpeaker` to prevent routing audio only to receiver.
- `.ambient`: Mixes with other audio apps; silenced by Ring/Silent switch.

---

## Interruption & Route Change Handling

Always observe `AVAudioSession.interruptionNotification` and `AVAudioSession.routeChangeNotification` asynchronously using `NotificationCenter` async sequences.

```swift
import AVFAudio

actor AudioNotificationObserver {
    private var task: Task<Void, Never>?

    func startObserving(
        onInterruption: @Sendable @escaping (Bool) -> Void,
        onPauseForRouteLoss: @Sendable @escaping () -> Void
    ) {
        task = Task {
            for await notification in NotificationCenter.default.notifications(named: AVAudioSession.interruptionNotification) {
                guard let userInfo = notification.userInfo,
                      let typeValue = userInfo[AVAudioSessionInterruptionTypeKey] as? UInt,
                      let type = AVAudioSession.InterruptionType(rawValue: typeValue) else { continue }

                switch type {
                case .began:
                    onInterruption(true)
                case .ended:
                    let optionsValue = userInfo[AVAudioSessionInterruptionOptionKey] as? UInt ?? 0
                    let shouldResume = AVAudioSession.InterruptionOptions(rawValue: optionsValue).contains(.shouldResume)
                    onInterruption(!shouldResume)
                @unknown default:
                    break
                }
            }
        }
    }

    func stopObserving() {
        task?.cancel()
        task = nil
    }
}
```

Pause playback immediately when `AVAudioSessionRouteChangeReasonKey` indicates `.oldDeviceUnavailable` (e.g., headphones disconnected).

---

## AVAudioEngine Architecture

`AVAudioEngine` coordinates a graph of `AVAudioNode` instances (player nodes, mixer nodes, effect nodes) connected together.

```swift
import AVFAudio

@MainActor
final class AudioEngineController {
    private let engine = AVAudioEngine()
    private let playerNode = AVAudioPlayerNode()

    func setupGraph(audioFileURL: URL) throws {
        let file = try AVAudioFile(forReading: audioFileURL)
        let format = file.processingFormat

        engine.attach(playerNode)
        engine.connect(playerNode, to: engine.mainMixerNode, format: format)

        try engine.start()

        playerNode.scheduleFile(file, at: nil) {
            // Playback completed
        }
        playerNode.play()
    }

    func stop() {
        playerNode.stop()
        engine.stop()
        engine.reset()
    }
}
```

---

## Live Microphone Capture & Taps

To analyze or stream microphone PCM buffers, install an audio tap on the `inputNode`. Always remove previous taps before installing a new tap or tearing down.

```swift
import AVFAudio

final class MicrophoneTapManager: Sendable {
    private let engine = AVAudioEngine()

    func startTapping(bufferHandler: @escaping @Sendable (AVAudioPCMBuffer, AVAudioTime) -> Void) throws {
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.removeTap(onBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, time in
            bufferHandler(buffer, time)
        }

        engine.prepare()
        try engine.start()
    }

    func stopTapping() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
    }
}
```

---

## Common Mistakes

- **Activating session at app launch:** Causes unwanted background audio suspension. Deactivate or defer activation until the user requests audio.
- **Mismatching audio formats in engine connections:** Connecting nodes with incompatible sample rates or channel counts without a mixer or format converter throws an exception.
- **Duplicate tap installation:** Calling `installTap(onBus:bufferSize:format:)` on a bus that already has a tap installed crashes at runtime. Always call `removeTap(onBus:)` first.
- **Ignoring route loss:** Failing to pause playback when headphones disconnect blares audio through built-in speakers.
- **Retaining AVAudioEngine across session resets:** Handle `AVAudioEngineConfigurationChange` by rebuilding graph or restarting the engine.

---

## Review Checklist

- [ ] Does `AVAudioSession` configuration set appropriate category, mode, and options (`.defaultToSpeaker`, `.allowBluetoothHFP`)?
- [ ] Is `setActive(true)` deferred until audio playback/recording actually starts?
- [ ] Is `setActive(false, options: .notifyOthersOnDeactivation)` invoked when stopping to restore other audio apps?
- [ ] Are route changes observed, specifically pausing on `.oldDeviceUnavailable`?
- [ ] Are interruptions (`.began` and `.ended` with `.shouldResume`) handled gracefully?
- [ ] Does microphone capture check and request `AVAudioApplication.requestRecordPermission()` prior to starting?
- [ ] Are audio node taps properly removed prior to re-installing or stopping?

---

## References

- [Audio Engine Patterns](references/audio-engine-patterns.md) — Advanced mixer graphs, EQ, audio conversion, and unit tests.
- [AVFAudio Documentation](https://sosumi.ai/documentation/avfaudio) — Official Apple AVFAudio API reference.
- [AVAudioSession Guide](https://sosumi.ai/documentation/avfaudio/avaudiosession) — Audio session lifecycle, routing, and categories.
- [AVAudioEngine Guide](https://sosumi.ai/documentation/avfaudio/avaudioengine) — Real-time audio node processing graph.
