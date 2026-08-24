---
name: spritekit
description: "Build 2D games and animations using SpriteKit. Use when creating game scenes with SKScene and SKView, adding sprites with SKSpriteNode, animating with SKAction sequences, simulating physics with SKPhysicsBody and contact detection, creating particle effects with SKEmitterNode, building tile maps, using SKCameraNode, or integrating SpriteKit scenes in SwiftUI with SpriteView."
---

# SpriteKit

Build 2D games and interactive animations for iOS 26+ using SpriteKit and
Swift 6.3. Covers scene lifecycle, node hierarchy, actions, physics, particles,
camera, touch handling, and SwiftUI integration.

## Workflow

1. Establish scene size, scale mode, coordinate system, and ownership before adding gameplay nodes.
2. Keep gameplay state in the scene or a stable model; do not recreate the scene during SwiftUI updates.
3. Configure node names, z-order, actions, physics categories, and contact masks deliberately.
4. Separate camera/HUD coordinates from world coordinates and remove transient nodes predictably.
5. Verify frame-rate behavior, contact delivery, pause/resume, resizing, and scene teardown.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for scene setup, sprites, actions, physics, touch handling, camera, particles, and SwiftUI integration.
- Read [extended SpriteKit patterns](references/spritekit-patterns.md) for tile maps, atlases, shaders, advanced camera work, audio, and performance recipes.

## Core Decisions

- Choose the scene coordinate and scaling contract before positioning content.
- Use category and contact masks as a reviewed collision matrix.
- Keep `SKScene` identity stable when hosted by `SpriteView`.
- Prefer textures and atlases over expensive shape-node rendering in repeated content.

## Common Mistakes

### Creating a new scene on every SwiftUI re-render

```swift
// DON'T: Scene is recreated on every body evaluation
var body: some View {
    SpriteView(scene: GameScene(size: CGSize(width: 390, height: 844)))
}

// DO: Create once and reuse
@State private var scene = GameScene(size: CGSize(width: 390, height: 844))
var body: some View {
    SpriteView(scene: scene)
}
```

### Adding a child node that already has a parent

A node can only have one parent. Remove from the current parent first or
create a separate instance. Adding a node that already has a parent crashes.

### Forgetting to set contactTestBitMask

```swift
// DON'T: Bodies collide but didBegin is never called
player.physicsBody?.categoryBitMask = PhysicsCategory.player
enemy.physicsBody?.categoryBitMask = PhysicsCategory.enemy

// DO: Set contactTestBitMask to receive contact callbacks
player.physicsBody?.contactTestBitMask = PhysicsCategory.enemy
```

### Using SKShapeNode for performance-critical rendering

`SKShapeNode` uses a separate draw call per instance. Prefer `SKSpriteNode`
with a texture for repeated elements to enable batched rendering.

### Not removing nodes that leave the screen

```swift
// DON'T
enemy.run(SKAction.moveBy(x: -800, y: 0, duration: 3.0))
addChild(enemy)

// DO: Remove after leaving the visible area
enemy.run(SKAction.sequence([
    SKAction.moveBy(x: -800, y: 0, duration: 3.0),
    SKAction.removeFromParent()
]))
addChild(enemy)
```

### Setting physicsWorld.contactDelegate too late

Set `physicsWorld.contactDelegate = self` in `didMove(to:)`, not in
`update(_:)` or after a delay.

## Review Checklist

- [ ] Scene subclass overrides `didMove(to:)` for setup, not `init`
- [ ] `scaleMode` chosen appropriately for the game's design
- [ ] `ignoresSiblingOrder` set to `true` on `SKView` for performance
- [ ] `zPosition` used consistently when `ignoresSiblingOrder` is enabled
- [ ] Physics `contactDelegate` set in `didMove(to:)`
- [ ] Category, collision, and contact bit masks configured correctly
- [ ] `contactTestBitMask` set for any pair needing `didBegin`/`didEnd` callbacks
- [ ] Contact callbacks queue changes instead of mutating the physics world directly
- [ ] Static bodies use `isDynamic = false`
- [ ] `SKShapeNode` avoided in performance-critical paths; `SKSpriteNode` preferred
- [ ] Actions that move nodes offscreen include `.removeFromParent()` in sequence
- [ ] One-shot emitters remove themselves after particle lifetime expires
- [ ] Emitter `targetNode` set when particles should stay in world space
- [ ] Scene stored in `@State` when used with `SpriteView` in SwiftUI
- [ ] Texture atlases used for related sprites to reduce draw calls
- [ ] `update(_:)` uses delta time for frame-rate-independent movement
- [ ] Nodes removed from parent before being re-added elsewhere

## References

- See [references/spritekit-patterns.md](references/spritekit-patterns.md) for tile maps, texture atlases, shaders,
  scene transitions, game loop patterns, audio, and SceneKit embedding.
- [SpriteKit documentation](https://sosumi.ai/documentation/spritekit)
- [SKScene](https://sosumi.ai/documentation/spritekit/skscene)
- [SKSpriteNode](https://sosumi.ai/documentation/spritekit/skspritenode)
- [SKAction](https://sosumi.ai/documentation/spritekit/skaction)
- [SKPhysicsBody](https://sosumi.ai/documentation/spritekit/skphysicsbody)
- [SKEmitterNode](https://sosumi.ai/documentation/spritekit/skemitternode)
- [SKCameraNode](https://sosumi.ai/documentation/spritekit/skcameranode)
- [SpriteView](https://sosumi.ai/documentation/spritekit/spriteview)
- [SKTileMapNode](https://sosumi.ai/documentation/spritekit/sktilemapnode)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
