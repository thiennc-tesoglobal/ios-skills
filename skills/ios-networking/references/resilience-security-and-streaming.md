# URLSession Resilience, Security, Caching, and Streaming

Read this reference only when the task matches the sections below.

## Retry with Exponential Backoff

Respect cancellation. Do not retry client errors (4xx except 429 rate
limiting). Include jitter to prevent thundering herd.

```swift
func withRetry<T: Sendable>(
    maxAttempts: Int = 3,
    initialDelay: Duration = .seconds(1),
    maxDelay: Duration = .seconds(30),
    shouldRetry: @Sendable (Error) -> Bool = { error in
        if error is CancellationError { return false }
        if case NetworkError.httpError(let code, _, _) = error {
            return code >= 500 || code == 429
        }
        if let urlError = error as? URLError {
            return [.timedOut, .networkConnectionLost, .notConnectedToInternet]
                .contains(urlError.code)
        }
        return false
    },
    operation: @Sendable () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 0..<maxAttempts {
        try Task.checkCancellation()
        do {
            return try await operation()
        } catch {
            lastError = error
            guard shouldRetry(error), attempt < maxAttempts - 1 else {
                throw error
            }
            // Exponential backoff with jitter
            let base = Double(initialDelay.components.seconds) * pow(2.0, Double(attempt))
            let capped = min(base, Double(maxDelay.components.seconds))
            let jitter = Double.random(in: 0...(capped * 0.1))
            let delay = Duration.seconds(capped + jitter)
            try await Task.sleep(for: delay)
        }
    }

    throw lastError!
}

// Usage
let users = try await withRetry {
    try await client.get([User].self, path: "users")
}
```

---

## Certificate Pinning (URLSessionDelegate)

Prefer ATS `NSPinnedDomains` for declarative certificate pinning when the
pinset can ship in `Info.plist`. For manual `URLSessionDelegate` trust work,
defer to the `swift-security` skill: correct SPKI pinning requires hashing
the Subject Public Key Info structure, not just the raw key bytes returned by
`SecKeyCopyExternalRepresentation`.

**Important considerations:**
- Pin at least two keys (primary + backup) to avoid lockout during rotation.
- Have a remote kill switch (feature flag) to disable pinning in emergencies.
- Test certificate rotation in staging before deploying to production.
- Always evaluate system trust before applying pins.
- Keep certificate-trust implementation details in the security boundary.

---

## Request Logging / Debugging Middleware

Log outgoing requests and incoming responses for debugging. Disable or
reduce verbosity in release builds.

```swift
struct LoggingMiddleware: RequestMiddleware {
    let logger: Logger

    func prepare(_ request: URLRequest) async throws -> URLRequest {
        #if DEBUG
        let method = request.httpMethod ?? "GET"
        let url = request.url?.absoluteString ?? "unknown"
        logger.debug("[\(method)] \(url)")
        if let headers = request.allHTTPHeaderFields {
            for (key, value) in headers where key != "Authorization" {
                logger.debug("  \(key): \(value)")
            }
        }
        if let body = request.httpBody, body.count < 10_000 {
            logger.debug("  Body: \(String(data: body, encoding: .utf8) ?? "<binary>")")
        }
        #endif
        return request
    }
}
```

### Response Logging

To log responses, wrap the transport call rather than using middleware:

```swift
func loggedRequest<T: Decodable & Sendable>(
    _ type: T.Type,
    endpoint: Endpoint,
    logger: Logger
) async throws -> T {
    let start = ContinuousClock().now
    do {
        let result: T = try await request(type, endpoint: endpoint)
        let elapsed = ContinuousClock().now - start
        logger.debug("[\(endpoint.method.rawValue)] \(endpoint.path) -> 200 (\(elapsed))")
        return result
    } catch {
        let elapsed = ContinuousClock().now - start
        logger.error("[\(endpoint.method.rawValue)] \(endpoint.path) -> ERROR (\(elapsed)): \(error)")
        throw error
    }
}
```

---

## Request Caching Strategies

### URLCache Configuration

