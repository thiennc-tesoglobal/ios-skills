# URLSession Pagination and URLProtocol Testing

Read this reference only when the task matches the sections below.

## Cursor-Based Pagination

A reusable paginator that conforms to `AsyncSequence`, yielding pages
of results until the server indicates no more data.

```swift
struct PageResponse<T: Decodable & Sendable>: Decodable, Sendable {
    let data: [T]
    let pagination: PaginationInfo
}

struct PaginationInfo: Decodable, Sendable {
    let nextCursor: String?
    let hasMore: Bool
}

struct CursorPaginator<T: Decodable & Sendable>: AsyncSequence {
    typealias Element = [T]

    private let fetchPage: @Sendable (String?) async throws -> PageResponse<T>

    init(fetchPage: @escaping @Sendable (String?) async throws -> PageResponse<T>) {
        self.fetchPage = fetchPage
    }

    func makeAsyncIterator() -> Iterator {
        Iterator(fetchPage: fetchPage)
    }

    struct Iterator: AsyncIteratorProtocol {
        private let fetchPage: @Sendable (String?) async throws -> PageResponse<T>
        private var cursor: String?
        private var exhausted = false

        init(fetchPage: @escaping @Sendable (String?) async throws -> PageResponse<T>) {
            self.fetchPage = fetchPage
        }

        mutating func next() async throws -> [T]? {
            guard !exhausted else { return nil }
            try Task.checkCancellation()

            let response = try await fetchPage(cursor)
            cursor = response.pagination.nextCursor
            exhausted = !response.pagination.hasMore

            return response.data.isEmpty ? nil : response.data
        }
    }
}

// Usage
let paginator = CursorPaginator<User> { cursor in
    var queryItems = [URLQueryItem(name: "limit", value: "50")]
    if let cursor {
        queryItems.append(URLQueryItem(name: "cursor", value: cursor))
    }
    return try await client.get(
        PageResponse<User>.self,
        path: "users",
        queryItems: queryItems
    )
}

var allUsers: [User] = []
for try await batch in paginator {
    allUsers.append(contentsOf: batch)
}
```

---

## Offset-Based Pagination

```swift
struct OffsetPaginator<T: Decodable & Sendable>: AsyncSequence {
    typealias Element = [T]

    private let pageSize: Int
    private let fetchPage: @Sendable (Int, Int) async throws -> [T]

    init(
        pageSize: Int = 20,
        fetchPage: @escaping @Sendable (_ offset: Int, _ limit: Int) async throws -> [T]
    ) {
        self.pageSize = pageSize
        self.fetchPage = fetchPage
    }

    func makeAsyncIterator() -> Iterator {
        Iterator(pageSize: pageSize, fetchPage: fetchPage)
    }

    struct Iterator: AsyncIteratorProtocol {
        private let pageSize: Int
        private let fetchPage: @Sendable (Int, Int) async throws -> [T]
        private var offset = 0
        private var exhausted = false

        init(
            pageSize: Int,
            fetchPage: @escaping @Sendable (Int, Int) async throws -> [T]
        ) {
            self.pageSize = pageSize
            self.fetchPage = fetchPage
        }

        mutating func next() async throws -> [T]? {
            guard !exhausted else { return nil }
            try Task.checkCancellation()

            let items = try await fetchPage(offset, pageSize)
            offset += items.count
            if items.count < pageSize { exhausted = true }

            return items.isEmpty ? nil : items
        }
    }
}
```

---

## URLProtocol Mock for Testing

`URLProtocol` is the correct way to mock network responses at the
transport level. It works with any URLSession configuration and does
not require changing production code.

```swift
final class MockURLProtocol: URLProtocol {
    nonisolated(unsafe) static var requestHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?

    override class func canInit(with request: URLRequest) -> Bool { true }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        guard let handler = Self.requestHandler else {
            fatalError("MockURLProtocol.requestHandler is not set")
        }

        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}
```

### Test Setup

```swift
import Testing

@Suite struct APIClientTests {
    let client: APIClient
    let session: URLSession

    init() {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [MockURLProtocol.self]
        session = URLSession(configuration: config)
        client = APIClient(
            baseURL: URL(string: "https://api.example.com")!,
            session: session
        )
    }

    @Test func fetchUsersDecodesCorrectly() async throws {
        let usersJSON = """
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        """
        MockURLProtocol.requestHandler = { request in
            #expect(request.url?.path == "/users")
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 200,
                httpVersion: nil,
                headerFields: ["Content-Type": "application/json"]
            )!
            return (response, Data(usersJSON.utf8))
        }

        let users: [User] = try await client.get([User].self, path: "users")
        #expect(users.count == 2)
        #expect(users[0].name == "Alice")
    }

    @Test func fetchReturnsHTTPError() async throws {
        MockURLProtocol.requestHandler = { request in
            let response = HTTPURLResponse(
                url: request.url!,
                statusCode: 404,
                httpVersion: nil,
                headerFields: nil
            )!
            return (response, Data())
        }

        await #expect(throws: NetworkError.self) {
            let _: [User] = try await client.get([User].self, path: "missing")
        }
    }

    @Test func requestIncludesAuthHeader() async throws {
        let authClient = APIClient(
            baseURL: URL(string: "https://api.example.com")!,
            session: session,
            middlewares: [AuthMiddleware { "test-token" }]
        )

        MockURLProtocol.requestHandler = { request in
            #expect(request.value(forHTTPHeaderField: "Authorization") == "Bearer test-token")
            let response = HTTPURLResponse(
                url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil
            )!
            return (response, Data("{}".utf8))
        }

        let _: EmptyResponse = try await authClient.get(EmptyResponse.self, path: "me")
    }
}

struct EmptyResponse: Decodable, Sendable {}
```

---
