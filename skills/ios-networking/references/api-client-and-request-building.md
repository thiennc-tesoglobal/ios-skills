# URLSession API Client and Request Building

Complete implementation patterns for URLSession-based networking.

---

## Complete API Client with Protocol

A full-featured client with middleware support, configurable decoding,
and response validation.

### Protocol

```swift
protocol APIClientProtocol: Sendable {
    func request<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint
    ) async throws -> T

    func request(endpoint: Endpoint) async throws

    func upload<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint,
        body: Data
    ) async throws -> T
}
```

### Endpoint Definition

```swift
struct Endpoint: Sendable {
    let path: String
    var method: HTTPMethod = .get
    var queryItems: [URLQueryItem] = []
    var headers: [String: String] = [:]
    var body: Data? = nil
    var cachePolicy: URLRequest.CachePolicy = .useProtocolCachePolicy
    var timeoutInterval: TimeInterval = 30

    enum HTTPMethod: String, Sendable {
        case get = "GET"
        case post = "POST"
        case put = "PUT"
        case patch = "PATCH"
        case delete = "DELETE"
    }

    func urlRequest(relativeTo baseURL: URL) -> URLRequest {
        var components = URLComponents(
            url: baseURL.appendingPathComponent(path),
            resolvingAgainstBaseURL: true
        )!
        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }
        var request = URLRequest(url: components.url!)
        request.httpMethod = method.rawValue
        request.httpBody = body
        request.cachePolicy = cachePolicy
        request.timeoutInterval = timeoutInterval
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        return request
    }
}
```

### Client Implementation

```swift
final class APIClient: APIClientProtocol {
    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let middlewares: [any RequestMiddleware]

    init(
        baseURL: URL,
        session: URLSession = .shared,
        decoder: JSONDecoder = {
            let d = JSONDecoder()
            d.dateDecodingStrategy = .iso8601
            d.keyDecodingStrategy = .convertFromSnakeCase
            return d
        }(),
        encoder: JSONEncoder = {
            let e = JSONEncoder()
            e.dateEncodingStrategy = .iso8601
            e.keyEncodingStrategy = .convertToSnakeCase
            return e
        }(),
        middlewares: [any RequestMiddleware] = []
    ) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = decoder
        self.encoder = encoder
        self.middlewares = middlewares
    }

    func request<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint
    ) async throws -> T {
        let request = try await prepareRequest(for: endpoint)
        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
        return try decoder.decode(T.self, from: data)
    }

    func request(endpoint: Endpoint) async throws {
        let request = try await prepareRequest(for: endpoint)
        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
    }

    func upload<T: Decodable & Sendable>(
        _ type: T.Type,
        endpoint: Endpoint,
        body: Data
    ) async throws -> T {
        var request = try await prepareRequest(for: endpoint)
        request.httpBody = body
        let (data, response) = try await session.upload(for: request, from: body)
        try validateResponse(response, data: data)
        return try decoder.decode(T.self, from: data)
    }

    // MARK: - Convenience methods

    func get<T: Decodable & Sendable>(
        _ type: T.Type,
        path: String,
        queryItems: [URLQueryItem] = []
    ) async throws -> T {
        try await request(type, endpoint: Endpoint(
            path: path,
            method: .get,
            queryItems: queryItems
        ))
    }

    func post<T: Decodable & Sendable, B: Encodable & Sendable>(
        _ type: T.Type,
        path: String,
        body: B
    ) async throws -> T {
        let bodyData = try encoder.encode(body)
        return try await request(type, endpoint: Endpoint(
            path: path,
            method: .post,
            headers: ["Content-Type": "application/json"],
            body: bodyData
        ))
    }

    func delete(path: String) async throws {
        try await request(endpoint: Endpoint(path: path, method: .delete))
    }

    // MARK: - Internal

    private func prepareRequest(for endpoint: Endpoint) async throws -> URLRequest {
        var request = endpoint.urlRequest(relativeTo: baseURL)
        for middleware in middlewares {
            request = try await middleware.prepare(request)
        }
        return request
    }

    private func validateResponse(_ response: URLResponse, data: Data) throws {
        guard let http = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        guard (200..<300).contains(http.statusCode) else {
            let apiError = try? decoder.decode(APIErrorBody.self, from: data)
            throw NetworkError.httpError(
                statusCode: http.statusCode,
                data: data,
                message: apiError?.message
            )
        }
    }
}
```

