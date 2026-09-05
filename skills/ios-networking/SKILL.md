---
name: ios-networking
description: "Builds or reviews Apple-platform networking with URLSession, async/await, and structured concurrency. Use for REST clients, uploads/downloads, WebSockets, pagination, retries, middleware, caching, background transfers, reachability, request errors, or network data loading."
---

# iOS Networking

Build and review Apple-platform networking using `URLSession` with native async/await, structured concurrency, and `Network.framework`. Targets Swift 6.3 / iOS 26+.

## Contents

- [Core Principles](#core-principles)
- [Status Code Validation and Error Contract](#status-code-validation-and-error-contract)
- [Foreground vs Background Transfers](#foreground-vs-background-transfers)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Core Principles

1. **Prefer native async/await**: Use `URLSession.shared.data(for:)`, `download(for:)`, and `bytes(for:)` for all foreground network operations.
2. **Never swallow HTTP errors**: `URLSession` only throws for transport-level failures (offline, DNS, timeout). It does **not** throw on 4xx or 5xx responses. Always validate `(200..<300).contains(httpResponse.statusCode)`.
3. **Keep retry policies bounded**: Limit retries with exponential backoff and jitter. Only retry idempotent operations (GET, PUT, DELETE); never loop token refresh indefinitely.
4. **Isolate shared state**: Isolate token storage, refresh locks, and cookie management inside actors or serial synchronization queues.

## Status Code Validation and Error Contract

```swift
let (data, response) = try await session.data(for: request)

guard let httpResponse = response as? HTTPURLResponse else {
    throw NetworkError.invalidResponse
}

guard (200..<300).contains(httpResponse.statusCode) else {
    throw NetworkError.httpError(statusCode: httpResponse.statusCode, data: data)
}
```

Differentiate error categories: transport errors (`URLError`), decoding errors (`DecodingError`), client errors (4xx), server errors (5xx), and cancellation (`CancellationError`).

## Foreground vs Background Transfers

| Transfer Mode | API Pattern | Session Configuration | Suspension Behavior |
|---|---|---|---|
| Foreground Data | `try await session.data(for:)` | `.default` or `.ephemeral` | Cancelled on app suspension |
| Foreground Download | `try await session.download(for:)` | `.default` | Pauses/cancels on suspension |
| Background Transfer | `session.downloadTask(with:)` with delegate | `URLSessionConfiguration.background(withIdentifier:)` | Managed out-of-process; relaunches app on finish |
| WebSocket | `session.webSocketTask(with:)` | `.default` | Reconnection required on resume |

## Route by Task

- For building reusable API clients, request encoders, authentication headers, and actors, read [API Client and Request Building](references/api-client-and-request-building.md) and [Lightweight Clients](references/lightweight-clients.md).
- For resilient retries, certificate pinning, TLS security, and byte streaming, read [Resilience, Security, and Streaming](references/resilience-security-and-streaming.md).
- For large file uploads, resume data, and progress tracking, read [Uploads and Downloads](references/uploads-and-downloads.md) and [File Storage Patterns](references/file-storage-patterns.md).
- For background transfers and app relaunch handlers, read [Background Transfers](references/background-transfers.md). For real-time WebSockets, read [WebSocket Networking](references/websocket-networking.md).
- For cursor/offset pagination, AsyncSequence streams, and URLProtocol unit testing, read [Pagination and URLProtocol Testing](references/pagination-and-urlprotocol-testing.md).
- For low-level TCP/UDP sockets, path monitoring, and cellular constraints with `NWPathMonitor`, read [Network Framework](references/network-framework.md).

## Common Mistakes

- Assuming `URLSession.data(for:)` throws on HTTP 404 or 500 responses instead of inspecting `statusCode`.
- Using async/await convenience overloads on background `URLSessionConfiguration`, which requires delegate callbacks.
- Retrying non-idempotent POST requests automatically after a network timeout.
- Leaking `NWPathMonitor` instances or starting monitoring without setting a dispatch queue.
- Moving downloaded files after returning from `urlSession(_:downloadTask:didFinishDownloadingTo:)` (file is deleted upon return).

## Review Checklist

- [ ] HTTP status code explicitly validated before decoding payload
- [ ] Transport errors separated from server-returned error payloads
- [ ] Safe retry policy with jitter applied only to idempotent requests
- [ ] Auth token refresh uses actor isolation to avoid redundant refresh calls
- [ ] Background sessions configure delegate and move temporary files synchronously
- [ ] URLProtocol tests verify 2xx, 4xx, 5xx, timeout, and cancellation states
- [ ] App Transport Security (ATS) exceptions avoided unless strictly necessary

## References

- [API client and request building](references/api-client-and-request-building.md)
- [Lightweight clients](references/lightweight-clients.md)
- [Resilience, security, and streaming](references/resilience-security-and-streaming.md)
- [Uploads and downloads](references/uploads-and-downloads.md)
- [File storage patterns](references/file-storage-patterns.md)
- [Background transfers](references/background-transfers.md)
- [WebSocket networking](references/websocket-networking.md)
- [Pagination and URLProtocol testing](references/pagination-and-urlprotocol-testing.md)
- [Network.framework and NWPathMonitor](references/network-framework.md)
- [URLSession documentation](https://sosumi.ai/documentation/foundation/urlsession)
- [URLRequest documentation](https://sosumi.ai/documentation/foundation/urlrequest)
