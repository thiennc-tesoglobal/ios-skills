---
name: dockkit
description: "Control motorized camera docks and enable intelligent subject tracking using DockKit. Use when discovering DockKit-compatible accessories, implementing camera subject tracking for faces or bodies, controlling dock motors for pan and tilt, configuring framing behavior, setting regions of interest, or building video apps with automatic camera tracking."
---

# DockKit

Framework for integrating with motorized camera stands and gimbals that
physically track subjects by rotating the iPhone. DockKit handles motor
control, subject detection, and framing so camera apps get 360-degree pan
and 90-degree tilt tracking with no additional code. Apps can override
system tracking to supply custom observations, control motors directly,
or adjust framing. iOS 17+, Swift 6.3.

## Workflow

1. Gate the feature on DockKit availability and a connected compatible accessory; plan physical-device verification.
2. Start and retain the accessory session, observe lifecycle events, and choose system tracking or custom tracking.
3. For custom tracking, provide observations at the supported cadence with valid camera geometry and confidence.
4. Disable system tracking before direct motor commands, enforce limits, and restore the intended mode afterward.
5. Verify disconnect/reconnect, tracking loss, subject changes, thermal/battery state, and cancellation.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for accessory discovery, system/custom tracking, framing, motor control, animations, events, and battery state.
- Read [extended DockKit patterns](references/dockkit-patterns.md) for Vision integration, service architecture, observation pipelines, and custom animations.

## Core Decisions

- Do not mix system subject tracking and direct motor control concurrently.
- Treat camera intrinsics, orientation, and observation coordinates as explicit inputs.
- Rate-limit tracking observations and motor/animation commands.
- Restore safe tracking state after lifecycle transitions and failures.

## Common Mistakes

### DON'T: Control motors without disabling system tracking

```swift
// WRONG -- system tracking fights manual commands
try await accessory.setAngularVelocity(velocity)

// CORRECT -- disable system tracking first
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
try await accessory.setAngularVelocity(velocity)
```

### DON'T: Assume tracking state persists across lifecycle events

```swift
// WRONG -- state may have reset after backgrounding
func applicationDidBecomeActive() {
    // Assume custom tracking is still active
}

// CORRECT -- re-set tracking state on foreground
func applicationDidBecomeActive() {
    Task {
        try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
    }
}
```

### DON'T: Call track() outside the recommended rate

```swift
// WRONG -- calling once per second is too slow
try await accessory.track(observations, cameraInformation: cameraInfo)
// (called at 1 fps)

// CORRECT -- call at 10-30 fps
// Hook into AVCaptureVideoDataOutputSampleBufferDelegate for per-frame calls
```

### DON'T: Spam orientation or animation calls

DockKit can throw `.frameRateTooHigh` if `animate(motion:)` or
`setOrientation(_:duration:relative:)` is called more than twice per second.
Set a trajectory, observe its `Progress`, and avoid tight command loops.

### DON'T: Forget to restore tracking after animations

```swift
// WRONG -- tracking stays disabled after animation
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
let progress = try await accessory.animate(motion: .kapow)

// CORRECT -- restore tracking when animation completes
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
let progress = try await accessory.animate(motion: .kapow)
while !progress.isFinished && !progress.isCancelled {
    try await Task.sleep(for: .milliseconds(100))
}
try await DockAccessoryManager.shared.setSystemTrackingEnabled(true)
```

### DON'T: Use DockKit in Simulator

DockKit requires a physical DockKit-compatible accessory. Guard
initialization and provide fallback behavior when no accessory is
available.

## Review Checklist

- [ ] `import DockKit` present where needed
- [ ] Subscribed to `accessoryStateChanges` to detect dock/undock events
- [ ] Handled both `.docked` and `.undocked` states
- [ ] System tracking disabled before custom tracking or motor control
- [ ] System tracking restored after animations complete
- [ ] Custom observations supplied at 10-30 fps
- [ ] `animate` and `setOrientation` commands limited to 2 calls per second
- [ ] Observation `rect` uses normalized coordinates (lower-left origin)
- [ ] Camera information is built inline from the active `AVCaptureDevice` and current sample buffer
- [ ] Observation type choice names `.humanFace`, `.humanBody`, and `.object`
- [ ] `@unknown default` handled in all switch statements over DockKit enums
- [ ] Motion limits set if restricting accessory range of motion
- [ ] Tracking state re-applied after app returns to foreground
- [ ] `accessoryEvents` guarded with `#available(iOS 17.4, *)`
- [ ] `trackingStates` and `batteryStates` guarded with `#available(iOS 18.0, *)`
- [ ] Battery UI preserves `BatteryState.name` for multi-battery docks
- [ ] No DockKit code paths executed in Simulator builds

## References

- Extended patterns (Vision integration, service architecture, custom animations): [references/dockkit-patterns.md](references/dockkit-patterns.md)
- [DockKit framework](https://sosumi.ai/documentation/dockkit)
- [DockAccessoryManager](https://sosumi.ai/documentation/dockkit/dockaccessorymanager)
- [DockAccessory](https://sosumi.ai/documentation/dockkit/dockaccessory)
- [Controlling a DockKit accessory using your camera app](https://sosumi.ai/documentation/dockkit/controlling-a-dockkit-accessory-using-your-camera-app)
- [Track custom objects in a frame](https://sosumi.ai/documentation/dockkit/track-custom-objects-in-a-frame)
- [Modify rotation and positioning programmatically](https://sosumi.ai/documentation/dockkit/modify-rotation-and-positioning-behavior-programmatically)
- [Integrate with motorized iPhone stands using DockKit -- WWDC23](https://sosumi.ai/videos/play/wwdc2023/10304/)
- [What's new in DockKit -- WWDC24](https://sosumi.ai/videos/play/wwdc2024/10164/)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
