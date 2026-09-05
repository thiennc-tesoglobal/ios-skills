---
name: tipkit
description: "Implement and review Apple TipKit feature-discovery UI for iOS 17+ apps. Use when adding or auditing in-app tips, contextual help, coach marks, Tip, TipView, popoverTip, rules, events, actions, display frequency, testing overrides, reusable tip identifiers, or iOS 18+ TipGroup and CloudKit tip sync; avoid for generic SwiftUI navigation or layout outside tip presentation."
---

# TipKit

Use TipKit for small, contextual feature-discovery moments: inline tips, popover tips, rule-gated education, and lightweight coach marks. Keep generic SwiftUI navigation, layout, and long first-run onboarding flows in their sibling skills.

## Contents

- [Availability & Configuration](#availability--configuration)
- [Defining Tips](#defining-tips)
- [Presenting Tips](#presenting-tips)
- [Rules & Events](#rules--events)
- [Tip Groups (iOS 18+)](#tip-groups-ios-18)
- [Testing Overrides](#testing-overrides)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Availability & Configuration

Core TipKit (`Tip`, `TipView`, `popoverTip`, rules, events) is iOS 17+. Gate iOS 18+ APIs (`TipGroup`, `.cloudKitContainer`, `MaxDisplayDuration`) and iOS 26+ APIs (`resetEligibility()`) explicitly.

Call `Tips.configure(_:)` once during app startup in `init()` or `application(_:didFinishLaunchingWithOptions:)`:

```swift
import SwiftUI
import TipKit

@main
struct MyApp: App {
    init() {
        do {
            try Tips.configure([
                .datastoreLocation(.applicationDefault),
                .displayFrequency(.daily)
            ])
        } catch {
            assertionFailure("TipKit configuration failed: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

For app groups sharing tip state, use `.groupContainer(identifier:)`. On iOS 18+, sync tip state across devices by adding `.cloudKitContainer(.named("iCloud.com.example.tips"))`.

## Defining Tips

Create tips by conforming to the `Tip` protocol:

```swift
struct BookmarkTip: Tip {
    var title: Text { Text("Save for Later") }
    var message: Text? { Text("Tap to bookmark your favorite articles.") }
    var image: Image? { Image(systemName: "bookmark") }

    @Parameter
    static var hasViewedArticle: Bool = false

    static let bookmarkEvent = Event(id: "didBookmarkArticle")

    var rules: [Rule] {
        #Rule(Self.$hasViewedArticle) { $0 == true }
        #Rule(Self.bookmarkEvent) { $0.donations.count < 3 }
    }

    var actions: [Action] {
        Action(id: "learn-more", title: "Learn More") {
            // Action handler
        }
    }
}
```

## Presenting Tips

Present tips inline within layouts or anchored as popovers:

```swift
// Inline presentation
TipView(BookmarkTip(), arrowEdge: .bottom)

// Popover presentation anchored to a control
Button("Bookmark", systemImage: "bookmark") {
    saveBookmark()
    BookmarkTip.bookmarkEvent.donate()
}
.popoverTip(BookmarkTip(), arrowEdge: .top)
```

Invalidate tips when the user completes the taught action: `BookmarkTip().invalidate(reason: .actionPerformed)`.

## Rules & Events

- **Parameters (`#Rule(Self.$param)`)**: Persistent state flags representing user characteristics or settings.
- **Events (`Event(id:)`)**: Track user interactions. Donate via `event.donate()`. Use `#Rule(event) { $0.donations.count == 0 }` for frequency or completion gating.

## Tip Groups (iOS 18+)

Coordinate multiple tips without cluttering the screen. Store `TipGroup` in `@State`:

```swift
struct OnboardingView: View {
    @State private var tips = TipGroup(.ordered) {
        WelcomeTip()
        SearchTip()
        FilterTip()
    }

    var body: some View {
        VStack {
            TipView(tips.currentTip)
            ContentView()
        }
    }
}
```

## Testing Overrides

Use testing overrides only in debug builds, before calling `Tips.configure()`:

```swift
#if DEBUG
if ProcessInfo.processInfo.arguments.contains("--reset-tips") {
    try? Tips.resetDatastore()
}
if ProcessInfo.processInfo.arguments.contains("--show-all-tips") {
    Tips.showAllTipsForTesting()
}
#endif
try Tips.configure()
```

Launch arguments: `-com.apple.TipKit.ResetDatastore 1`, `-com.apple.TipKit.ShowAllTips 1`.

## Common Mistakes

- **Configuring TipKit from a view**: Calling `Tips.configure()` in `onAppear` races with view layout and can throw datastore errors. Configure in app `init()`.
- **Using tips for critical information**: Tips are dismissible educational hints. Use alerts or inline banners for errors and destructive warnings.
- **Shipping testing overrides to production**: `showAllTipsForTesting()` bypasses display rules. Keep overrides behind `#if DEBUG`.
- **Ungated iOS 18+ APIs**: Always gate `TipGroup`, `.cloudKitContainer`, and `MaxDisplayDuration` with `#available(iOS 18, *)`.
- **Unstable reusable tip IDs**: If dynamic tips do not provide stable `id` properties, TipKit cannot track persistence and invalidation correctly.

## Review Checklist

- [ ] `Tips.configure(_:)` invoked once at app launch before any tip displays
- [ ] iOS 18+ features (`TipGroup`, CloudKit container) guarded with availability checks
- [ ] Tip copy is concise, actionable, and focused on discovery
- [ ] Events donated when user performs the action; tip invalidated upon completion
- [ ] `TipGroup` stored in `@State` when sequencing related tips
- [ ] Testing overrides isolated to debug schemes or UI test arguments

## References

- Rules, events, and placement: [references/rules-events-and-placement.md](references/rules-events-and-placement.md)
- Custom styling, groups, and testing: [references/styles-groups-and-testing.md](references/styles-groups-and-testing.md)
- Actions, onboarding flows, and CloudKit sync: [references/actions-onboarding-and-sync.md](references/actions-onboarding-and-sync.md)
- [Apple TipKit Documentation](https://sosumi.ai/documentation/tipkit)
- [Tips.configure(_:)](https://sosumi.ai/documentation/tipkit/tips/configure(_:))
- [TipGroup](https://sosumi.ai/documentation/tipkit/tipgroup)
- [HIG Offering Help](https://sosumi.ai/design/human-interface-guidelines/offering-help)
- [WWDC24 Customize feature discovery with TipKit](https://sosumi.ai/videos/play/wwdc2024/10070)
