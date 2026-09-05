---
name: speech-recognition
description: "Transcribe live and recorded audio with the Speech framework. Use when implementing SpeechAnalyzer (iOS 26+), SpeechTranscriber, SFSpeechRecognizer, live microphone speech-to-text, audio file transcription, on-device speech models, speech recognition permissions, or custom language models."
---

# Speech Recognition

Convert live speech and prerecorded audio to text. Targets modern on-device `SpeechAnalyzer` (iOS 26+) and legacy `SFSpeechRecognizer` (iOS 10+).

## Contents

- [Permissions & Audio Session](#permissions--audio-session)
- [Modern SpeechAnalyzer (iOS 26+)](#modern-speechanalyzer-ios-26)
- [Legacy SFSpeechRecognizer](#legacy-sfspeechrecognizer)
- [On-Device Model Assets](#on-device-model-assets)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Permissions & Audio Session

Add `NSSpeechRecognitionUsageDescription` and `NSMicrophoneUsageDescription` to Info.plist. Request speech and microphone authorization before starting recording:

```swift
import Speech
import AVFAudio

func requestPermissions() async -> Bool {
    let speechAuthorized = await withCheckedContinuation { continuation in
        SFSpeechRecognizer.requestAuthorization { status in
            continuation.resume(returning: status == .authorized)
        }
    }
    guard speechAuthorized else { return false }
    return await AVAudioApplication.requestRecordPermission()
}
```

## Modern SpeechAnalyzer (iOS 26+)

`SpeechAnalyzer` delivers modular, asynchronous streaming transcription using `SpeechTranscriber`:

```swift
import Speech

final class LiveTranscriber {
    private var analyzer: SpeechAnalyzer?
    private var transcriber: SpeechTranscriber?

    func startTranscribing(format: AVAudioFormat) async throws {
        let transcriber = SpeechTranscriber(locale: Locale(identifier: "en-US"), preset: .transcription)
        let analyzer = SpeechAnalyzer(modules: [transcriber])
        self.transcriber = transcriber
        self.analyzer = analyzer

        Task {
            for try await result in transcriber.results {
                let text = result.text
                if result.isFinal {
                    print("Committed: \(text)")
                } else {
                    print("Partial: \(text)")
                }
            }
        }

        try await analyzer.start(inputFormat: format)
    }

    func appendAudio(buffer: AVAudioPCMBuffer) {
        analyzer?.append(buffer)
    }

    func stop() async throws {
        try await analyzer?.finish()
    }
}
```

## Legacy SFSpeechRecognizer

For audio file transcription and backward compatibility:

```swift
func transcribeFile(url: URL) async throws -> String {
    guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US")),
          recognizer.isAvailable else {
        throw SpeechError.unavailable
    }

    let request = SFSpeechURLRecognitionRequest(url: url)
    request.requiresOnDeviceRecognition = true

    return try await withCheckedThrowingContinuation { continuation in
        recognizer.recognitionTask(with: request) { result, error in
            if let error {
                continuation.resume(throwing: error)
            } else if let result, result.isFinal {
                continuation.resume(returning: result.bestTranscription.formattedString)
            }
        }
    }
}
```

## On-Device Model Assets

Check asset installation or download language packs before recognition:

```swift
let status = await AssetInventory.status(for: .transcription, locale: Locale(identifier: "en-US"))
if status != .installed {
    try await AssetInventory.download(for: .transcription, locale: Locale(identifier: "en-US"))
}
```

## Common Mistakes

- **Missing microphone usage description**: Omitting `NSMicrophoneUsageDescription` crashes immediately when accessing `AVAudioEngine`.
- **Conflating partial and final results**: Partial results update frequently; only commit text into data models when `result.isFinal` is true.
- **Starting multiple concurrent recognition tasks**: Always finish or cancel the previous task before launching a new recognition stream.
- **Ignoring on-device fallback failures**: If `requiresOnDeviceRecognition` is true, ensure model assets are installed via `AssetInventory`.
- **Not stopping audio engine alongside recognition**: Failing to halt `AVAudioEngine` keeps the microphone indicator active in the status bar.

## Review Checklist

- [ ] `NSSpeechRecognitionUsageDescription` and `NSMicrophoneUsageDescription` present in Info.plist
- [ ] Speech recognition authorization requested and confirmed authorized
- [ ] Audio engine input nodes and tap callbacks cleaned up upon completion
- [ ] `SpeechAnalyzer` (iOS 26+) used for modern streaming pipelines
- [ ] Transient partial results visually distinguished from finalized transcripts

## References

- SpeechAnalyzer pipelines, volatile results, and audio buffering: [references/speechanalyzer-patterns.md](references/speechanalyzer-patterns.md)
- [Speech framework](https://sosumi.ai/documentation/speech)
- [SpeechAnalyzer](https://sosumi.ai/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://sosumi.ai/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://sosumi.ai/documentation/speech/speechtranscriber/preset)
- [DictationTranscriber](https://sosumi.ai/documentation/speech/dictationtranscriber)
- [SpeechDetector](https://sosumi.ai/documentation/speech/speechdetector)
- [SFSpeechRecognizer](https://sosumi.ai/documentation/speech/sfspeechrecognizer)
- [SFSpeechAudioBufferRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechaudiobufferrecognitionrequest)
- [SFSpeechURLRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechurlrecognitionrequest)
- [SFSpeechRecognitionResult](https://sosumi.ai/documentation/speech/sfspeechrecognitionresult)
- [SFSpeechRecognitionRequest](https://sosumi.ai/documentation/speech/sfspeechrecognitionrequest)
- [AssetInventory](https://sosumi.ai/documentation/speech/assetinventory)
- [Asking Permission to Use Speech Recognition](https://sosumi.ai/documentation/speech/asking-permission-to-use-speech-recognition)
- [Recognizing Speech in Live Audio](https://sosumi.ai/documentation/speech/recognizing-speech-in-live-audio)
- [Bring advanced speech-to-text to your app with SpeechAnalyzer](https://sosumi.ai/videos/play/wwdc2025/277)
