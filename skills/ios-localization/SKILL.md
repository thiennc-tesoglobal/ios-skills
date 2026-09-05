---
name: ios-localization
description: "Implement or review Apple-platform localization with String Catalogs, generated symbols, plurals, locale-aware formatting, package resources, and right-to-left layout. Use for multi-language UI, translation keys, localized values, or localization testing."
---

# iOS Localization & Internationalization

Localize Apple-platform applications using String Catalogs (`.xcstrings`), compiler-generated symbols, locale-aware `FormatStyle`, and right-to-left (RTL) layout adaptation. Targets Swift 6.3 / iOS 26+.

## Contents

- [String Catalogs (.xcstrings)](#string-catalogs-xcstrings)
- [String Types: Key vs Resource](#string-types-key-vs-resource)
- [Pluralization & Variations](#pluralization--variations)
- [FormatStyle & Locales](#formatstyle--locales)
- [Right-to-Left (RTL) Layout](#right-to-left-rtl-layout)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## String Catalogs (.xcstrings)

String Catalogs are the standard format for Xcode localization. Xcode automatically extracts localizable strings from source code on every build:

```swift
// Automatically extracted as LocalizedStringKey in SwiftUI
Text("Welcome back")
Button("Save Changes") { }
Label("Account Settings", systemImage: "person.crop.circle")
```

For non-view code, use generated symbols or `String(localized:)`:

```swift
// Modern type-safe localized string
let message = String(localized: "order_confirmation_title", defaultValue: "Order Confirmed")
```

## String Types: Key vs Resource

- **`LocalizedStringKey`**: Used across SwiftUI views (`Text`, `Button`). Evaluated lazily at view render time.
- **`LocalizedStringResource`**: Decoupled from SwiftUI. Ideal for passing localized strings across view models, models, or App Intents.
- **`String(localized:)`**: Immediately materializes the localized `String` using the current locale.

## Pluralization & Variations

String Catalogs support Unicode plural rules (`zero`, `one`, `two`, `few`, `many`, `other`) and device-specific variations (iPhone, iPad, Mac) in the visual catalog editor without complex `.stringsdict` files:

```swift
// Single integer interpolation triggers plural variant support in String Catalogs
Text("\(unreadCount) unread messages")
```

## FormatStyle & Locales

Never format currency, numbers, or dates with manual string concatenation. Always use `FormatStyle`:

```swift
// Currency formatting adhering to user locale
let priceString = amount.formatted(.currency(code: "USD"))

// Date and relative time formatting
let dateString = eventDate.formatted(date: .abbreviated, time: .shortened)
let relativeString = eventDate.formatted(.relative(presentation: .named))
```

## Right-to-Left (RTL) Layout

- Use leading/trailing layout constraints rather than absolute left/right.
- Directional SF Symbols mirror automatically; set `.imageScale` or disable mirroring only when representing physical hardware orientation.

## Common Mistakes

- **String concatenation for localized sentences**: Concatenating strings breaks syntax across languages. Use format specifiers with positional arguments (`%1$@`).
- **Hardcoding date or number formatting**: Manual decimal or comma placement breaks in non-US locales. Use `FormatStyle`.
- **Using left/right alignment**: Hardcoded left/right alignments do not flip in Arabic/Hebrew RTL layouts. Use `leading`/`trailing`.
- **Eager localization in static constants**: Initializing `String(localized:)` in static properties pins the language at launch, failing when the user switches language dynamically.
- **Ignoring pluralization variations**: Hardcoding `s` for counts fails across languages with complex plural rules (e.g. Russian, Arabic).

## Review Checklist

- [ ] String Catalogs (`.xcstrings`) used for all new string localization
- [ ] `LocalizedStringResource` used when passing localized strings from model layers
- [ ] Numeric, date, and currency values formatted via Foundation `FormatStyle`
- [ ] Layout constraints and padding use `leading` and `trailing`
- [ ] Inflection and plural rules configured in String Catalogs

## References

- FormatStyle patterns: [references/formatstyle-locale.md](references/formatstyle-locale.md)
- String Catalogs guide: [references/string-catalogs.md](references/string-catalogs.md)
