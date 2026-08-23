# Rich Notifications

This is the routing index for notification extensions. Load only the focused
reference needed by the task:

- [Notification service extensions](service-extension.md) — alert trigger,
  bounded mutation, attachment fallback, and exactly-once completion.
- [Notification content extensions](content-extension.md) — custom expanded UI,
  category configuration, media, and response options.
- [Communication notifications](communication-notifications.md) — capability,
  intent activity types, donation, and `content.updating(from:)`.

The former all-in-one implementation is preserved in
[rich-notifications-complete.md](rich-notifications-complete.md). Use it for a
full copyable recipe or migration; it is not the default context for a narrow
extension task.
