# URLSession Upload and Download Patterns

Read this reference only when the task matches the sections below.

## Multipart Form Upload

Multipart/form-data uploads are common for file attachments. Build the
body manually -- no third-party library needed.

```swift
struct MultipartFormData: Sendable {
    private let boundary: String
    private var parts: [Part] = []

    init(boundary: String = UUID().uuidString) {
        self.boundary = boundary
    }

    var contentType: String {
        "multipart/form-data; boundary=\(boundary)"
    }

    mutating func addField(name: String, value: String) {
        parts.append(Part(
            headers: "Content-Disposition: form-data; name=\"\(name)\"",
            body: Data(value.utf8)
        ))
    }

    mutating func addFile(
        name: String,
        filename: String,
        mimeType: String,
        data: Data
    ) {
        parts.append(Part(
            headers: """
            Content-Disposition: form-data; name="\(name)"; filename="\(filename)"\r
            Content-Type: \(mimeType)
            """,
            body: data
        ))
    }

    func encode() -> Data {
        var data = Data()
        let crlf = "\r\n"
        for part in parts {
            data.append("--\(boundary)\(crlf)")
            data.append("\(part.headers)\(crlf)\(crlf)")
            data.append(part.body)
            data.append(crlf)
        }
        data.append("--\(boundary)--\(crlf)")
        return data
    }

    private struct Part: Sendable {
        let headers: String
        let body: Data
    }
}

extension Data {
    mutating func append(_ string: String) {
        append(Data(string.utf8))
    }
}

// Usage
var form = MultipartFormData()
form.addField(name: "title", value: "Profile Photo")
form.addFile(
    name: "image",
    filename: "photo.jpg",
    mimeType: "image/jpeg",
    data: imageData
)

var request = URLRequest(url: uploadURL)
request.httpMethod = "POST"
request.setValue(form.contentType, forHTTPHeaderField: "Content-Type")
request.httpBody = form.encode()

let (data, response) = try await URLSession.shared.upload(
    for: request,
    from: form.encode()
)
```

---

## Download with Progress Tracking

Use `bytes(for:)` for real-time progress. The response includes
`expectedContentLength` for calculating percentage.

```swift
@available(iOS 15.0, *)
func downloadWithProgress(
    from url: URL,
    progressHandler: @Sendable (Double) -> Void
) async throws -> Data {
    let (bytes, response) = try await URLSession.shared.bytes(from: url)

    let expectedLength = response.expectedContentLength
    var receivedData = Data()
    if expectedLength > 0 {
        receivedData.reserveCapacity(Int(expectedLength))
    }

    var receivedLength: Int64 = 0
    for try await byte in bytes {
        receivedData.append(byte)
        receivedLength += 1
        if expectedLength > 0 {
            let progress = Double(receivedLength) / Double(expectedLength)
            progressHandler(progress)
        }
    }

    return receivedData
}
```

For large files, prefer `URLSessionDownloadTask` with a delegate for
better memory efficiency and background support.

### Download to File with Progress (Delegate-Based)

```swift
@available(iOS 15.0, *)
final class DownloadManager: NSObject, URLSessionDownloadDelegate, Sendable {
    private let continuation: AsyncStream<DownloadEvent>.Continuation

    enum DownloadEvent: Sendable {
        case progress(Double)
        case completed(URL)
        case failed(Error)
    }

    static func download(from url: URL) -> AsyncStream<DownloadEvent> {
        AsyncStream { continuation in
            let manager = DownloadManager(continuation: continuation)
            let session = URLSession(
                configuration: .default,
                delegate: manager,
                delegateQueue: nil
            )
            session.downloadTask(with: url).resume()
        }
    }

    private init(continuation: AsyncStream<DownloadEvent>.Continuation) {
        self.continuation = continuation
    }

    nonisolated func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        // Move file to permanent location before this method returns
        let destination = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        do {
            try FileManager.default.moveItem(at: location, to: destination)
            continuation.yield(.completed(destination))
        } catch {
            continuation.yield(.failed(error))
        }
        continuation.finish()
    }

    nonisolated func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        guard totalBytesExpectedToWrite > 0 else { return }
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        continuation.yield(.progress(progress))
    }

    nonisolated func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: (any Error)?
    ) {
        if let error {
            continuation.yield(.failed(error))
            continuation.finish()
        }
    }
}
```

---
