---
name: shazamkit
description: "Recognize music and audio with ShazamKit using SHManagedSession, SHSession, SHCustomCatalog, and SHSignatureGenerator for live microphone matching and custom audio catalogs in iOS apps."
---

# ShazamKit

Match recorded or ambient audio against the Shazam catalog or custom audio catalogs using `SHManagedSession`, `SHSession`, and `SHCustomCatalog` in iOS and iPadOS.

## Contents

- [Modern Audio Recognition with SHManagedSession](#modern-audio-recognition-with-shmanagedsession)
- [Real-Time Matching with SHSession](#real-time-matching-with-shsession)
- [Custom Catalogs with SHCustomCatalog](#custom-catalogs-with-shcustomcatalog)
- [Signature Generation with SHSignatureGenerator](#signature-generation-with-shsignaturegenerator)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

---

## Modern Audio Recognition with SHManagedSession

On iOS 17+, `SHManagedSession` encapsulates audio recording, session management, and recognition into an async stream of `SHManagedSession.Item` results.

```swift
import ShazamKit

@MainActor
@Observable
final class AudioRecognitionViewModel {
    private let managedSession = SHManagedSession()
    var currentMatch: SHMatchedMediaItem?
    var isListening = false

    func startListening() async {
        isListening = true
        defer { isListening = false }

        for await item in managedSession.results {
            switch item {
            case .match(let match):
                if let mediaItem = match.mediaItems.first {
                    self.currentMatch = mediaItem
                }
            case .noMatch:
                // Signature didn't match any known audio
                break
            @unknown default:
                break
            }
        }
    }

    func stopListening() {
        managedSession.cancel()
        isListening = false
    }
}
```

---

## Real-Time Matching with SHSession

When manual control over the `AVAudioEngine` pipeline or custom catalogs is required, feed PCM buffers directly to `SHSession`.

```swift
import ShazamKit
import AVFAudio

final class ManualShazamMatcher: NSObject, SHSessionDelegate, @unchecked Sendable {
    private let session: SHSession
    private let engine = AVAudioEngine()

    init(catalog: SHCustomCatalog? = nil) {
        if let catalog {
            self.session = SHSession(catalog: catalog)
        } else {
            self.session = SHSession()
        }
        super.init()
        self.session.delegate = self
    }

    func startMatching() throws {
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.removeTap(onBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 2048, format: format) { [weak self] buffer, audioTime in
            self?.session.matchStreamingBuffer(buffer, at: audioTime)
        }

        try engine.start()
    }

    func stopMatching() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
    }

    // MARK: - SHSessionDelegate

    func session(_ session: SHSession, didFind match: SHMatch) {
        guard let item = match.mediaItems.first else { return }
        print("Matched: \(item.title ?? "Unknown") by \(item.artist ?? "Unknown")")
    }

    func session(_ session: SHSession, didNotFindMatchFor signature: SHSignature, error: Error?) {
        // No match found
    }
}
```

---

## Custom Catalogs with SHCustomCatalog

Match non-commercial audio, museum exhibits, podcast episodes, or proprietary assets by building an `SHCustomCatalog`.

```swift
import ShazamKit

final class CustomCatalogService {
    let catalog = SHCustomCatalog()

    func addTrack(signature: SHSignature, title: String, artist: String) throws {
        let mediaItem = SHMediaItem(properties: [
            .title: title,
            .artist: artist
        ])
        try catalog.addReferenceSignature(signature, representing: [mediaItem])
    }

    func exportCatalog(to fileURL: URL) throws {
        try catalog.write(to: fileURL)
    }

    func loadCatalog(from fileURL: URL) throws {
        try catalog.add(from: fileURL)
    }
}
```

---

## Signature Generation with SHSignatureGenerator

Generate compact, privacy-preserving audio signatures from PCM buffers without sending raw audio to servers.

```swift
import ShazamKit
import AVFAudio

final class SignatureGeneratorHelper {
    func generateSignature(from audioFile: AVAudioFile) throws -> SHSignature {
        let generator = SHSignatureGenerator()
        let format = audioFile.processingFormat
        let buffer = AVAudioPCMBuffer(
            pcmFormat: format,
            frameCapacity: AVAudioFrameCount(audioFile.length)
        )!

        try audioFile.read(into: buffer)
        try generator.append(buffer, at: nil)

        return generator.signature()
    }
}
```

---

## Common Mistakes

- **Missing NSMicrophoneUsageDescription:** Attempting to record ambient audio without microphone permission in `Info.plist` crashes at launch.
- **Passing incompatible audio buffer formats:** ShazamKit requires mono or stereo PCM buffers; multi-channel audio must be converted first.
- **Ignoring no-match returns:** An `SHSession` triggers `session(_:didNotFindMatchFor:error:)` frequently during silence or unrecognized songs; handle this without treating it as a fatal failure.
- **Reusing depleted signature generators:** Once `generator.signature()` is called, the signature generator is finished; create a new instance for subsequent audio segments.
- **Retaining taps on AVAudioEngine:** Always remove the tap before deallocating `AVAudioEngine` to prevent runtime crashes.

---

## Review Checklist

- [ ] Is `NSMicrophoneUsageDescription` declared in `Info.plist` for live listening?
- [ ] Is `SHManagedSession` used for straightforward iOS 17+ ambient audio recognition?
- [ ] Are audio buffers formatted correctly before calling `session.matchStreamingBuffer(_:at:)`?
- [ ] Does `SHSessionDelegate` implement both `didFind` and `didNotFindMatchFor`?
- [ ] Are custom catalogs loaded from `.shazamcatalog` files or initialized with valid reference signatures?
- [ ] Is `engine.inputNode.removeTap(onBus: 0)` called when listening concludes?

---

## References

- [ShazamKit Patterns](references/shazamkit-patterns.md) — Custom catalog bundling, offline signatures, and sync offset tracking.
- [ShazamKit Documentation](https://sosumi.ai/documentation/shazamkit) — Official Apple ShazamKit API reference.
- [SHManagedSession Guide](https://sosumi.ai/documentation/shazamkit/shmanagedsession) — Modern async sequence audio recognition.
- [SHCustomCatalog Guide](https://sosumi.ai/documentation/shazamkit/shcustomcatalog) — Building and bundling custom audio reference catalogs.
