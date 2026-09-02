# Swift iOS Skills Community

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-90-2ea44f)](skills/)
[![Swift](https://img.shields.io/badge/Swift-6.3-F05138?logo=swift&logoColor=white)](https://swift.org)
[![Validation](https://github.com/thiennc-tesoglobal/ios-skills/actions/workflows/validate-repository.yml/badge.svg)](https://github.com/thiennc-tesoglobal/ios-skills/actions/workflows/validate-repository.yml)
[![License](https://img.shields.io/badge/License-PolyForm%20Perimeter-blue)](LICENSE)

**90 focused Agent Skills for modern Swift and Apple-platform development.**

The collection gives coding agents practical guidance for architecture,
implementation, testing, performance, accessibility, security, Apple frameworks,
and App Store delivery. It is a knowledge layer, not an app template or runtime
dependency.

## Core principles

- Use one workflow skill and only the specialists required by the task.
- Prefer current Swift, SwiftUI, concurrency, and Apple framework APIs.
- Verify work with builds, tests, Simulator runs, and physical devices when hardware matters.
- Keep each skill focused, self-contained, and progressively disclosed through references.

For a complete app or substantial feature, start with
[`ios-app-workflow`](skills/ios-app-workflow/). For a narrow task, load the matching
specialist directly.

```text
Request → ios-app-workflow → focused skills → implementation → verification
```

## Install

Interactive installer:

```sh
npx @thiennc/ios-skills
```

Install one skill or the complete collection:

```sh
npx @thiennc/ios-skills --skill ios-app-workflow
npx @thiennc/ios-skills --all
```

Direct GitHub installation:

```sh
npx skills add thiennc-tesoglobal/ios-skills
```

### Claude Code

```sh
/plugin marketplace add thiennc-tesoglobal/ios-skills
/plugin install all-ios-skills@ios-skills
```

Focused bundles include `swiftui-skills`, `swift-core-skills`,
`ios-engineering-skills`, and framework-specific collections.

## Use

Name the skill explicitly when routing needs to be deterministic:

```text
Use $ios-app-workflow to build a SwiftUI feature with SwiftData,
accessibility, tests, and verified Simulator behavior.
```

Common specialists:

- [`swift-concurrency`](skills/swift-concurrency/) — isolation, `Sendable`, tasks, and async code
- [`swiftdata`](skills/swiftdata/) — models, queries, relationships, and migrations
- [`swiftui-patterns`](skills/swiftui-patterns/) — state, composition, and project structure
- [`swiftui-responsive-layout`](skills/swiftui-responsive-layout/) — adaptive layout failures
- [`swift-code-review`](skills/swift-code-review/) — evidence-backed Swift review
- [`ios-simulator`](skills/ios-simulator/) — build, launch, and runtime verification
- [`core-haptics`](skills/core-haptics/) — custom tactile patterns and AHAP playback

Browse the complete catalog in [`skills/`](skills/). Installing all skills does not
mean every skill should be loaded for every task.

## Coverage

The collection covers:

- Swift language, concurrency, architecture, testing, SwiftData, and Core Data
- SwiftUI layout, navigation, animation, performance, accessibility, and UIKit interop
- Apple app, data, hardware, media, AI/ML, gaming, and platform frameworks
- Networking, security, diagnostics, localization, App Review, and delivery workflows

Current inventory: **90 skills**, **288 local evaluation cases**, and
**268 published evaluation scenarios**.

## Quality

Pull requests validate metadata, references, evaluations, bundle membership, public
discovery, tests, and SDK-sensitive compile fixtures.

```sh
python3 .github/scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npm test
npm run pack:check
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for authoring rules and
[`CHANGELOG.md`](CHANGELOG.md) for notable changes.

## License

The project uses the [PolyForm Perimeter License 1.0.0](LICENSE). The adapted
[`swift-code-review`](skills/swift-code-review/) skill keeps its upstream Apache-2.0
attribution. Apple frameworks, documentation, and trademarks belong to Apple Inc.
This project is independent and not endorsed by Apple.