### Error Types

```swift
enum NetworkError: Error, Sendable, LocalizedError {
    case invalidResponse
    case httpError(statusCode: Int, data: Data, message: String? = nil)
    case noConnection
    case timedOut
    case cancelled

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid server response"
        case .httpError(let code, _, let message):
            return message ?? "HTTP error \(code)"
        case .noConnection:
            return "No internet connection"
        case .timedOut:
            return "Request timed out"
        case .cancelled:
            return nil
        }
    }

    static func from(_ urlError: URLError) -> NetworkError {
        switch urlError.code {
        case .notConnectedToInternet, .networkConnectionLost:
            return .noConnection
        case .timedOut:
            return .timedOut
        case .cancelled:
            return .cancelled
        default:
            return .invalidResponse
        }
    }
}

struct APIErrorBody: Decodable, Sendable {
    let code: String?
    let message: String?
}
```

### Request Middleware

```swift
protocol RequestMiddleware: Sendable {
    func prepare(_ request: URLRequest) async throws -> URLRequest
}

struct AuthMiddleware: RequestMiddleware {
    let tokenProvider: @Sendable () async throws -> String

    func prepare(_ request: URLRequest) async throws -> URLRequest {
        var request = request
        let token = try await tokenProvider()
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        return request
    }
}
```

---

## Request Builder Pattern

For complex request construction, a builder provides a fluent API that
reduces errors.

```swift
struct RequestBuilder: Sendable {
    private var method: String = "GET"
    private var path: String
    private var baseURL: URL
    private var queryItems: [URLQueryItem] = []
    private var headers: [String: String] = [:]
    private var body: Data?
    private var cachePolicy: URLRequest.CachePolicy = .useProtocolCachePolicy
    private var timeout: TimeInterval = 30

    init(baseURL: URL, path: String) {
        self.baseURL = baseURL
        self.path = path
    }

    func method(_ method: String) -> RequestBuilder {
        var copy = self
        copy.method = method
        return copy
    }

    func query(_ name: String, _ value: String?) -> RequestBuilder {
        guard let value else { return self }
        var copy = self
        copy.queryItems.append(URLQueryItem(name: name, value: value))
        return copy
    }

    func header(_ name: String, _ value: String) -> RequestBuilder {
        var copy = self
        copy.headers[name] = value
        return copy
    }

    func jsonBody<T: Encodable>(_ value: T) throws -> RequestBuilder {
        var copy = self
        copy.body = try JSONEncoder().encode(value)
        copy.headers["Content-Type"] = "application/json"
        return copy
    }

    func timeout(_ interval: TimeInterval) -> RequestBuilder {
        var copy = self
        copy.timeout = interval
        return copy
    }

    func cachePolicy(_ policy: URLRequest.CachePolicy) -> RequestBuilder {
        var copy = self
        copy.cachePolicy = policy
        return copy
    }

    func build() -> URLRequest {
        var components = URLComponents(
            url: baseURL.appendingPathComponent(path),
            resolvingAgainstBaseURL: true
        )!
        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }
        var request = URLRequest(url: components.url!)
        request.httpMethod = method
        request.httpBody = body
        request.cachePolicy = cachePolicy
        request.timeoutInterval = timeout
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        return request
    }
}

// Usage
let request = try RequestBuilder(baseURL: apiURL, path: "users")
    .method("POST")
    .header("X-Request-ID", UUID().uuidString)
    .jsonBody(CreateUserRequest(name: "Alice", email: "alice@example.com"))
    .timeout(15)
    .build()
```

---
