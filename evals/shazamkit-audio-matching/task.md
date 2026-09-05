# ShazamKit Audio Recognition Engine

You are building an ambient music identification feature in a modern iOS application.

Implement an audio recognition manager in Swift using ShazamKit conforming to these requirements:
1. Provide an implementation using `SHManagedSession` (iOS 17+) that streams recognition results asynchronously via `session.results`.
2. Extract the matched song title, artist, and artwork URL when a match is found, and handle the `.noMatch` state gracefully.
3. Provide a fallback or alternative workflow for matching against an `SHCustomCatalog` of proprietary audio tracks.
4. Explain how audio signatures are generated locally with `SHSignatureGenerator` without transmitting raw user microphone audio off-device.
5. Declare required permissions in `Info.plist` (`NSMicrophoneUsageDescription`).
