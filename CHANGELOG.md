# Changelog

## Unreleased

### Skills

- Add `core-haptics` for custom waveform composition, engine lifecycle, live parameter modulation, AHAP playback, capability fallback, and physical-device verification.
- Route ordinary SwiftUI and UIKit feedback to system feedback APIs while reserving Core Haptics for custom tactile experiences.

### Quality and maintainability

- Compact the six largest remaining skill entrypoints—ActivityKit, Contacts, CryptoTokenKit, FinanceKit, RelevanceKit, and SharePlay—into progressive-disclosure routing guides.
- Add required Xcode 26.6 and informational Xcode 27 compile lanes for MetricKit, EnergyKit, SwiftData, Swift concurrency, and Core Haptics fixtures.
- Add four local Core Haptics evaluations and one published drag-modulation scenario.

### Distribution

- Isolate Agent Skills discovery checks from ignored maintainer state.
- Validate the exact public skill names and count from a release-faithful repository snapshot.
- Repair stale Sosumi documentation URLs and add a scheduled external-link check.

## 1.2.0 - 2026-08-24

### Quality and maintainability

- Add a real Codex backend, provider/model selection, scenario filtering, and duration capture to the behavioral A/B runner.
- Record blind behavioral comparisons for the `v1.1.0` fixes and the later skill/reference compaction work.
- Compact the 15 largest skill entrypoints into task-routing guides while moving implementation recipes into opt-in references.
- Rewrite the 30 longest discovery descriptions around capability, trigger, and ownership boundaries; verify the catalog with a 19-case routing matrix.
- Split the 10 largest reference files into 31 focused references, preserve every technical section, and correct an overstatement about automatic Swift Charts accessibility.

## 1.1.0 - 2026-08-24

### Skills

- Add `swiftui-responsive-layout` for diagnosing and fixing clipping, overlap, safe-area, keyboard, Dynamic Type, localization, rotation, and iPad window-resizing failures.
- Keep ordinary container selection in `swiftui-layout-components` and route responsive failures through a dedicated boundary.
- Add the adapted `swift-code-review` skill for evidence-backed Swift/SwiftUI diff reviews covering concurrency, ownership, error boundaries, and Observation state.
- Route layout, networking, accessibility, StoreKit, persistence, and other framework-specific findings to the existing specialist skills instead of duplicating their implementation guides.

### Quality

- Add four local eval cases and one published responsive checkout scenario covering keyboard, safe areas, large text, localization, iPad multitasking, state preservation, and sibling routing.
- Add four local review eval cases and one published cross-cutting review scenario covering verification gates, actor/task lifetime, Observation ownership, error boundaries, and specialist routing.
- Add the `@thiennc/ios-skills` npm CLI for version-pinned one-command installation.
- Validate npm metadata, wrapper behavior, package contents, and release version alignment in CI.

## v1.0.0

Initial community release.

### Collection

- Publish 87 Agent Skills for modern Swift and Apple-platform development.
- Add `ios-app-workflow` for complete app and feature delivery from project preflight through Simulator verification.
- Organize skills into focused SwiftUI, Swift core, framework, engineering, hardware, platform, AI/ML, and gaming bundles.
- Keep skills independently installable through the Agent Skills directory format.

### Guidance

- Streamline core Swift, SwiftUI, persistence, accessibility, testing, and Simulator entrypoints around clear scope boundaries.
- Add project-structure and file-naming guidance to `swiftui-patterns`.
- Use progressive disclosure so detailed patterns load only when relevant.
- Standardize local skill eval files on the documented `assertions` field.
- Normalize stable names across all 274 local eval cases.
- Add published end-to-end scenarios for `ios-app-workflow`.

### Quality infrastructure

- Add repository-wide validation for skill metadata, links, references, evals, and distribution bundles.
- Add CI tests and an Agent Skills installation smoke test.
- Add a maintainer audit workflow for focused, collection, and release audits.
- Reduce high-cost discovery descriptions while preserving specialist routing boundaries.
- Refactor `push-notifications` and `storekit` with directly routed progressive-disclosure references and focused routing evaluations.
- Correct APNs Simulator coverage, Notification Service Extension exactly-once fallback, App Review payment boundaries, and StoreKit Test-only API examples against current Apple documentation.
- Split notification and StoreKit references into focused runtime, extension, offer, testing, and recovery guides; retain full recipes as opt-in archives.
- Add a provider-neutral behavioral A/B runner and record model-access blockers instead of treating static validation as output-quality evidence.
- Route each behavioral A/B scenario to its owning skill and keep communication-extension examples behind the exact-once completion wrapper.

### Project identity

- Publish Claude marketplace and Tessl metadata under `ios-skills`.
- Point installation, Discussions, Funding, issue assignment, and contribution links to this repository.
- Preserve the PolyForm Perimeter license and all legally required notices.
