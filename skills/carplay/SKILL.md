---
name: carplay
description: "Builds eligible CarPlay navigation, audio, communication, EV charging, parking, or ordering apps with template scenes. Use for entitlements, scene delegates, interface-controller hierarchies, lists, maps, Now Playing, dashboard displays, or CarPlay Simulator verification."
---

# CarPlay

Build category-entitled, template-based CarPlay apps for the vehicle display.
Scope: Swift 6.3, iOS 26+.

See [references/carplay-patterns.md](references/carplay-patterns.md) for extended patterns including full
navigation sessions, dashboard scenes, and advanced template composition.

Scope boundary: full CarPlay framework apps use category entitlements,
`CPTemplateApplicationScene`, `CPTemplateApplicationSceneDelegate`,
`CPInterfaceController`, and system `CPTemplate` navigation. CarPlay-visible
WidgetKit widgets and ActivityKit Live Activities are separate system
experiences; route their implementation to those domains while keeping
CarPlay-specific validation here.

## Workflow

1. Confirm the app category is eligible and obtain the exact CarPlay entitlement before building templates.
2. Configure the CarPlay scene role and retain the interface controller supplied by the scene delegate.
3. Build only category-allowed template hierarchies and respect tab, list, image, and interaction limits.
4. Keep navigation, audio, communication, and point-of-interest behavior behind their specific templates and completion handlers.
5. Verify reconnect, day/night appearance, multiple display sizes, driving restrictions, and physical vehicle behavior where required.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for entitlements, scenes, templates, navigation, audio, communication, POI, and Simulator testing.
- Read [extended CarPlay patterns](references/carplay-patterns.md) for dashboard/instrument-cluster scenes, complete navigation flows, and complex tab composition.

## Core Decisions

- Do not draw arbitrary custom UI where CarPlay requires templates.
- Never push or present templates that Apple exposes only as shared/system surfaces.
- Use the correct scene delegate callback for the app category and display role.
- Call template completion handlers exactly once and keep handlers responsive.

## Common Mistakes

### DON'T: Use the wrong scene delegate method

Navigation apps must implement `templateApplicationScene(_:didConnect:to:)`
(with `CPWindow`). Non-navigation apps use
`templateApplicationScene(_:didConnect:)` (no window). Using the wrong
variant produces no CarPlay UI.

### DON'T: Draw custom UI in the navigation window

`CPWindow` is exclusively for map content. All overlays, alerts, and
controls must use CarPlay templates.

### DON'T: Push or present CPTabBarTemplate

`CPTabBarTemplate` can only be set as root. Pushing or presenting it fails.
Use `setRootTemplate(_:animated:completion:)`.

### DON'T: Instantiate CPNowPlayingTemplate

Use `CPNowPlayingTemplate.shared`. Creating a new instance causes issues.

### DON'T: Add handlers to CPMessageListItem

`CPMessageListItem` is Siri-managed, unlike `CPListItem`. Do not set
`message.handler`; use the item configuration and `userInfo` for context.

### DON'T: Treat widgets as CarPlay template apps

CarPlay-visible widgets and Live Activities belong to WidgetKit and
ActivityKit. Use this skill for category-entitled CarPlay template app scenes
and for validating those surfaces in the car context.

### DON'T: Ignore vehicle display limits

Check `CPSessionConfiguration.limitedUserInterfaces` and respect
`maximumItemCount` / `maximumSectionCount` on list templates.

### DON'T: Forget to call the completion handler

`CPListItem.handler` must call its completion handler in every code path.
Failure leaves the list in a loading state.

## Review Checklist

- [ ] Correct CarPlay entitlement key in `Entitlements.plist`
- [ ] `UIApplicationSupportsMultipleScenes` set to `true`
- [ ] `CPTemplateApplicationSceneSessionRoleApplication` scene in Info.plist
- [ ] Scene delegate class name matches `UISceneDelegateClassName`
- [ ] Correct delegate method used (with/without `CPWindow`)
- [ ] Root template set in `didConnect` before returning
- [ ] Interface controller and window references cleared on disconnect
- [ ] `CPTabBarTemplate` only used as root, never pushed
- [ ] `CPNowPlayingTemplate.shared` used, not a new instance
- [ ] Communication rows use `CPMessageListItem` without custom handlers
- [ ] WidgetKit/ActivityKit surfaces routed outside CarPlay template app code
- [ ] `maximumItemCount`/`maximumSectionCount` checked before populating lists
- [ ] `CPListItem.handler` calls completion in every path
- [ ] Map-only content in `CPWindow` root view controller (navigation apps)
- [ ] App functions while iPhone is locked
- [ ] Tested at minimum, standard, and high-resolution simulator sizes
- [ ] Audio session deactivated when not actively playing

## References

- Extended patterns (dashboard, instrument cluster, full nav flow, tab composition): [references/carplay-patterns.md](references/carplay-patterns.md)
- [CarPlay framework](https://sosumi.ai/documentation/carplay)
- [CPTemplateApplicationSceneDelegate](https://sosumi.ai/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPInterfaceController](https://sosumi.ai/documentation/carplay/cpinterfacecontroller)
- [CPMapTemplate](https://sosumi.ai/documentation/carplay/cpmaptemplate)
- [CPListTemplate](https://sosumi.ai/documentation/carplay/cplisttemplate)
- [CPNowPlayingTemplate](https://sosumi.ai/documentation/carplay/cpnowplayingtemplate)
- [CPPointOfInterestTemplate](https://sosumi.ai/documentation/carplay/cppointofinteresttemplate)
- [CPNavigationSession](https://sosumi.ai/documentation/carplay/cpnavigationsession)
- [Requesting CarPlay Entitlements](https://sosumi.ai/documentation/carplay/requesting-carplay-entitlements)
- [Displaying Content in CarPlay](https://sosumi.ai/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://sosumi.ai/documentation/carplay/using-the-carplay-simulator)
- [CarPlay HIG](https://sosumi.ai/design/human-interface-guidelines/carplay)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
