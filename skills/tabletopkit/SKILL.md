---
name: tabletopkit
description: "Builds multiplayer spatial board games with TabletopKit on visionOS. Use for tables, seats, equipment, turns, TabletopAction state changes, interactions, snapping/tossing/physics, RealityKit rendering, deterministic game state, or Group Activities synchronization."
---

# TabletopKit

Build visionOS board games whose synchronized state changes flow through `TabletopAction` and render with RealityKit. The availability matrix below owns version details.

## Workflow

1. Confirm visionOS availability, TabletopKit capability, and whether the experience needs local, shared, or SharePlay-backed play.
2. Model stable identifiers, seats, equipment, and table geometry before rendering entities.
3. Express state changes as tabletop actions with validation, turn ownership, and deterministic outcomes.
4. Connect interactions and RealityKit representations without making rendered entities the source of truth.
5. Verify reset, reconnect, late-join, undo, and multi-participant behavior.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for setup, tables, equipment, seats, actions, interactions, RealityKit rendering, and Group Activities wiring.
- Read [extended TabletopKit patterns](references/tabletopkit-patterns.md) for custom actions, dice simulation, card layouts, state bookmarks, observers, and network coordination.

## Core Decisions

- Keep game state and equipment identifiers deterministic across participants.
- Validate custom actions before mutation and keep turn/seat authority explicit.
- Use TabletopKit interactions for tabletop semantics; use RealityKit for presentation and effects.
- Treat SharePlay transport, reconnection, and late joining as lifecycle states, not happy-path callbacks.

## Common Mistakes

- **Skipping seat claim.** Players must call `claimAnySeat()` or `claimSeat(_:)`
  before interacting with equipment. Without a seat, actions are rejected.
- **Mutating state outside actions.** All state changes must go through
  `TabletopAction` or `CustomAction`. Directly modifying equipment properties
  bypasses synchronization.
- **Missing custom action registration.** Register every custom action with
  `setup.register(action:)` before use.
- **Not handling action rollback.** Actions are optimistically applied and can be
  rolled back if validation fails on the arbiter. Implement
  `actionWasRolledBack(_:snapshot:)` to revert UI state.
- **Ignoring discarded actions when available.** Implement
  `actionWasDiscarded(_:)` when local action queue pressure matters; it is
  called for local actions that cannot be enqueued.
- **Using wrong parent ID.** Equipment `parentID` in state must reference a
  valid equipment ID (typically the table or a container). An invalid parent
  causes the piece to disappear.
- **Ignoring TossOutcome faces.** After a toss, read the face from
  `outcome.tossableRepresentation.face(for: outcome.restingOrientation)` rather
  than generating a random value. The physics simulation determines the result.
- **Testing multiplayer in Simulator.** Group Activities do not work in Simulator.
  Multiplayer requires physical Apple Vision Pro devices on a FaceTime call.

## Review Checklist

- [ ] The centralized platform/availability matrix is applied
- [ ] `TableSetup` created with a `Tabletop`/`EntityTabletop` conforming type
- [ ] All equipment conforms to `Equipment` or `EntityEquipment` with correct state type
- [ ] Seats added and `claimAnySeat()` / `claimSeat(_:)` called at game start
- [ ] All custom actions registered with `setup.register(action:)`
- [ ] `TabletopGame.Observer` reconciles confirmed, rolled-back, discarded, and
      bookmark-reset outcomes with the current snapshot
- [ ] `EntityRenderDelegate` or `RenderDelegate` connected
- [ ] `.tabletopGame(_:parent:automaticUpdate:)` modifier on `RealityView`
- [ ] `GroupActivity` defined and `coordinateWithSession(_:)` called; multiplayer described as Group Activities/SharePlay synchronization
- [ ] Group Activities capability added in Xcode for multiplayer builds
- [ ] Debug visualization (`debugDraw`) disabled before release
- [ ] Device notes state Simulator is single-player only; multiplayer requires 2+ Apple Vision Pro units on FaceTime

## References

- [references/tabletopkit-patterns.md](references/tabletopkit-patterns.md) -- extended patterns for observer implementation, custom actions, dice simulation, card overlap, and network coordination
- [Apple Documentation: TabletopKit](https://sosumi.ai/documentation/tabletopkit), [Creating tabletop games](https://sosumi.ai/documentation/tabletopkit/creating-tabletop-games), [Synchronizing group gameplay](https://sosumi.ai/documentation/tabletopkit/synchronizing-group-gameplay-with-tabletopkit)
- [Simulating dice rolls](https://sosumi.ai/documentation/tabletopkit/simulating-dice-rolls-as-a-component-for-your-game), [Implementing playing card overlap](https://sosumi.ai/documentation/tabletopkit/implementing-playing-card-overlap-and-physical-characteristics)
- [WWDC24 session 10091: Build a spatial board game](https://sosumi.ai/videos/play/wwdc2024/10091/)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
