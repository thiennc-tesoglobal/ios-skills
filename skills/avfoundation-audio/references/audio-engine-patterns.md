# Audio Engine Patterns and Recipes

Practical recipes for complex `AVAudioEngine` graphs, audio format conversion, and multi-track mixing in iOS and iPadOS.

## Multi-Track Mixer Graph

Connect multiple player nodes into a mixer node, adjust volume levels, and route into `mainMixerNode`.

```swift
import AVFAudio

@MainActor
final class MultiTrackAudioMixer {
    private let engine = AVAudioEngine()
    private let subMixer = AVAudioMixerNode()
    private var players: [AVAudioPlayerNode] = []

    func setupTracks(files: [URL]) throws {
        engine.attach(subMixer)
        engine.connect(subMixer, to: engine.mainMixerNode, format: nil)

        for fileURL in files {
            let player = AVAudioPlayerNode()
            engine.attach(player)

            let audioFile = try AVAudioFile(forReading: fileURL)
            engine.connect(player, to: subMixer, format: audioFile.processingFormat)

            player.scheduleFile(audioFile, at: nil)
            players.append(player)
        }

        try engine.start()
    }

    func playAll() {
        for player in players {
            player.play()
        }
    }

    func setTrackVolume(index: Int, volume: Float) {
        guard players.indices.contains(index) else { return }
        players[index].volume = volume
    }

    func stopAll() {
        for player in players {
            player.stop()
        }
        engine.stop()
        engine.reset()
        players.removeAll()
    }
}
```

## Adding Real-Time Audio Effects

Insert `AVAudioUnitEQ` or `AVAudioUnitTimePitch` between a player node and mixer node.

```swift
import AVFAudio

@MainActor
final class PitchEffectController {
    private let engine = AVAudioEngine()
    private let player = AVAudioPlayerNode()
    private let pitchUnit = AVAudioUnitTimePitch()

    func setup(fileURL: URL) throws {
        let audioFile = try AVAudioFile(forReading: fileURL)
        let format = audioFile.processingFormat

        engine.attach(player)
        engine.attach(pitchUnit)

        // Connect player -> pitchUnit -> mainMixer
        engine.connect(player, to: pitchUnit, format: format)
        engine.connect(pitchUnit, to: engine.mainMixerNode, format: format)

        // Pitch shift: 1200 cents = 1 octave up
        pitchUnit.pitch = 400
        pitchUnit.rate = 1.0

        try engine.start()
        player.scheduleFile(audioFile, at: nil)
        player.play()
    }

    func updatePitch(cents: Float) {
        pitchUnit.pitch = cents
    }
}
```

## Microphone Record Permission & Recording

Use modern `AVAudioApplication.requestRecordPermission()` (iOS 17+) before activating recording or installing input taps.

```swift
import AVFAudio

@MainActor
final class AudioRecorderService {
    private var recorder: AVAudioRecorder?

    func requestPermissionAndRecord(destinationURL: URL) async throws -> Bool {
        let granted = await AVAudioApplication.requestRecordPermission()
        guard granted else { return false }

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
        try session.setActive(true)

        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100.0,
            AVNumberOfChannelsKey: 2,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]

        recorder = try AVAudioRecorder(url: destinationURL, settings: settings)
        recorder?.record()
        return true
    }

    func stop() {
        recorder?.stop()
        recorder = nil
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}
```

## Format Conversion with AVAudioConverter

Convert incoming PCM buffers (e.g. 48kHz stereo) to required destination format (e.g. 16kHz mono for speech/ML models):

```swift
import AVFAudio

final class AudioBufferConverter: Sendable {
    func convert(
        buffer: AVAudioPCMBuffer,
        to targetFormat: AVAudioFormat
    ) throws -> AVAudioPCMBuffer {
        guard let converter = AVAudioConverter(from: buffer.format, to: targetFormat) else {
            throw AudioConverterError.cannotCreateConverter
        }

        let frameCapacity = AVAudioFrameCount(
            Double(buffer.frameLength) * targetFormat.sampleRate / buffer.format.sampleRate
        )

        guard let outputBuffer = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: frameCapacity) else {
            throw AudioConverterError.bufferAllocationFailed
        }

        var error: NSError?
        var isConsumed = false

        let status = converter.convert(to: outputBuffer, error: &error) { _, outStatus in
            if isConsumed {
                outStatus.pointee = .noDataNow
                return nil
            }
            isConsumed = true
            outStatus.pointee = .haveData
            return buffer
        }

        if let error {
            throw error
        }

        guard status == .haveData || status == .inputRanDry else {
            throw AudioConverterError.conversionIncomplete(status)
        }

        return outputBuffer
    }

    enum AudioConverterError: Error {
        case cannotCreateConverter
        case bufferAllocationFailed
        case conversionIncomplete(AVAudioConverterOutputStatus)
    }
}
```
