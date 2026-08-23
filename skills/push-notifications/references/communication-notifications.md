# Communication Notifications

Use this reference for Messages-style notification presentation. Treat it as a
service-extension and Siri/Intents integration, not as a generic rich-media
shortcut.

## Required setup

- Add the Communication Notifications capability to the relevant target.
- Add the intent class (for example `INSendMessageIntent`) to
  `NSUserActivityTypes` in the app and extension configuration as required by
  the chosen integration.
- Model a stable conversation identifier and sender handle.
- Donate an incoming `INInteraction` for the conversation.
- Call `UNMutableNotificationContent.updating(from:)` and keep the original
  content if donation or updating fails.

The service-extension trigger still applies: the remote payload must contain an
alert and `mutable-content: 1`. A silent push cannot be upgraded into a
communication notification by the extension.

## Bounded update flow

1. Validate sender, conversation, and authorization data from the payload.
2. Load a display-safe avatar or attachment within the extension time budget.
3. Build the intent and donate the incoming interaction.
4. Ask the content to update from the intent.
5. Call the content handler exactly once with updated, best-attempt, or original
   content, including the timeout path.

Do not place decryption secrets in App Group `UserDefaults`; use Keychain
Sharing. Do not make a failed avatar download suppress the underlying alert.

For the complete intent construction and extension example, read
[rich-notifications-complete.md](rich-notifications-complete.md#communication-notifications).
