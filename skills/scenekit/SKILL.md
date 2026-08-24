---
name: scenekit
description: "Maintains existing SceneKit scenes, nodes, materials, cameras, lights, animation, physics, particles, assets, shaders, and SwiftUI hosting. Use for SceneKit maintenance; route new 3D apps, major redesigns, USD/USDZ pipelines, and migration planning to RealityKit."
---

# SceneKit

Maintain existing SceneKit scenes only. Apple deprecated SceneKit at WWDC 2025 and limits it to maintenance; route new projects, major modernization, and USD/USDZ pipelines to RealityKit. Existing apps continue to work.

## Workflow

1. Confirm the task is maintenance or extension of an existing SceneKit surface; prefer RealityKit for substantial new 3D work.
2. Inspect scene ownership, node hierarchy, coordinate spaces, camera, lights, and rendering delegate before editing.
3. Configure geometry, materials, transforms, animation, and physics with explicit lifecycle ownership.
4. Keep dynamic physics bodies under physics control and perform renderer mutations on the correct thread.
5. Verify model loading, device rendering, memory, frame time, and SwiftUI/UIKit teardown.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for scenes, nodes, materials, lighting, cameras, animation, physics, particles, model loading, and SwiftUI hosting.
- Read [extended SceneKit patterns](references/scenekit-patterns.md) for custom geometry, shader modifiers, constraints, morph targets, serialization, hit testing, LOD, and renderer delegates.

## Core Decisions

- Preserve SceneKit for existing pipelines while documenting migration pressure toward RealityKit.
- Treat node hierarchy and coordinate conversion as part of the data contract.
- Match physics shapes to performance needs instead of defaulting to exact geometry.
- Keep camera and lighting explicit so imported scenes do not depend on editor-only defaults.

## Common Mistakes

### Not adding a camera or lights

```swift
// DON'T: Scene renders blank or black -- no camera, no lights
sceneView.scene = scene

// DO: Add camera + lights, or use convenience flags
let cameraNode = SCNNode()
cameraNode.camera = SCNCamera()
cameraNode.position = SCNVector3(0, 5, 15)
scene.rootNode.addChildNode(cameraNode)
sceneView.pointOfView = cameraNode
sceneView.autoenablesDefaultLighting = true
```

### Using exact geometry for physics shapes

```swift
// DON'T
node.physicsBody = SCNPhysicsBody(type: .dynamic,
    shape: SCNPhysicsShape(geometry: complexMesh, options: nil))

// DO: Simplified primitive
node.physicsBody = SCNPhysicsBody(type: .dynamic,
    shape: SCNPhysicsShape(
        geometry: SCNBox(width: 1, height: 2, length: 1, chamferRadius: 0),
        options: nil))
```

### Modifying transforms on dynamic bodies

```swift
// DON'T: Resets physics simulation
dynamicNode.position = SCNVector3(5, 0, 0)

// DO: Use forces/impulses
dynamicNode.physicsBody?.applyForce(SCNVector3(10, 0, 0), asImpulse: true)
```

## Review Checklist

- [ ] Scene has at least one camera node set as `pointOfView`
- [ ] Scene has appropriate lighting (or `autoenablesDefaultLighting` for prototyping)
- [ ] Physics shapes use simplified geometry, not full mesh detail
- [ ] `contactTestBitMask` set for bodies that need collision callbacks
- [ ] `SCNPhysicsContactDelegate` assigned to `scene.physicsWorld.contactDelegate`
- [ ] Dynamic body transforms changed via forces/impulses, not direct position
- [ ] Lights limited to 8 per node; `attenuationEndDistance` set on point/spot lights
- [ ] Materials use `.physicallyBased` lighting model for realistic rendering
- [ ] SceneKit assets use documented `.scn`, `.dae`, or `.abc` scene-source formats
- [ ] Imported and exported assets pass consistency and required-node checks
      before commit
- [ ] Bundled SceneKit textures/images use asset catalogs or Xcode-optimized resources
- [ ] Scene metadata/import options use documented API; no invented `SCNScene.Attribute.unit`
- [ ] New USD/USDZ pipelines or significant updates are routed to RealityKit
- [ ] Game Center authentication, leaderboards, achievements, or multiplayer are handed off to GameKit
- [ ] `SCNReferenceNode` used for large models to enable lazy loading
- [ ] Particle `birthRate` and `particleLifeSpan` balanced to control particle count
- [ ] `categoryBitMask` used to scope lights and cameras to relevant nodes
- [ ] SwiftUI scenes use `SceneView` or `UIViewRepresentable`-wrapped `SCNView`
- [ ] Deprecation acknowledged; RealityKit evaluated for new projects

## References

- See [references/scenekit-patterns.md](references/scenekit-patterns.md) for custom geometry, shader modifiers, constraints, morph targets, hit testing, scene serialization, render loop delegates, performance, SpriteKit overlay, LOD, and Metal shaders.
- [SceneKit documentation](https://sosumi.ai/documentation/scenekit), [SCNSceneSource](https://sosumi.ai/documentation/scenekit/scnscenesource), [SCNView](https://sosumi.ai/documentation/scenekit/scnview), [SceneView](https://sosumi.ai/documentation/scenekit/sceneview)
- [SCNPhysicsShape](https://sosumi.ai/documentation/scenekit/scnphysicsshape), [SCNShadable](https://sosumi.ai/documentation/scenekit/scnshadable)
- [WWDC 2025 session 288: Bring your SceneKit project to RealityKit](https://sosumi.ai/videos/play/wwdc2025/288/)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
