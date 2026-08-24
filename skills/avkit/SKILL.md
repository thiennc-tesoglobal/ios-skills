---
name: avkit
description: "Create media playback experiences using AVKit. Use when adding video players with AVPlayerViewController, enabling Picture-in-Picture, routing media with AirPlay, using SwiftUI VideoPlayer views, configuring transport controls, displaying subtitles and closed captions, or integrating AVFoundation playback with system UI."
---

# AVKit

High-level media playback UI built on AVFoundation. Provides system-standard
video players, Picture-in-Picture, AirPlay routing, transport controls, and
subtitle/caption display. Targets Swift 6.3 / iOS 26+.

## Workflow

1. Define playback ownership, media source, audio-session policy, background behavior, and supported system controls.
2. Choose `AVPlayerViewController` for full system playback UI or SwiftUI `VideoPlayer` for simpler embedding.
3. Keep `AVPlayer` in stable state outside transient view initialization and observe readiness/errors deliberately.
4. Configure Picture in Picture, AirPlay, Now Playing, subtitles, and seeking only when the product needs them.
5. Verify interruptions, route changes, foreground/background transitions, PiP restoration, captions, and teardown.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for audio session, player controllers, `VideoPlayer`, PiP, AirPlay, controls, and subtitles.
- Read [extended AVKit patterns](references/avkit-patterns.md) for custom player UI, interstitials, background playback, error handling, and advanced hosting.

## Core Decisions

- Prefer system playback UI and delegation over subclassing `AVPlayerViewController`.
- Configure the audio session for the intended playback/background contract.
- Complete every PiP restoration callback and retain objects required by PiP.
- Keep player identity and observation lifetime stable across SwiftUI body updates.

## Common Mistakes

### DON'T: Subclass AVPlayerViewController

Apple explicitly states this is unsupported. It may cause undefined behavior or
crash on future OS versions.

```swift
// WRONG
class MyPlayerVC: AVPlayerViewController { } // Unsupported

// CORRECT: Use composition with delegation
let playerVC = AVPlayerViewController()
playerVC.delegate = coordinator
```

### DON'T: Skip audio session configuration for PiP

PiP and background playback depend on the playback audio session category and
the Audio, AirPlay, and Picture in Picture background mode.

```swift
// WRONG: Default audio session
let playerVC = AVPlayerViewController()
playerVC.player = player // PiP won't work

// CORRECT: Configure the category, then activate when playback starts
try AVAudioSession.sharedInstance().setCategory(.playback, mode: .moviePlayback)
try AVAudioSession.sharedInstance().setActive(true)
let playerVC = AVPlayerViewController()
playerVC.player = player
```

### DON'T: Forget the PiP restore delegate or its completion handler

Without `restoreUserInterfaceForPictureInPictureStopWithCompletionHandler`, the
system cannot return the user to your player. Failing to call
`completionHandler(true)` leaves the system in an inconsistent state.

```swift
// WRONG: No delegate method or missing completionHandler call
// User taps restore in PiP -> nothing happens or animation hangs

// CORRECT
func playerViewController(
    _ playerViewController: AVPlayerViewController,
    restoreUserInterfaceForPictureInPictureStopWithCompletionHandler completionHandler: @escaping (Bool) -> Void
) {
    present(playerViewController, animated: false) {
        completionHandler(true)
    }
}
```

### DON'T: Create AVPlayer in a SwiftUI view's init

Creating the player eagerly causes performance issues. SwiftUI may recreate the
view multiple times.

```swift
// WRONG: Created on every view init
struct PlayerView: View {
    let player = AVPlayer(url: videoURL) // Re-created on every view evaluation

    var body: some View { VideoPlayer(player: player) }
}

// CORRECT: Use @State and defer creation
struct PlayerView: View {
    @State private var player: AVPlayer?

    var body: some View {
        VideoPlayer(player: player)
            .task { player = AVPlayer(url: videoURL) }
    }
}
```

## Review Checklist

- [ ] Audio session category set to `.playback` with `mode: .moviePlayback`
- [ ] Audio session activation deferred until playback begins
- [ ] Audio, AirPlay, and Picture in Picture background mode added to `UIBackgroundModes`
- [ ] `AVPlayerViewController` is not subclassed
- [ ] PiP tested with supported video media, not only app/device setup
- [ ] PiP restore delegate method implemented and calls `completionHandler(true)`
- [ ] Custom PiP checks both device support and current `isPictureInPicturePossible`
- [ ] Custom PiP starts only from explicit user interaction
- [ ] `AVPlayer` deferred to `.task` in SwiftUI (not created eagerly)
- [ ] `canStartPictureInPictureAutomaticallyFromInline` set for inline players
- [ ] `requiresLinearPlayback` toggled only during required ad/legal segments
- [ ] tvOS-only skipping APIs are not used for iOS transport controls
- [ ] External playback is not disabled accidentally when AirPlay is required
- [ ] Subtitle selection tested with actual media tracks
- [ ] Video gravity set appropriately (`.resizeAspect` vs `.resizeAspectFill`)
- [ ] `isReadyForDisplay` observed before showing the player view
- [ ] Error handling for network-streamed content (HLS failures, timeouts)

## References

- Advanced patterns (custom player UI, interstitials, background playback, error handling): [references/avkit-patterns.md](references/avkit-patterns.md)
- [AVKit framework](https://sosumi.ai/documentation/avkit)
- [AVPlayerViewController](https://sosumi.ai/documentation/avkit/avplayerviewcontroller)
- [VideoPlayer (SwiftUI)](https://sosumi.ai/documentation/avkit/videoplayer)
- [AVPictureInPictureController](https://sosumi.ai/documentation/avkit/avpictureinpicturecontroller)
- [AVRoutePickerView](https://sosumi.ai/documentation/avkit/avroutepickerview)
- [AVPlaybackSpeed](https://sosumi.ai/documentation/avkit/avplaybackspeed)
- [Configuring your app for media playback](https://sosumi.ai/documentation/avfoundation/configuring-your-app-for-media-playback)
- [Adopting Picture in Picture in a Standard Player](https://sosumi.ai/documentation/avkit/adopting-picture-in-picture-in-a-standard-player)
- [Playing video content in a standard user interface](https://sosumi.ai/documentation/avkit/playing-video-content-in-a-standard-user-interface)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
