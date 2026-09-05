# WebSocket Networking with URLSessionWebSocketTask

Use this reference when building real-time bidirectional WebSocket connections, handling reconnections, structured concurrency streaming, and Codable messaging in iOS.

## Contents

- [URLSessionWebSocketTask Overview](#urlsessionwebsockettask)
- [WebSocket with Structured Concurrency](#websocket-with-structured-concurrency)
- [Usage in SwiftUI](#usage-in-swiftui)
- [WebSocket Reconnection Strategy](#websocket-reconnection-strategy)
- [WebSocket with Codable Messages](#websocket-with-codable-messages)
- [WebSocket Authentication](#websocket-authentication)
- [WebSocket Subprotocol Negotiation](#websocket-subprotocol-negotiation)

---

`URLSessionWebSocketTask` provides native WebSocket support without
third-party libraries. Available since iOS 13. WebSockets use `ws:` or `wss:`
URLs and are foreground/default-session realtime networking; background
URLSession configuration does not make a WebSocket connection durable after
suspension.

### Basic Connection

```swift
@available(iOS 15.0, *)
final class WebSocketConnection: Sendable {
    private let task: URLSessionWebSocketTask

    init(url: URL, session: URLSession = .shared) {
        self.task = session.webSocketTask(with: url)
    }

    func connect() {
        task.resume()
    }

    func disconnect(reason: String? = nil) {
        task.cancel(with: .normalClosure, reason: reason?.data(using: .utf8))
    }

    func send(_ message: URLSessionWebSocketTask.Message) async throws {
        try await task.send(message)
    }

    func send(text: String) async throws {
        try await task.send(.string(text))
    }

    func send(data: Data) async throws {
        try await task.send(.data(data))
    }

    func receive() async throws -> URLSessionWebSocketTask.Message {
        try await task.receive()
    }
}
```

### WebSocket with Structured Concurrency

The key pattern: run a receive loop as an async task that yields
messages through an `AsyncStream`. This integrates naturally with
structured concurrency.

```swift
@available(iOS 15.0, *)
actor WebSocketManager {
    private var task: URLSessionWebSocketTask?
    private var receiveTask: Task<Void, Never>?
    private let session: URLSession
    private let url: URL

    enum Event: Sendable {
        case connected
        case text(String)
        case data(Data)
        case disconnected(URLSessionWebSocketTask.CloseCode, Data?)
        case error(Error)
    }

    init(url: URL, session: URLSession = .shared) {
        self.url = url
        self.session = session
    }

    /// Returns a stream of WebSocket events. Call `connect()` to start.
    func events() -> AsyncStream<Event> {
        AsyncStream { continuation in
            let wsTask = session.webSocketTask(with: url)
            self.task = wsTask

            wsTask.resume()
            continuation.yield(.connected)

            // Start the receive loop
            self.receiveTask = Task { [weak self] in
                await self?.receiveLoop(continuation: continuation)
            }

            continuation.onTermination = { _ in
                Task { [weak self] in
                    await self?.disconnect()
                }
            }
        }
    }

    private func receiveLoop(continuation: AsyncStream<Event>.Continuation) async {
        guard let task else { return }

        while !Task.isCancelled {
            do {
                let message = try await task.receive()
                switch message {
                case .string(let text):
                    continuation.yield(.text(text))
                case .data(let data):
                    continuation.yield(.data(data))
                @unknown default:
                    break
                }
            } catch {
                // The receive threw -- connection closed or failed
                let closeCode = task.closeCode
                let closeReason = task.closeReason
                if closeCode == .invalid {
                    // Unexpected disconnection
                    continuation.yield(.error(error))
                } else {
                    continuation.yield(.disconnected(closeCode, closeReason))
                }
                continuation.finish()
                return
            }
        }
    }

    func send(text: String) async throws {
        try await task?.send(.string(text))
    }

    func send(data: Data) async throws {
        try await task?.send(.data(data))
    }

    func disconnect() {
        receiveTask?.cancel()
        receiveTask = nil
        task?.cancel(with: .normalClosure, reason: nil)
        task = nil
    }

    /// Send periodic pings to keep the connection alive
    func startPinging(interval: Duration = .seconds(30)) {
        Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: interval)
                guard let self else { return }
                await self.ping()
            }
        }
    }

    private func ping() {
        task?.sendPing { error in
            if let error {
                // Connection may be dead
                print("Ping failed: \(error)")
            }
        }
    }
}
```

### Usage in SwiftUI

```swift
@MainActor
@Observable final class ChatStore {
    var messages: [ChatMessage] = []
    var connectionState: ConnectionState = .disconnected

    enum ConnectionState { case disconnected, connecting, connected }

    private let wsManager: WebSocketManager
    private var eventTask: Task<Void, Never>?

    init(url: URL) {
        self.wsManager = WebSocketManager(url: url)
    }

    func connect() async {
        connectionState = .connecting
        let stream = await wsManager.events()

        eventTask = Task {
            for await event in stream {
                await handleEvent(event)
            }
        }
    }

    func sendMessage(_ text: String) async {
        do {
            try await wsManager.send(text: text)
            messages.append(ChatMessage(text: text, isOutgoing: true))
        } catch {
            // Handle send failure
        }
    }

    func disconnect() async {
        eventTask?.cancel()
        eventTask = nil
        await wsManager.disconnect()
        connectionState = .disconnected
    }

    private func handleEvent(_ event: WebSocketManager.Event) async {
        switch event {
        case .connected:
            connectionState = .connected
        case .text(let text):
            messages.append(ChatMessage(text: text, isOutgoing: false))
        case .data(let data):
            if let text = String(data: data, encoding: .utf8) {
                messages.append(ChatMessage(text: text, isOutgoing: false))
            }
        case .disconnected:
            connectionState = .disconnected
        case .error:
            connectionState = .disconnected
            // Optionally trigger reconnection
        }
    }
}
```

```swift
struct ChatView: View {
    @State var store: ChatStore

    var body: some View {
        List(store.messages) { message in
            ChatBubble(message: message)
        }
        .task { await store.connect() }
        .onDisappear { Task { await store.disconnect() } }
    }
}
```

---

## WebSocket Reconnection Strategy

Network drops happen. A robust WebSocket client must reconnect
automatically with exponential backoff.

```swift
@available(iOS 15.0, *)
actor ReconnectingWebSocket {
    private let url: URL
    private let session: URLSession
    private let maxReconnectAttempts: Int
    private let initialDelay: Duration
    private let maxDelay: Duration

    private var currentManager: WebSocketManager?
    private var reconnectAttempts = 0
    private var isIntentionalDisconnect = false

    init(
        url: URL,
        session: URLSession = .shared,
        maxReconnectAttempts: Int = 10,
        initialDelay: Duration = .seconds(1),
        maxDelay: Duration = .seconds(60)
    ) {
        self.url = url
        self.session = session
        self.maxReconnectAttempts = maxReconnectAttempts
        self.initialDelay = initialDelay
        self.maxDelay = maxDelay
    }

    /// Returns a stream that automatically reconnects on disconnection.
    func events() -> AsyncStream<WebSocketManager.Event> {
        AsyncStream { continuation in
            Task {
                await connectWithReconnection(continuation: continuation)
            }
            continuation.onTermination = { _ in
                Task { [weak self] in
                    await self?.intentionalDisconnect()
                }
            }
        }
    }

    private func connectWithReconnection(
        continuation: AsyncStream<WebSocketManager.Event>.Continuation
    ) async {
        while !isIntentionalDisconnect && reconnectAttempts < maxReconnectAttempts {
            guard !Task.isCancelled else { break }

            let manager = WebSocketManager(url: url, session: session)
            currentManager = manager
            let stream = await manager.events()

            for await event in stream {
                switch event {
                case .connected:
                    reconnectAttempts = 0  // Reset on successful connection
                    continuation.yield(event)
                case .error, .disconnected:
                    continuation.yield(event)
                default:
                    continuation.yield(event)
                }
            }

            // Stream ended -- attempt reconnection unless intentional
            guard !isIntentionalDisconnect, !Task.isCancelled else { break }

            reconnectAttempts += 1
            let delay = calculateBackoff()
            do {
                try await Task.sleep(for: delay)
            } catch {
                break  // Cancelled during sleep
            }
        }

        continuation.finish()
    }

    private func calculateBackoff() -> Duration {
        let base = Double(initialDelay.components.seconds) * pow(2.0, Double(reconnectAttempts - 1))
        let capped = min(base, Double(maxDelay.components.seconds))
        let jitter = Double.random(in: 0...(capped * 0.25))
        return .seconds(capped + jitter)
    }

    func send(text: String) async throws {
        try await currentManager?.send(text: text)
    }

    func send(data: Data) async throws {
        try await currentManager?.send(data: data)
    }

    private func intentionalDisconnect() {
        isIntentionalDisconnect = true
        Task {
            await currentManager?.disconnect()
        }
    }
}
```

---

## WebSocket with Codable Messages

For typed message protocols (common in chat, gaming, real-time apps),
decode/encode messages automatically.

```swift
protocol WebSocketMessage: Codable, Sendable {
    static var messageType: String { get }
}

struct TypedWebSocketTransport {
    private let manager: WebSocketManager
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    init(manager: WebSocketManager) {
        self.manager = manager
    }

    func send<T: WebSocketMessage>(_ message: T) async throws {
        let envelope = MessageEnvelope(
            type: T.messageType,
            payload: try encoder.encode(message)
        )
        let data = try encoder.encode(envelope)
        try await manager.send(data: data)
    }

    /// Typed event stream that decodes known message types
    func typedEvents() async -> AsyncStream<DecodedEvent> {
        let rawEvents = await manager.events()
        return AsyncStream { continuation in
            Task {
                for await event in rawEvents {
                    switch event {
                    case .data(let data):
                        if let envelope = try? decoder.decode(MessageEnvelope.self, from: data) {
                            continuation.yield(.message(type: envelope.type, payload: envelope.payload))
                        }
                    case .text(let text):
                        if let data = text.data(using: .utf8),
                           let envelope = try? decoder.decode(MessageEnvelope.self, from: data) {
                            continuation.yield(.message(type: envelope.type, payload: envelope.payload))
                        }
                    case .connected:
                        continuation.yield(.connected)
                    case .disconnected(let code, _):
                        continuation.yield(.disconnected(code))
                    case .error(let error):
                        continuation.yield(.error(error))
                    }
                }
                continuation.finish()
            }
        }
    }

    enum DecodedEvent: Sendable {
        case connected
        case message(type: String, payload: Data)
        case disconnected(URLSessionWebSocketTask.CloseCode)
        case error(Error)
    }

    private struct MessageEnvelope: Codable, Sendable {
        let type: String
        let payload: Data
    }
}
```

---

## Background Session Gotchas


WebSocket connections often require authentication via a token in the
initial handshake (either as a query parameter or a custom header).

```swift
func authenticatedWebSocket(
    baseURL: URL,
    token: String
) -> URLSessionWebSocketTask {
    // Option 1: Token as query parameter
    guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: true) else {
        preconditionFailure("Invalid URL components for: \(baseURL)")
    }
    components.queryItems = [URLQueryItem(name: "token", value: token)]
    guard let authenticatedURL = components.url else {
        preconditionFailure("Failed to construct URL from components")
    }
    let task = URLSession.shared.webSocketTask(with: authenticatedURL)

    // Option 2: Token as custom header (use URLRequest)
    var request = URLRequest(url: baseURL)
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    let taskWithHeader = URLSession.shared.webSocketTask(with: request)

    return taskWithHeader
}
```

**Prefer the header approach** when the server supports it. Query
parameters may appear in server access logs, which is a security
concern for tokens.

---

## WebSocket Subprotocol Negotiation

```swift
// Request a specific subprotocol (e.g., graphql-ws)
let task = URLSession.shared.webSocketTask(
    with: url,
    protocols: ["graphql-transport-ws"]
)
task.resume()

// After connection, verify the negotiated protocol
// via the URLSessionWebSocketDelegate
```

```swift
extension WebSocketConnection: URLSessionWebSocketDelegate {
    nonisolated func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didOpenWithProtocol protocol: String?
    ) {
        print("Connected with protocol: \(`protocol` ?? "none")")
    }

    nonisolated func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
        reason: Data?
    ) {
        let reasonString = reason.flatMap { String(data: $0, encoding: .utf8) }
        print("Closed: \(closeCode) - \(reasonString ?? "no reason")")
    }
}
```
