# Notification Content Extensions

Use this reference for custom expanded notification UI. A content extension
does not replace the service extension: the service extension prepares content,
while the content extension renders an expanded interface and handles actions.

## Scope and configuration

- Add a Notification Content Extension target and its `NSExtension` declaration.
- Match the notification category identifier in the extension configuration and
  in the delivered payload/local request.
- Keep the extension UI bounded and useful when media, network data, or the
  containing app is unavailable.
- Use `UNNotificationContentExtension` lifecycle callbacks for the initial
  notification and response/action events.

Prefer system controls and Dynamic Type where possible. If media playback is
needed, declare and test the relevant audio/session behavior; do not assume the
extension has the same lifecycle or memory budget as the containing app.

## Response handling

Return an explicit `UNNotificationContentExtensionResponseOption` for custom
actions. Use `.dismiss`, `.dismissAndForwardAction`, or `.doNotDismiss` based on
product behavior, and make the action idempotent. Validate payload identifiers
again before mutating app state; forward a destination to the app rather than
constructing a second navigation stack in the extension.

For service-extension preparation, attachment format/size details, and a full
view-controller recipe, read
[rich-notifications-complete.md](rich-notifications-complete.md#notification-content-extension).
