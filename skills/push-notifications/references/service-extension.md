# Notification Service Extensions

Use this reference when a remote alert needs bounded content mutation before
display. A service extension runs only for an alerting remote notification with
`mutable-content: 1`; a silent-only, sound-only, or badge-only push does not
launch it. The extension has roughly 30 seconds, so every path must fall back
quickly.

## Exact-once completion

The normal task and `serviceExtensionTimeWillExpire()` can race. Guard the
handler with a lock (or an equivalent serialized state machine), keep the
original and best-attempt content, cancel in-flight work after finishing, and
invoke the handler exactly once.

```swift
import Foundation
import UserNotifications

final class NotificationService: UNNotificationServiceExtension {
    private var handler: ((UNNotificationContent) -> Void)?
    private var original: UNNotificationContent?
    private var bestAttempt: UNMutableNotificationContent?
    private var task: Task<Void, Never>?
    private let lock = NSLock()
    private var completed = false

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        handler = contentHandler
        original = request.content
        bestAttempt = request.content.mutableCopy() as? UNMutableNotificationContent

        guard let content = bestAttempt else {
            finish(original)
            return
        }

        task = Task { [weak self] in
            guard let self else { return }
            await self.modify(content)
            self.finish(content)
        }
    }

    override func serviceExtensionTimeWillExpire() {
        finish(bestAttempt ?? original)
    }

    private func finish(_ content: UNNotificationContent?) {
        lock.lock()
        guard !completed, let content, let handler else {
            lock.unlock()
            return
        }
        completed = true
        self.handler = nil
        task?.cancel()
        task = nil
        lock.unlock()
        handler(content)
    }

    private func modify(_ content: UNMutableNotificationContent) async {
        // Keep downloads, decryption, and attachment creation bounded.
    }
}
```

When work fails, leave the original or best-attempt alert intact. Download
attachments into the extension's temporary directory, validate the MIME/type
and size, then create `UNNotificationAttachment` from the local file. Use
Keychain Sharing for decryption keys; App Groups are for shared files or
defaults, not secret storage.

For communication notifications, load the additional capability and intent
configuration from [communication-notifications.md](communication-notifications.md).
For a complete image/decryption implementation, read
[rich-notifications-complete.md](rich-notifications-complete.md#complete-service-extension-example).
