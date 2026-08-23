# Notification Runtime and Routing

Use this reference for launch wiring, foreground presentation, tap/action
routing, categories, and idempotent handling. Keep the delegate thin: validate
payload data, then hand a typed destination to the app's existing navigation or
state owner.

## Install the delegates during launch

Set the notification-center delegate before a response can arrive. Install the
application delegate callbacks in the app delegate or its adaptor, not in a
transient SwiftUI view.

```swift
import SwiftUI
import UIKit
import UserNotifications

@main
struct ExampleApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup { RootView() }
    }
}

final class AppDelegate: NSObject, UIApplicationDelegate {
    let notificationDelegate = NotificationDelegate()

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions options: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        UNUserNotificationCenter.current().delegate = notificationDelegate
        NotificationCategoryRegistry.register()
        return true
    }
}
```

Ask for authorization in product context and keep APNs token registration
separate; the APNs lifecycle reference owns that contract.

## Foreground and response handling

```swift
@MainActor
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        let content = notification.request.content
        guard PayloadValidator.isAllowed(content.userInfo) else { return [] }
        return [.banner, .list, .sound, .badge]
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        guard let destination = PayloadValidator.destination(
            from: response.notification.request.content.userInfo
        ) else { return }
        await AppRouter.shared.open(destination, action: response.actionIdentifier)
    }
}
```

Foreground receipt does not imply presentation. Return only options the product
intends to show, and handle body taps, custom actions, and dismissals as
separate events. Treat payload identifiers as untrusted; re-check authorization
and current app state before navigation or mutation.

## Categories and actions

Register categories at launch. The payload's `category` value and a local
request's `categoryIdentifier` must exactly match the registered identifier.

```swift
enum NotificationCategoryRegistry {
    static let message = "MESSAGE"
    static let markRead = "MARK_READ"

    static func register() {
        let markReadAction = UNNotificationAction(
            identifier: markRead,
            title: "Mark Read",
            options: []
        )
        let category = UNNotificationCategory(
            identifier: message,
            actions: [markReadAction],
            intentIdentifiers: [],
            options: []
        )
        UNUserNotificationCenter.current().setNotificationCategories([category])
    }
}
```

Choose action options deliberately: `.foreground` for UI work,
`.authenticationRequired` for sensitive work, `.destructive` for irreversible
work, and `UNTextInputNotificationAction` for inline text. Make each action
idempotent because delivery, retries, or user taps can repeat it.

## Full recipes

For a complete, copyable app-delegate/router implementation—including the
legacy combined examples—read
[notification-patterns-complete.md](notification-patterns-complete.md). It is
an archive of full recipes; load it only when the focused guidance above is not
enough.
