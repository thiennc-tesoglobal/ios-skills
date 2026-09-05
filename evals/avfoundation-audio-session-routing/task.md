# Audio Session Configuration and Interruption Handling

You are building an audio playback engine for a modern iOS podcast application. The application streams voice audio in the background and must handle interruptions and peripheral disconnection gracefully.

Implement an `AudioPlaybackSessionController` in Swift conforming to the following requirements:
1. Configure `AVAudioSession` with the `.playback` category and `.spokenAudio` mode.
2. Ensure audio session activation is deferred until playback actually starts, and deactivates notifying other apps when stopped.
3. Observe `AVAudioSession.interruptionNotification` to pause playback when an interruption begins and check `.shouldResume` before resuming when the interruption ends.
4. Observe `AVAudioSession.routeChangeNotification` and pause playback whenever the output route becomes unavailable (`.oldDeviceUnavailable`).
5. Structure code safely for modern Swift concurrency using actors or `@MainActor`.
