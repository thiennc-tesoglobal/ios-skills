---
name: app-intents
description: "Implement App Intents for Siri, Shortcuts, Spotlight, widgets, Control Center, and Apple Intelligence on iOS. Covers AppIntent actions, AppEntity and EntityQuery models, AppShortcutsProvider phrases, IndexedEntity Spotlight indexing, WidgetConfigurationIntent, SnippetIntent, and assistant schemas. Use when exposing app actions or entities to system surfaces."
---

# App Intents

Expose app actions and entities to Siri, Shortcuts, Spotlight search, interactive widgets, Control Center, and Apple Intelligence using the `AppIntents` framework. Targets Swift 6.3 / iOS 26+.

## Contents

- [Triage Workflow](#triage-workflow)
- [System Surface Integration Matrix](#system-surface-integration-matrix)
- [AppEntity and EntityQuery](#appentity-and-entityquery)
- [AppShortcuts and Voice Phrases](#appshortcuts-and-voice-phrases)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Triage Workflow

1. **Select core actions**: Expose 1–3 high-value user tasks that make sense outside the app.
2. **Define AppEntity models**: Create identifiable shadow models (`AppEntity`) for domain data referenced by the intent.
3. **Implement AppIntent**: Define parameters with `@Parameter`, implement `perform() async throws -> some IntentResult`.
4. **Register voice phrases**: Provide natural voice invocations with `AppShortcutsProvider`.
5. **Verify system surface**: Test discovery in Shortcuts, Spotlight search, and widget configuration.

## System Surface Integration Matrix

| System Surface | Protocol / Attribute | Purpose |
|---|---|---|
| Siri & Shortcuts | `AppIntent` | Direct voice and shortcut automation |
| Configurable Widgets | `WidgetConfigurationIntent` | Supplies parameters to widget timelines |
| Control Center | `ControlConfigurationIntent` | Powers Control Center buttons and toggles |
| Spotlight Search | `IndexedEntity` | Indexes domain items into on-device Spotlight |
| Apple Intelligence | `@AppIntent(schema:)` | Assistant semantic reasoning and tooling |
| Interactive Snippets | `SnippetIntent` | In-line system confirmation views (iOS 26+) |

## AppEntity and EntityQuery

Expose domain data to intents using `AppEntity`:
```swift
struct OrderEntity: AppEntity {
    static var defaultQuery = OrderQuery()
    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Order")

    var id: UUID
    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(orderNumber)")
    }
}
```

Implement `EntityQuery` to resolve identifiers (`entities(for:)`) and provide suggested choices (`suggestedEntities()`).

## AppShortcuts and Voice Phrases

Expose voice triggers without requiring user setup via `AppShortcutsProvider`:
- Register app shortcut phrases using `\(.applicationName)` token.
- Provide clean fallback phrases for Siri matching.

## Route by Task

- For `@Parameter` types, `AppEntity` declarations, and `EntityQuery` variants, read [Parameters and Entity Queries](references/parameters-and-entity-queries.md).
- For widget controls, interactive snippets, and Lock Screen integrations, read [System Surfaces](references/system-surfaces.md).
- For Siri voice matching, confirmation dialogs, and authentication policies, read [Assistant Focus and Intent Behavior](references/assistant-focus-and-intent-behavior.md).
- For Spotlight search indexing, deep link routing, and `IndexedEntity`, read [URL and Spotlight Integration](references/url-and-spotlight-integration.md).

## Common Mistakes

- Performing UI navigation or view presentation directly inside `perform()` without returning an `OpenURLIntent` or navigation result.
- Forgetting to provide an `EntityQuery` for custom `@Parameter` entity types, breaking Shortcuts parameter selection.
- Hardcoding the app name in `AppShortcut` phrases instead of using `\(.applicationName)`.
- Running long network calls in `perform()` without checking `Task.isCancelled` or providing progress dialogs.
- Omitting `typeDisplayRepresentation` on `AppEntity` conformances.

## Review Checklist

- [ ] Intent conforms to `AppIntent` or specialized surface protocol
- [ ] Parameters have clear titles and valid default/suggested values
- [ ] Entities implement `EntityQuery` with `entities(for:)` and `suggestedEntities()`
- [ ] `perform()` returns an appropriate `IntentResult` (e.g. `.result()`, `.result(dialog:)`)
- [ ] Shortcuts phrases use `\(.applicationName)` macro
- [ ] Destructive actions declare `requestConfirmation()` before executing
- [ ] Sensitive actions require device authentication where appropriate

## References

- [Parameters and entity query implementations](references/parameters-and-entity-queries.md)
- [System surfaces: widgets, controls, and snippets](references/system-surfaces.md)
- [Assistant focus, voice dialogs, and intent behavior](references/assistant-focus-and-intent-behavior.md)
- [URL and Spotlight search indexing](references/url-and-spotlight-integration.md)
- [App Intents documentation](https://sosumi.ai/documentation/appintents)
- [AppIntent](https://sosumi.ai/documentation/appintents/appintent)
