# iOS Delivery Checklist

Load only the section matching the current task. This checklist supplies proof criteria; it does not expand user authorization.

## New App

- Confirm product name, supported Apple platforms, deployment target, orientation/device families, and persistence choice.
- Establish an app entry point named for the product and a discoverable feature-first source structure.
- Implement one complete user flow before decorative secondary surfaces.
- Provide useful empty/loading/error states and deterministic starter/preview data only when appropriate.
- Verify a clean build, first launch, relaunch persistence, core interactions, appearance, Dynamic Type, and Reduce Motion.

## New Feature

- Identify feature entry point, owner, dependencies, routes, stored data, and public integration boundary.
- Match the existing architecture and naming unless observed complexity justifies a scoped change.
- Test the feature's domain behavior and failure/cancellation paths.
- Verify integration from the real parent flow rather than only an isolated preview.

## Structure-Only Refactor

- Pin layout, navigation, identity, state ownership, accessibility, side effects, timing, and persistence before moving code.
- Extract one meaningful boundary at a time; filenames should match primary types.
- Build after compiler-visible or ownership changes.
- Compare the same preview/simulator fixture before and after.
- Treat any visual or behavior change as a regression unless explicitly requested.

## Visual Polish

- Confirm the visual request permits design changes.
- Preserve task completion clarity, readable contrast, Dynamic Type, and reduced-motion alternatives.
- Prefer system semantics and materials; do not raise deployment target merely for an effect.
- Capture the same representative states in light/dark mode and relevant text sizes.

## Persistence Change

- Inventory current schema and real store configuration.
- Define save timing, errors, relationships, delete rules, and migration expectations.
- Test from the previous schema with representative data.
- Verify create/update/delete and relaunch behavior.
- Never reset a user store without explicit authorization.

## Release-Oriented Work

- Build the intended configuration and inspect warnings.
- Confirm signing/capability changes are in scope before making them.
- Run relevant tests and accessibility checks.
- Separate Simulator evidence from required real-device checks.
- Route App Store policy and privacy-manifest review to `app-store-review`.