```swift
// 50 MB memory / 200 MB disk cache
let cache = URLCache(
    memoryCapacity: 50 * 1024 * 1024,
    diskCapacity: 200 * 1024 * 1024,
    directory: FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)
        .first?.appendingPathComponent("URLCache")
)

let config = URLSessionConfiguration.default
config.urlCache = cache
config.requestCachePolicy = .returnCacheDataElseLoad

let session = URLSession(configuration: config)
```

### Per-Request Cache Control

```swift
// Force fresh data
var request = URLRequest(url: url)
request.cachePolicy = .reloadIgnoringLocalCacheData

// Use cached if available
request.cachePolicy = .returnCacheDataElseLoad

// Cache only (offline mode)
request.cachePolicy = .returnCacheDataDontLoad
```

### ETag / If-None-Match

```swift
func fetchWithETag<T: Decodable & Sendable>(
    _ type: T.Type,
    url: URL,
    cachedETag: String?,
    cachedData: Data?
) async throws -> (T, String?) {
    var request = URLRequest(url: url)
    if let etag = cachedETag {
        request.setValue(etag, forHTTPHeaderField: "If-None-Match")
    }

    let (data, response) = try await URLSession.shared.data(for: request)
    guard let http = response as? HTTPURLResponse else {
        throw NetworkError.invalidResponse
    }

    if http.statusCode == 304, let cachedData {
        // Not modified -- use cached data
        let decoded = try JSONDecoder().decode(T.self, from: cachedData)
        return (decoded, cachedETag)
    }

    let newETag = http.value(forHTTPHeaderField: "ETag")
    let decoded = try JSONDecoder().decode(T.self, from: data)
    return (decoded, newETag)
}
```

---

## Server-Sent Events (SSE) Parsing

Use `bytes(for:)` to consume a streaming SSE endpoint.

```swift
struct ServerSentEvent: Sendable {
    var event: String?
    var data: String
    var id: String?
}

func sseStream(from url: URL) -> AsyncThrowingStream<ServerSentEvent, Error> {
    AsyncThrowingStream { continuation in
        let task = Task {
            do {
                var request = URLRequest(url: url)
                request.setValue("text/event-stream", forHTTPHeaderField: "Accept")

                let (bytes, _) = try await URLSession.shared.bytes(for: request)

                var currentEvent: String?
                var currentData = ""
                var currentId: String?

                for try await line in bytes.lines {
                    if line.isEmpty {
                        // Empty line = dispatch event
                        if !currentData.isEmpty {
                            continuation.yield(ServerSentEvent(
                                event: currentEvent,
                                data: currentData.trimmingCharacters(in: .newlines),
                                id: currentId
                            ))
                        }
                        currentEvent = nil
                        currentData = ""
                        currentId = nil
                    } else if line.hasPrefix("event:") {
                        currentEvent = String(line.dropFirst(6)).trimmingCharacters(in: .whitespaces)
                    } else if line.hasPrefix("data:") {
                        let value = String(line.dropFirst(5)).trimmingCharacters(in: .whitespaces)
                        currentData += currentData.isEmpty ? value : "\n" + value
                    } else if line.hasPrefix("id:") {
                        currentId = String(line.dropFirst(3)).trimmingCharacters(in: .whitespaces)
                    }
                }
                continuation.finish()
            } catch {
                continuation.finish(throwing: error)
            }
        }
        continuation.onTermination = { _ in task.cancel() }
    }
}
```

---

## Configured URLSession for Production

Use a configured session for production clients instead of calling
`URLSession.shared` from request methods. Set explicit request/resource
timeouts, cache behavior, connectivity policy, and any delegates needed for
authentication challenges, redirects, metrics, pinning boundaries, or
background transfers before creating the `URLSession`.

```swift
enum SessionFactory {
    static func makeDefault(delegate: (any URLSessionDelegate)? = nil) -> URLSession {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        config.waitsForConnectivity = true
        config.httpMaximumConnectionsPerHost = 6
        config.requestCachePolicy = .useProtocolCachePolicy
        config.httpAdditionalHeaders = [
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        ]

        let cache = URLCache(
            memoryCapacity: 25 * 1024 * 1024,
            diskCapacity: 100 * 1024 * 1024
        )
        config.urlCache = cache

        return URLSession(
            configuration: config,
            delegate: delegate,
            delegateQueue: nil
        )
    }
}
```
