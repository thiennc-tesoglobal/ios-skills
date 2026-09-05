# Background URLSession Transfers

Use this reference when configuring out-of-process background download and upload tasks, handling app relaunch events, and managing download progress in iOS.

## Contents

- [Background URLSession Configuration](#background-urlsession-configuration)
- [Background Download Tasks](#background-download-tasks)
- [Handling Background Session Events](#handling-background-session-events)
- [Background Upload Tasks](#background-upload-tasks)
- [Background Session Gotchas](#background-session-gotchas)
- [Combining Background Downloads with SwiftUI Progress](#combining-background-downloads-with-swiftui-progress)

---

Background sessions allow HTTP/HTTPS upload and download transfers to continue
when the app is suspended or terminated by the system. The system manages the
transfer in a separate process and wakes the app on completion.

### Why Background Sessions

- Downloads/uploads survive app suspension, system termination, and device restarts.
- The system handles retries for network failures automatically.
- Required for any transfer the user expects to complete even if they
  switch away from the app (e.g., file sync, media downloads).

If the user force-quits the app from the multitasking screen, iOS cancels the
background transfers and does not relaunch the app until the user opens it
again.

### Configuration

```swift
@available(iOS 15.0, *)
final class BackgroundDownloadManager: NSObject, Sendable {
    static let shared = BackgroundDownloadManager()

    /// Use a unique identifier tied to your app's bundle ID.
    /// The system uses this to reconnect to the session after relaunch.
    private let sessionID = "com.example.app.background-downloads"

    /// Lazy-initialized background session. Must use a delegate, not async/await,
    /// because the system delivers events through the delegate after app relaunch.
    lazy var session: URLSession = {
        let config = URLSessionConfiguration.background(
            withIdentifier: sessionID
        )
        config.isDiscretionary = false          // Start immediately (true = system-scheduled)
        config.sessionSendsLaunchEvents = true  // Wake app on completion
        config.allowsExpensiveNetworkAccess = true
        config.allowsConstrainedNetworkAccess = false  // Respect Low Data Mode
        config.timeoutIntervalForResource = 24 * 60 * 60  // 24 hours

        return URLSession(
            configuration: config,
            delegate: self,
            delegateQueue: nil  // Use a system-managed serial queue
        )
    }()

    /// Store completionHandler from AppDelegate for system callback
    nonisolated(unsafe) var backgroundCompletionHandler: (() -> Void)?
}
```

### Key Configuration Options

| Property | Effect |
|---|---|
| `isDiscretionary` | `true` = system schedules for optimal battery/network. Use for non-urgent sync. `false` = start immediately. |
| `sessionSendsLaunchEvents` | Relaunches the app when transfers complete. Required for completion handling. |
| `allowsConstrainedNetworkAccess` | `false` = honor Low Data Mode. Good for optional downloads. |
| `allowsExpensiveNetworkAccess` | `false` = Wi-Fi only. Use for large transfers. |
| `timeoutIntervalForResource` | Maximum time for the entire transfer. Default is 7 days. |

---

## Background Download Tasks

Background downloads must use `downloadTask(with:)`, not `data(for:)`.
The async/await overloads are not supported for background sessions --
you must use the delegate pattern.

```swift
extension BackgroundDownloadManager {
    func startDownload(from url: URL) -> URLSessionDownloadTask {
        let task = session.downloadTask(with: url)
        task.earliestBeginDate = Date()  // Start now
        task.countOfBytesClientExpectsToSend = 0
        task.countOfBytesClientExpectsToReceive = 50 * 1024 * 1024  // Estimated size
        task.resume()
        return task
    }

    func startDownload(from url: URL, resumeData: Data) -> URLSessionDownloadTask {
        let task = session.downloadTask(withResumeData: resumeData)
        task.resume()
        return task
    }
}
```

### Download Delegate

```swift
extension BackgroundDownloadManager: URLSessionDownloadDelegate {
    nonisolated func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        // CRITICAL: Move or open the file before this method returns.
        // The temporary file is only available until the delegate returns.
        let destinationDir = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first!

        let filename = downloadTask.originalRequest?.url?.lastPathComponent ?? UUID().uuidString
        let destination = destinationDir.appendingPathComponent(filename)

        do {
            // Remove existing file if present
            if FileManager.default.fileExists(atPath: destination.path) {
                try FileManager.default.removeItem(at: destination)
            }
            try FileManager.default.moveItem(at: location, to: destination)
            // Notify the app (post notification, update state, etc.)
        } catch {
            // Handle file move failure
        }
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
        // Update progress UI (dispatch to main if needed)
    }

    nonisolated func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: (any Error)?
    ) {
        guard let error else { return }  // Success handled in didFinishDownloadingTo

        // Check for resume data on failure
        let nsError = error as NSError
        if let resumeData = nsError.userInfo[NSURLSessionDownloadTaskResumeData] as? Data {
            // Store resumeData for retry
            saveResumeData(resumeData, for: task)
        }
    }

    private func saveResumeData(_ data: Data, for task: URLSessionTask) {
        // Persist resume data to disk for later retry
        let key = task.originalRequest?.url?.absoluteString ?? ""
        let path = FileManager.default.temporaryDirectory
            .appendingPathComponent("resume-\(key.hashValue)")
        try? data.write(to: path)
    }
}
```

---

## Handling Background Session Events

When the system completes a background transfer and the app is not
running, it relaunches the app and calls the `AppDelegate` method. If you use
the completion-handler overload, call the system's completion handler after
processing all events.

### UIKit App Delegate

```swift
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        handleEventsForBackgroundURLSession identifier: String,
        completionHandler: @escaping () -> Void
    ) {
        // Store the completion handler. The BackgroundDownloadManager will
        // call it after processing all pending events.
        BackgroundDownloadManager.shared.backgroundCompletionHandler = completionHandler

        // Accessing .session triggers lazy initialization, which reconnects
        // to the background session and starts delivering delegate events.
        _ = BackgroundDownloadManager.shared.session
    }
}
```

### Session-Level Delegate

```swift
extension BackgroundDownloadManager: URLSessionDelegate {
    nonisolated func urlSessionDidFinishEvents(
        forBackgroundURLSession session: URLSession
    ) {
        // Called after ALL pending delegate events have been delivered.
        // Call the stored completion handler on the main thread.
        Task { @MainActor in
            backgroundCompletionHandler?()
            backgroundCompletionHandler = nil
        }
    }
}
```

### SwiftUI App with AppDelegate Adapter

```swift
@main
struct MyApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

**Important:** For the handler-based `UIApplicationDelegate` overload, the
completion handler must be called exactly once and on the main thread. Failing
to call it causes the system to take a snapshot of the app in the wrong state
and may waste background runtime.

---

## Background Upload Tasks

Background uploads require data from a file, not from memory.

```swift
extension BackgroundDownloadManager {
    func startUpload(
        to url: URL,
        fileURL: URL,
        method: String = "POST",
        headers: [String: String] = [:]
    ) -> URLSessionUploadTask {
        var request = URLRequest(url: url)
        request.httpMethod = method
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }

        let task = session.uploadTask(with: request, fromFile: fileURL)
        task.resume()
        return task
    }
}
```

### Upload Delegate Methods

```swift
extension BackgroundDownloadManager {
    nonisolated func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didSendBodyData bytesSent: Int64,
        totalBytesSent: Int64,
        totalBytesExpectedToSend: Int64
    ) {
        guard totalBytesExpectedToSend > 0 else { return }
        let progress = Double(totalBytesSent) / Double(totalBytesExpectedToSend)
        // Update progress UI
    }
}
```

**Constraints of background uploads:**
- Data must come from a file (`uploadTask(with:fromFile:)`).
- `uploadTask(with:from: Data)` is not supported in background sessions.
- Write multipart form data to a temporary file first, then upload.

---

## URLSessionWebSocketTask


### The session identifier must be unique per app
If two sessions share the same identifier, events may be delivered to
the wrong delegate. Use your bundle identifier as a prefix.

### Background sessions do not support async/await overloads
The `data(for:)` and `download(for:)` async methods are not available
on background sessions. Use `downloadTask(with:)` and the delegate.

### Only download and upload tasks are supported
Data tasks (`dataTask`) are not supported in background sessions. Convert
data requests to download tasks if needed for background execution.
WebSocket tasks are not background transfer tasks; reconnect them when the app
is active again.

### The app may be terminated and relaunched
Store any state you need (task identifiers, file destinations) to disk.
Do not rely on in-memory state surviving a background relaunch.
User force-quit is different from system termination: iOS cancels outstanding
background transfers and will not relaunch the app automatically.

### File must be moved or opened in didFinishDownloadingTo
The temporary file at `location` is available until the delegate method
returns. Move it to preserve it, or open it for reading before returning.

### Call the system completion handler exactly once
Store the completion handler from
`application(_:handleEventsForBackgroundURLSession:completionHandler:)`
and invoke it in `urlSessionDidFinishEvents(forBackgroundURLSession:)`
on the main thread.

### Test on a real device
Background session behavior differs significantly between the Simulator
and real devices. Always test background transfers on hardware.

---

## Combining Background Downloads with SwiftUI Progress

Bridge the delegate-based background download to an `@Observable` model
for live UI updates.

```swift
@MainActor
@Observable final class DownloadTracker {
    var downloads: [URL: DownloadProgress] = [:]

    struct DownloadProgress: Sendable {
        var fractionCompleted: Double = 0
        var state: State = .downloading

        enum State: Sendable { case downloading, completed, failed }
    }

    func updateProgress(for url: URL, fraction: Double) {
        downloads[url, default: DownloadProgress()].fractionCompleted = fraction
    }

    func markCompleted(for url: URL) {
        downloads[url]?.state = .completed
        downloads[url]?.fractionCompleted = 1.0
    }

    func markFailed(for url: URL) {
        downloads[url]?.state = .failed
    }
}
```

Wire the delegate to the tracker:

```swift
extension BackgroundDownloadManager {
    // Called from delegate methods; dispatches to MainActor
    func reportProgress(for url: URL, fraction: Double) {
        Task { @MainActor in
            downloadTracker.updateProgress(for: url, fraction: fraction)
        }
    }
}
```

---

## WebSocket Authentication
