---
name: gamekit
description: "Builds Game Center features with GameKit. Use for local-player authentication and restrictions, access point/dashboard, leaderboards, achievements, challenges, saved games, invitations, real-time or turn-based matchmaking, match data, and server identity verification."
---

# GameKit

Use GameKit for Game Center authentication, competition, matchmaking, social
surfaces, and saved-game handoffs; keep rendering, board logic, and full
SharePlay group-activity design in their owning framework skills.

## Workflow

1. Authenticate `GKLocalPlayer` once, present authentication UI when supplied, and inspect restrictions before enabling features.
2. Choose the smallest Game Center surface: access point/dashboard, leaderboard, achievement, real-time match, or turn-based match.
3. Register listeners and delegates before events can arrive, and define ownership/cancellation for matchmaking and sessions.
4. Treat network and match data as untrusted, version the payload, and separate reliable critical state from transient updates.
5. Verify signed-out, restricted, invitation, disconnect, reconnect, timeout, and multi-player completion paths.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for authentication, access point, dashboard, leaderboards, achievements, and multiplayer lifecycles.
- Read [extended GameKit patterns](references/gamekit-patterns.md) for server identity verification, saved games, custom matchmaking, challenges, images, and legacy voice chat.

## Core Decisions

- Do not use GameKit APIs until authentication has completed successfully.
- Set match delegates immediately and finish or cancel matchmaking on every exit path.
- Keep match payloads bounded, versioned, and validated before state mutation.
- Disconnect and unregister long-lived listeners when their owner ends.

## Common Mistakes

### Not authenticating before using GameKit APIs

```swift
// DON'T
func submitScore() {
    GKLeaderboard.submitScore(100, context: 0, player: GKLocalPlayer.local,
                              leaderboardIDs: ["scores"]) { _ in }
}

// DO
func submitScore() async throws {
    guard GKLocalPlayer.local.isAuthenticated else { return }
    try await GKLeaderboard.submitScore(
        100, context: 0, player: GKLocalPlayer.local, leaderboardIDs: ["scores"]
    )
}
```

### Setting authenticateHandler multiple times

```swift
// DON'T: Set handler on every scene transition
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    GKLocalPlayer.local.authenticateHandler = { vc, error in /* ... */ }
}

// DO: Set the handler once, early in the app lifecycle
```

### Ignoring multiplayer restrictions

```swift
// DON'T
func showMultiplayerMenu() { presentMatchmaker() }

// DO
func showMultiplayerMenu() {
    guard !GKLocalPlayer.local.isMultiplayerGamingRestricted else { return }
    presentMatchmaker()
}
```

### Not setting match delegate immediately

```swift
// DON'T: Set delegate in dismiss completion -- misses early messages
func matchmakerViewController(_ vc: GKMatchmakerViewController, didFind match: GKMatch) {
    vc.dismiss(animated: true) { match.delegate = self }
}

// DO: Set delegate before dismissing
func matchmakerViewController(_ vc: GKMatchmakerViewController, didFind match: GKMatch) {
    match.delegate = self
    vc.dismiss(animated: true)
}
```

### Not calling finishMatchmaking for programmatic matches

```swift
// DON'T
let match = try await GKMatchmaker.shared().findMatch(for: request)
startGame(with: match)

// DO
let match = try await GKMatchmaker.shared().findMatch(for: request)
GKMatchmaker.shared().finishMatchmaking(for: match)
startGame(with: match)
```

### Not disconnecting from match

```swift
// DON'T
func returnToMenu() { showMainMenu() }

// DO
func returnToMenu() {
    currentMatch?.disconnect()
    currentMatch?.delegate = nil
    currentMatch = nil
    showMainMenu()
}
```

## Review Checklist

- [ ] `GKLocalPlayer.local.authenticateHandler` set once at app launch
- [ ] `isAuthenticated` checked before any GameKit API call
- [ ] Player restrictions checked (`isUnderage`, `isMultiplayerGamingRestricted`, `isPersonalizedCommunicationRestricted`)
- [ ] Game Center capability added in Xcode signing settings
- [ ] Leaderboards and achievements configured in App Store Connect
- [ ] Access point configured and toggled appropriately during gameplay
- [ ] `GKGameCenterControllerDelegate` dismisses dashboard in `gameCenterViewControllerDidFinish`
- [ ] Match delegate set immediately when match is found
- [ ] `finishMatchmaking(for:)` called for programmatic matches; `disconnect()` and nil delegate on exit
- [ ] Turn-based match data stays under `match.matchDataMaximumSize`
- [ ] Turn-based participants have outcomes set before `endMatchInTurn`
- [ ] Invitation or turn listener registered with `GKLocalPlayer.local.register(_:)`
- [ ] Data mode chosen appropriately: `.reliable` for state, `.unreliable` for frequent updates
- [ ] Error handling for all async GameKit calls

## References

- See [references/gamekit-patterns.md](references/gamekit-patterns.md) for identity verification, legacy voice chat, saved games, custom match UI, leaderboard images, challenge handling, and rule-based matchmaking.
- [GameKit documentation](https://sosumi.ai/documentation/gamekit)
- [GKLocalPlayer](https://sosumi.ai/documentation/gamekit/gklocalplayer)
- [GKAccessPoint](https://sosumi.ai/documentation/gamekit/gkaccesspoint)
- [GKLeaderboard](https://sosumi.ai/documentation/gamekit/gkleaderboard)
- [GKAchievement](https://sosumi.ai/documentation/gamekit/gkachievement)
- [GKMatch](https://sosumi.ai/documentation/gamekit/gkmatch)
- [GKTurnBasedMatch](https://sosumi.ai/documentation/gamekit/gkturnbasedmatch)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
