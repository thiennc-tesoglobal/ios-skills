---
name: core-haptics
description: "Builds custom tactile and synchronized audio-haptic experiences with Core Haptics, including CHHapticEngine lifecycle, transient and continuous events, dynamic parameters, parameter curves, AHAP files, and device verification. Use when system sensoryFeedback or UIFeedbackGenerator patterns cannot express the required haptic behavior."
---

# Core Haptics

Compose, play, and verify custom haptic patterns with `CoreHaptics`. Scope:
Swift 6.3, iOS 26+, and supported physical hardware.

## Contents

- [Choose the Right API](#choose-the-right-api)
- [Implementation Workflow](#implementation-workflow)
- [Capability and Fallback](#capability-and-fallback)
- [Engine Lifecycle](#engine-lifecycle)
- [Choose a Pattern Representation](#choose-a-pattern-representation)
- [Playback and Modulation](#playback-and-modulation)
- [Testing](#testing)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Choose the Right API

Use the smallest API that expresses the interaction:

| Need | Owner |
|---|---|
| Standard success, warning, selection, impact, or SwiftUI state feedback | `sensoryFeedback` or UIKit feedback generators; see `swiftui-patterns` |
| Custom waveform, sustained feedback, live modulation, or synchronized haptic/audio | This skill and Core Haptics |
| Ordinary audio playback, routing, recording, or audio-session policy | AVFAudio/AVKit guidance, not this skill |
| Controller rumble | Core Haptics controller APIs; keep controller discovery/input in the game-controller owner |

Do not introduce `CHHapticEngine` for a normal button tap. Custom haptics add lifecycle,
hardware, interruption, power, and physical-device test responsibilities.

## Implementation Workflow

1. Define the interaction intent and a non-haptic fallback.
2. Check `CHHapticEngine.capabilitiesForHardware()` before creating an engine.
3. Retain one engine for the owning feature or experience; do not create one per tap.
4. Install `stoppedHandler` and `resetHandler` before starting the engine.
5. Choose a transient event, continuous event, parameter curve, or AHAP asset.
6. Retain players that require live updates, pause/resume, looping, or seeking.
7. Stop players at the interaction boundary and manage engine idle power.
8. Validate rhythm, intensity, fallback, interruptions, and accessibility on hardware.

Load [Core Haptics patterns](references/core-haptics-patterns.md) when writing engine
ownership, programmatic events, live modulation, parameter curves, or AHAP playback.

## Capability and Fallback

Core Haptics is not universally available. Apple specifically lists devices such as
iPad, iPod touch, and Apple Vision Pro among devices without haptic feedback support.
Check capability at runtime rather than inferring it from platform or model.

```swift
import CoreHaptics

struct HapticCapability {
    let supportsHaptics: Bool
    let supportsAudio: Bool

    static var current: Self {
        let hardware = CHHapticEngine.capabilitiesForHardware()
        return Self(
            supportsHaptics: hardware.supportsHaptics,
            supportsAudio: hardware.supportsAudio
        )
    }
}
```

Keep the product action successful when haptics are unavailable. Provide visual or
audio confirmation only when it is appropriate; never make haptics the sole carrier
of state or error information.

## Engine Lifecycle

- Set handlers before `start()`.
- Treat `stoppedHandler` as an external-stop notification. It may run off the main
  thread and is not called for an explicit `stop(completionHandler:)`.
- Treat `resetHandler` as invalidation of previously prepared engine resources.
  Restart the engine and recreate any players or registered audio resources the
  feature still needs.
- Keep callback state synchronization explicit. Hop to the owning actor before
  changing UI or actor-isolated state.
- Choose one power policy: stop the engine explicitly when unused, or enable
  `isAutoShutdownEnabled` and tolerate automatic idle shutdown/restart behavior.

Do not assume foregrounding alone repairs an interrupted engine. Recovery belongs
in the engine handlers and should be idempotent.

## Choose a Pattern Representation

### Programmatic patterns

Use `CHHapticEvent` and `CHHapticPattern` when timing and values derive from live
application state or the pattern is small. A transient event is a short impulse; a
continuous event has a duration and must be stopped at the interaction boundary.

### AHAP files

Use bundled `.ahap` assets when designers need to tune a reusable sequence without
rewriting Swift. AHAP represents events, dynamic parameters, parameter curves, and
optional synchronized custom audio. Validate the asset in the app bundle and handle
load/play errors rather than silently force-unwrapping its URL.

### Static versus live changes

- `CHHapticEventParameter` defines an event's initial intensity, sharpness, or envelope.
- `CHHapticParameterCurve` schedules gradual changes as part of a pattern.
- `CHHapticDynamicParameter` changes a running player immediately.

Do not confuse event parameter identifiers such as `.hapticIntensity` with dynamic
control identifiers such as `.hapticIntensityControl`.

## Playback and Modulation

Use `makePlayer(with:)` for fixed start/stop playback. Use
`makeAdvancedPlayer(with:)` when the feature needs looping, pause/resume, seeking,
completion callbacks, or reusable granular control.

For a gesture-driven continuous haptic:

- start one retained player when the gesture begins;
- send bounded intensity and sharpness dynamic parameters to that same player;
- throttle updates to meaningful changes instead of recreating patterns per frame;
- stop the player when the gesture ends or cancels;
- recreate it after an engine reset.

Intensity and sharpness are perceptual controls, not a guarantee of identical output
across hardware. Tune on every supported device family in scope.

## Testing

Simulator can compile Core Haptics code but cannot validate the tactile result. Test
on supported physical hardware and record:

- capability-off fallback;
- cold start and repeated playback;
- background/foreground and audio interruption recovery;
- continuous gesture cancellation;
- Reduce Motion or product-level haptic preference behavior where applicable;
- audible artifacts when synchronized audio is present;
- battery impact for long-running or frequent patterns.

Compile verification proves API availability only. Product review must assess whether
the feedback is distinguishable, proportional, and not fatiguing.

## Common Mistakes

- Creating and starting a new engine for every interaction.
- Using Core Haptics when `sensoryFeedback` already expresses the intent.
- Omitting the capability check or making the action depend on haptic support.
- Installing lifecycle handlers after starting the engine.
- Mutating main-actor state directly from engine callbacks.
- Restarting the engine after reset without rebuilding retained players/resources.
- Recreating a continuous player for every drag update.
- Treating Simulator success as tactile verification.
- Playing frequent, intense feedback without a user/product preference or UX review.

## Review Checklist

- [ ] Core Haptics is justified over system feedback APIs.
- [ ] Runtime capability and a non-haptic fallback are present.
- [ ] The engine has a clear owner and is retained across playback.
- [ ] Stop and reset handlers are installed before start and are thread-safe.
- [ ] Reset recovery recreates invalidated players/resources.
- [ ] Event and dynamic parameter identifiers are used in the correct context.
- [ ] Continuous players stop on completion and cancellation.
- [ ] Engine power behavior is deliberate.
- [ ] AHAP and audio resources are bundled and error-checked.
- [ ] Physical-device and interruption verification is documented.

## References

- [Core Haptics patterns](references/core-haptics-patterns.md) — engine owner,
  transient/continuous playback, live parameters, curves, and AHAP.
- [Core Haptics](https://sosumi.ai/documentation/corehaptics)
- [Preparing your app to play haptics](https://sosumi.ai/documentation/corehaptics/preparing-your-app-to-play-haptics)
- [Updating haptic parameters in real time](https://sosumi.ai/documentation/corehaptics/updating-continuous-and-transient-haptic-parameters-in-real-time)
- [Representing patterns in AHAP files](https://sosumi.ai/documentation/corehaptics/representing-haptic-patterns-in-ahap-files)
