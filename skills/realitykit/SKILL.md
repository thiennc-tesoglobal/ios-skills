---
name: realitykit
description: "Build iOS augmented reality and 3D experiences with RealityKit and ARKit. Use when adding RealityView content, loading entities or USDZ models, anchoring objects to planes or world positions, distinguishing entity hit tests from ARKit real-world raycasts, handling AR camera availability, world tracking, scene updates, or RealityKit entity gestures and interactions."
---

# RealityKit

Create augmented reality and 3D experiences on iOS using RealityKit for rendering and ARKit for world tracking and scene understanding. Targets Swift 6.3 / iOS 26+.

## Contents

- [Capabilities and Permissions](#capabilities-and-permissions)
- [RealityView and Architecture](#realityview-and-architecture)
- [Raycasting vs Entity Hit Testing](#raycasting-vs-entity-hit-testing)
- [Entity-Component-System (ECS)](#entity-component-system-ecs)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Capabilities and Permissions

Add `NSCameraUsageDescription` to `Info.plist`. Add `arkit` to `UIRequiredDeviceCapabilities` only if AR is an absolute requirement for the app; otherwise, check `ARWorldTrackingConfiguration.isSupported` at runtime and provide a 3D fallback (`content.camera = .virtual`).

## RealityView and Architecture

`RealityView` is the modern SwiftUI container for RealityKit content:
- **Make closure**: Asynchronously loads entities, materials, and sets up initial scene hierarchies.
- **Update closure**: Observes SwiftUI state changes and mutates entity properties or animations.
- **Attachments**: SwiftUI views anchored to 3D entities in space via `RealityViewContent.attachments`.

## Raycasting vs Entity Hit Testing

> [!IMPORTANT]
> Distinguish between real-world raycasting and virtual entity hit testing:
> - **ARKit Raycast (`raycast(from:allowing:alignment:)`)**: Intersects real-world physical surfaces (floors, tables, walls) discovered by camera feature points.
> - **RealityKit Hit Test (`scene.hitTest(_:)` / `entity.hitTest(_:)`)**: Intersects virtual 3D mesh geometry that has a `CollisionComponent`.

## Entity-Component-System (ECS)

RealityKit uses ECS architecture:
1. **`Entity`**: Identity container in the 3D scene hierarchy.
2. **`Component`**: Pure data structs attached to entities (`ModelComponent`, `CollisionComponent`, `InputTargetComponent`, custom components).
3. **`System`**: Per-frame update logic conforming to `System` protocol that processes entities matching specific component sets.

## Route by Task

- For loading USDZ models, custom materials, and programmatic geometries, read [Entity Creation and Materials](references/realitykit-patterns.md#entity-creation-and-materials).
- For anchoring entities to planes, faces, images, or world coordinates, read [Anchoring and World Tracking](references/realitykit-patterns.md#anchoring-and-world-tracking).
- For gesture-driven manipulation (rotate, scale, drag) and hit testing, read [Gestures and Interaction](references/realitykit-patterns.md#gestures-and-interaction).
- For physics simulations, collision detection, and raycast placement, read [Physics and Raycasting](references/realitykit-patterns.md#physics-and-raycasting).

## Common Mistakes

- Missing `NSCameraUsageDescription` in Info.plist, causing instant crash when `RealityView` initializes.
- Attempting to interact with entities that lack `CollisionComponent` and `InputTargetComponent`.
- Loading heavy USDZ models synchronously on the main actor, dropping UI frame rates.
- Confusing virtual hit testing with ARKit real-world surface raycasting.
- Forgetting to provide a non-AR fallback (`content.camera = .virtual`) for devices without world tracking.

## Review Checklist

- [ ] `NSCameraUsageDescription` declared in `Info.plist`
- [ ] Runtime support verified with `ARWorldTrackingConfiguration.isSupported`
- [ ] USDZ models and textures loaded asynchronously (`Entity(named:)` async)
- [ ] Interactive entities have both `CollisionComponent` and `InputTargetComponent`
- [ ] Real-world placement uses ARKit raycast; virtual manipulation uses entity hit test
- [ ] Per-frame system updates avoid allocating memory or performing blocking I/O
- [ ] Non-AR devices supported with virtual camera fallback

## References

- [RealityKit extended patterns and gesture handling](references/realitykit-patterns.md)
- [RealityKit documentation](https://sosumi.ai/documentation/realitykit)
- [RealityView](https://sosumi.ai/documentation/realitykit/realityview)
- [Entity](https://sosumi.ai/documentation/realitykit/entity)
- [ARKit documentation](https://sosumi.ai/documentation/arkit)
