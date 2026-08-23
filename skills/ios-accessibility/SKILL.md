---
name: ios-accessibility
description: "Implement or audit accessibility for SwiftUI, UIKit, and AppKit, including VoiceOver, Dynamic Type, focus, actions, traversal, contrast, motion preferences, keyboard access, and accessibility testing. Use when accessibility behavior or compliance evidence is in scope."
---

# Apple Platform Accessibility

Make essential content and actions perceivable, operable, understandable, and testable across supported assistive technologies.

## Scope and Compatibility

This skill owns semantic labels/values/traits, grouping and traversal, custom actions, focus, Dynamic Type, contrast, motion/transparency preferences, Voice Control, keyboard access, and accessibility verification. Route visual layout implementation to the relevant UI skill and App Store declaration policy to `app-store-review` when submission readiness is the main request.

Inspect deployment target, platform, UI framework, and supported device classes before selecting APIs. Preserve existing interaction behavior unless remediation requires a change, and verify versioned APIs in SDK headers or primary Apple documentation.

## Audit Workflow

1. Identify the screen's essential information, primary actions, state changes, errors, and time-sensitive content.
2. Inspect semantic output rather than inferring accessibility from visual appearance.
3. Test navigation order, labels, values, traits, actions, focus, text scaling, contrast, Reduce Motion, Reduce Transparency, and keyboard/Voice Control paths that apply.
4. Fix the narrowest semantic or layout boundary while preserving ordinary interaction.
5. Re-run automated checks and manually exercise the affected assistive-technology path.

Read [Accessibility Patterns](references/a11y-patterns.md) for SwiftUI/UIKit/AppKit recipes, focus management, rotors, and XCTest examples.

## Semantic Rules

- Prefer native controls because they provide semantics and interaction behavior together.
- Give every essential control an understandable accessible name; avoid labels that merely repeat the control type.
- Expose changing state through value or traits, not only color or animation.
- Combine children only when the combined element remains understandable and actionable.
- Hide decorative content, but never hide information needed to understand state or complete a task.
- Add named accessibility actions when a gesture or context menu is otherwise undiscoverable.
- Announce important asynchronous outcomes without flooding the user with routine updates.
- Keep focus order aligned with reading and task order; restore focus after modal or destructive transitions when needed.

## Layout and Preferences

Support accessibility text sizes without clipping essential content or forcing a fixed horizontal layout. Let controls grow, wrap, or change axis where necessary. Minimum target size is a usability floor, not a substitute for spacing and clear labels.

Respect system preferences including Reduce Motion, Reduce Transparency, Differentiate Without Color, Increased Contrast, and Button Shapes when the UI depends on those channels. Route animation alternatives to `swiftui-animation`, ordinary container construction to `swiftui-layout-components`, and cross-size clipping or reflow fixes to `swiftui-responsive-layout`.

Media work should read [Media Accessibility](references/media-accessibility.md) for captions, audio descriptions, and playback controls.

## Verification

Automated accessibility audits and identifier-based UI tests catch regressions but do not prove usability. Manually test the core task with VoiceOver and the relevant input methods. Use Accessibility Inspector to inspect element hierarchy, names, values, actions, and contrast.

Do not claim App Store accessibility support from implementation alone. Read [Accessibility Nutrition Labels](references/nutrition-labels.md), gather test evidence, and scope declarations to the platforms and features actually verified.

## Review Checklist

- [ ] Essential controls have clear labels, values, traits, and hints where needed
- [ ] Meaning is not conveyed by color, shape, position, or motion alone
- [ ] Reading and focus order follows the task
- [ ] Custom gestures have accessible alternatives
- [ ] Dynamic Type works at accessibility sizes without losing essential content
- [ ] Motion/transparency/contrast preferences have appropriate behavior
- [ ] Errors and important completion states are exposed and announced appropriately
- [ ] Keyboard, Voice Control, Switch Control, or Full Keyboard Access paths are tested when in scope
- [ ] Automated audits pass and the primary flow is manually verified
- [ ] Store declarations are backed by current evidence

## References

- [Implementation, focus, rotors, and testing patterns](references/a11y-patterns.md)
- [Media accessibility](references/media-accessibility.md)
- [App Store Accessibility Nutrition Labels](references/nutrition-labels.md)
