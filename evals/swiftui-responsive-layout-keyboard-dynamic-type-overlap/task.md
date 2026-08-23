# Repair a Responsive Checkout Layout

## Problem/Feature Description

An iOS 26 SwiftUI checkout screen is embedded in a `NavigationStack` and contains a long `ScrollView` form. A persistent checkout bar is attached with a bottom `overlay`. The last fields sit underneath the bar, the focused promo-code field becomes obstructed when the software keyboard appears, and the price label collides with the action button at accessibility Dynamic Type sizes. The current implementation also applies `ignoresSafeArea()` to the root screen and uses a fixed height for the checkout bar.

Produce a focused diagnosis and implementation recommendation. Preserve the existing navigation, state model, validation logic, and visual hierarchy.

## Output Specification

Create `responsive-checkout-review.md` containing:

- the root causes of the overlap and keyboard failures
- a compact SwiftUI code sketch for the corrected scroll and persistent-action structure
- the adaptation approach for large text and long localized labels
- safe-area boundaries for background versus interactive content
- a verification matrix covering the original failure and nearby configurations

Do not redesign the feature architecture, navigation routes, validation rules, or animation system.
