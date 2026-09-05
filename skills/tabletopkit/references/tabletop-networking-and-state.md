# TabletopKit Networking, State Bookmarks, and Debugging

Use this reference when implementing multiplayer coordination via GroupActivities, state bookmarks and undo, score tracking, and TabletopKit physics debugging.

## Contents

- [Network and Multiplayer Coordination](#network-and-multiplayer-coordination)
- [State Bookmarks and Undo](#state-bookmarks-and-undo)
- [Score Tracking](#score-tracking)
- [Debugging Techniques](#debugging-techniques)

---

## Network and Multiplayer Coordination

Group Activities coordination is available through
`TabletopGame.coordinateWithSession(_:)`; Apple's group-gameplay sample uses
visionOS 26.0+ / Xcode 26.0+ APIs.

### Custom Network Coordinator

For non-GroupActivities multiplayer (e.g., local network), implement
`TabletopNetworkSessionCoordinator`:

```swift
class LocalNetworkCoordinator: TabletopNetworkSessionCoordinator {
    typealias Peer = NetworkPeer
    typealias NetworkSession = TabletopNetworkSession<LocalNetworkCoordinator>

    var networkSession: NetworkSession?

    func coordinateWithSession(_ session: NetworkSession) {
        self.networkSession = session
    }

    func sendMessage(_ data: Data,
                     to peers: Set<NetworkPeer>,
                     completion: (TabletopSendMessageResult) -> Void) {
        // Send via your transport layer
        completion(.success)
    }

    func sendMessageUnreliably(_ data: Data,
                                to peers: Set<NetworkPeer>,
                                completion: (TabletopSendMessageResult) -> Void) {
        // Send without delivery guarantee
        completion(.success)
    }

    func peerJoinedGame(_ peerID: NetworkPeer.ID) {
        networkSession?.addPeer(/* peer */)
    }

    func peerLeftGame(_ peerID: NetworkPeer.ID) {
        networkSession?.removePeer(/* peer */)
    }
}
```

### Arbiter Role

In multiplayer, one device acts as the arbiter (source of truth). The arbiter
validates actions and resolves conflicts.

```swift
// Become the arbiter
networkSession.becomeArbiter()

// Or follow another peer as arbiter
networkSession.followArbiter(hostPeer)
```

### Handling Network Lifecycle

```swift
// Start hosting
networkSession.start()

// Join an existing session
networkSession.join()

// Leave gracefully
networkSession.leave()

// Terminate the session (arbiter only)
networkSession.terminate()
```

## State Bookmarks and Undo

### Creating Bookmarks at Key Points

Save state at the start of each turn for undo support:

```swift
func startNewTurn(seatID: TableSeatIdentifier) {
    let bookmarkID = StateBookmarkIdentifier(turnNumber)
    game.addAction(.createBookmark(id: bookmarkID))
    game.addAction(.setTurn(matching: seatID))
}
```

### Restoring to a Bookmark

```swift
// Undo last turn
if let lastBookmark = game.bookmarks.last {
    game.jumpToBookmark(matching: lastBookmark)
}
```

### Observer Notification

```swift
func stateDidResetToBookmark(_ bookmarkID: StateBookmarkIdentifier) {
    // This callback is the completion/reconciliation point for the jump.
    game.withCurrentSnapshot { snapshot in
        refreshUI(from: snapshot)
        validateRestoredTurnInvariant(snapshot)
    }
}
```

Do not inspect the snapshot immediately after `jumpToBookmark` or blindly issue
another jump when local UI disagrees. Wait for this ordered callback, then
rebuild local UI from its snapshot. Keep confirm, rollback, and discard handling
in the main [Observer Patterns](#observer-patterns) implementation.

## Score Tracking

### Setting Up Counters per Player

```swift
// During setup: one counter per seat
for seatIndex in 0..<4 {
    setup.add(counter: ScoreCounter(id: .init(seatIndex), value: 0))
}
```

### Updating Scores

```swift
// Increment a player's score
game.withCurrentSnapshot { snapshot in
    let currentScore = snapshot.counter(matching: .init(seatIndex))?.value ?? 0
    game.addAction(.updateCounter(
        matching: .init(seatIndex),
        value: currentScore + points
    ))
}
```

### Reading Scores from Snapshot

```swift
game.withCurrentSnapshot { snapshot in
    for counter in snapshot.counters {
        print("Counter \(counter.id): \(counter.value)")
    }
}
```

## Debugging Techniques

### Debug Draw Options

```swift
// Draw all debug visuals
game.debugDraw(options: [.drawTable, .drawSeats, .drawEquipment])

// Draw only table boundaries
game.debugDraw(options: [.drawTable])

// Disable all debug visuals
game.debugDraw(options: [])
```

### Inspecting Snapshots

```swift
game.withCurrentSnapshot { snapshot in
    // List all equipment
    for id in snapshot.equipmentIDs() {
        let state = snapshot.state(matching: id)
        print("Equipment \(id.rawValue): \(String(describing: state))")
    }

    // List seat assignments
    for seat in snapshot.seats {
        print("Seat: \(seat)")
    }

    // Check whose turn it is
    print("Turn: \(snapshot.turn)")

    // List active cursors (interactions in progress)
    for cursor in snapshot.cursors {
        print("Cursor: player=\(cursor.playerID), "
              + "equipment=\(cursor.controlledEquipmentPose.id)")
    }
}
```

### Logging Observer Events

Wrap observer methods with logging during development:

```swift
func actionWasConfirmed(_ action: some TabletopAction,
                        oldSnapshot: TableSnapshot,
                        newSnapshot: TableSnapshot) {
    #if DEBUG
    print("[Observer] Confirmed: \(type(of: action)), "
          + "player=\(String(describing: action.playerID))")
    #endif
    // Normal handling...
}

func actionWasRolledBack(_ action: some TabletopAction,
                          snapshot: TableSnapshot) {
    #if DEBUG
    print("[Observer] Rolled back: \(type(of: action))")
    #endif
}
```
