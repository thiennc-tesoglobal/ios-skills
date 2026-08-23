# Notification Patterns

This is the routing index for notification runtime patterns. Load only the
focused reference needed by the task:

- [Notification runtime and routing](notification-runtime.md) — launch wiring,
  foreground presentation, responses, deep-link validation, categories, and
  idempotent actions.
- [Notification delivery testing](notification-testing.md) — `.apns`,
  `simctl`, APNs Sandbox Simulator coverage, provider/device matrices, and
  diagnostics.
- [Local notifications](local-notifications.md) — on-device time, calendar,
  and location scheduling, ownership, updates, and removal.

The former combined implementation is preserved in
[notification-patterns-complete.md](notification-patterns-complete.md). Use it
only for an end-to-end recipe or migration; it intentionally is not the default
context for a narrow task.
