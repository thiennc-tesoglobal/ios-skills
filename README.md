# Swift iOS Skills Community

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-89-2ea44f)](skills/)
[![Swift](https://img.shields.io/badge/Swift-6.3-F05138?logo=swift&logoColor=white)](https://swift.org)
[![Apple platforms](https://img.shields.io/badge/Apple%20Platforms-iOS%20%7C%20iPadOS%20%7C%20macOS-black?logo=apple)](https://developer.apple.com)
[![Validation](https://github.com/thiennc-tesoglobal/ios-skills/actions/workflows/validate-repository.yml/badge.svg)](https://github.com/thiennc-tesoglobal/ios-skills/actions/workflows/validate-repository.yml)
[![License](https://img.shields.io/badge/License-PolyForm%20Perimeter-blue)](LICENSE)

A practical collection of **89 Agent Skills** for building complete Swift and Apple-platform applications with AI coding agents.

The collection helps an agent choose the right specialist guidance, organize maintainable source code, implement features, and verify the result with builds, tests, and Simulator evidence. It is a knowledge and delivery layer—not an app template or framework dependency.

> **Tiếng Việt:** Bộ skill giúp AI coding agent phát triển ứng dụng Swift và SwiftUI theo quy trình thực tế, từ tổ chức source code đến build, test và kiểm tra trên Simulator.

## Why this collection

- **Complete delivery:** architecture, implementation, testing, performance, accessibility, security, and App Store readiness.
- **Focused context:** load one workflow skill and only the specialists required by the task.
- **Modern Apple development:** current Swift, SwiftUI, concurrency, privacy, SDK, and deployment-target guidance.
- **Evidence-based results:** prefer real build, test, runtime, and Simulator verification over assumptions.

For an entire app or substantial multi-file feature, start with [`ios-app-workflow`](skills/ios-app-workflow/). For a narrow task, select the matching specialist directly.

```text
Product request → ios-app-workflow → relevant specialists → implementation → verification
```

## Install

### Codex and Agent Skills-compatible tools

Choose skills interactively:

```sh
npx @thiennc/ios-skills
```

Install the end-to-end workflow:

```sh
npx @thiennc/ios-skills --skill ios-app-workflow
```

Install the complete collection only when broad framework coverage is required:

```sh
npx @thiennc/ios-skills --all
```

The direct GitHub installer remains available as a fallback:

```sh
npx skills add thiennc-tesoglobal/ios-skills
```

Smaller installations provide agents with a cheaper and more precise discovery surface. The repository follows the open [Agent Skills specification](https://agentskills.io).

### Claude Code

Add the marketplace and install a bundle:

```sh
/plugin marketplace add thiennc-tesoglobal/ios-skills
/plugin install all-ios-skills@ios-skills
```

Focused bundles are also available:

```sh
/plugin install swiftui-skills@ios-skills
/plugin install swift-core-skills@ios-skills
/plugin install ios-engineering-skills@ios-skills
```

### Manual installation

Clone the repository and copy the required folders from [`skills/`](skills/) into the skills directory supported by your agent. Keep each folder intact so its instructions, references, scripts, and evaluations remain together.

## Use

Ask the agent to use a skill explicitly when deterministic routing matters:

```text
Use $ios-app-workflow to build a polished SwiftUI todo app with SwiftData,
accessible interactions, tests, and verified Simulator behavior.
```

Examples of focused routing:

- `swift-concurrency` — actor isolation, `Sendable`, and async code
- `swiftdata` — models, queries, relationships, and migrations
- `swiftui-animation` — transitions, springs, and Reduce Motion behavior
- `swiftui-responsive-layout` — clipping, overlap, safe areas, keyboard, and cross-size adaptation
- `swift-code-review` — evidence-backed Swift/SwiftUI diff review with concurrency, ownership, errors, and state checks
- `ios-accessibility` — VoiceOver, Dynamic Type, and accessible interactions
- `storekit` — purchases and subscriptions
- `ios-simulator` — build, install, launch, and runtime verification

Installing every skill does not mean every skill should be loaded for every request.

## Bundles

| Bundle | Skills | Coverage |
|---|---:|---|
| `all-ios-skills` | 89 | Complete collection |
| `swiftui-skills` | 11 | SwiftUI UI, responsive layout, navigation, animation, performance, and interop |
| `swift-core-skills` | 10 | Swift language, architecture, concurrency, data, and testing |
| `ios-app-framework-skills` | 15 | Widgets, StoreKit, App Intents, maps, media, PDFs, and CarPlay |
| `ios-data-framework-skills` | 8 | CloudKit, HealthKit, EventKit, Contacts, Wallet, and weather |
| `ios-ai-ml-skills` | 5 | Foundation Models, Core ML, Vision, language, and speech |
| `ios-engineering-skills` | 18 | Delivery, code review, networking, accessibility, security, diagnostics, and App Store readiness |
| `ios-hardware-skills` | 8 | Bluetooth, NFC, motion, PencilKit, RealityKit, and accessories |
| `ios-platform-skills` | 10 | HomeKit, SharePlay, CallKit, and specialized integrations |
| `ios-gaming-skills` | 4 | GameKit, SpriteKit, SceneKit, and TabletopKit |
| `apple-kit-skills` | 39 | Framework-focused Apple Kit subset |

Browse the full catalog in [`skills/`](skills/).

## Repository layout

```text
ios-skills/
├── skills/          # Skill instructions, references, scripts, and local evals
├── evals/           # Published behavior scenarios and assertions
├── tests/           # Repository and diagnostic-helper tests
├── .claude-plugin/  # Claude Code marketplace bundles
├── .tessl-plugin/   # Tessl package metadata
└── tessl.json
```

## Quality

Pull requests validate skill metadata, references, evaluation coverage, plugin bundles, repository tests, and clean Agent Skills discovery.

```sh
python3 .github/scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npm ci
npm test
npm run pack:check
npx --yes skills@1.5.23 add . --list
```

The complete collection currently includes **89 skills**, **284 local evaluation cases**, and **267 published evaluation scenarios**. See [`CHANGELOG.md`](CHANGELOG.md) for notable changes.

## Contributing

Issues and pull requests are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for skill structure, evaluation requirements, local checks, and the pull-request checklist.

Use [Issues](https://github.com/thiennc-tesoglobal/ios-skills/issues) for bugs and focused proposals, or [Discussions](https://github.com/thiennc-tesoglobal/ios-skills/discussions) for broader ideas.

## License

This source-available project is distributed under the [PolyForm Perimeter License 1.0.0](LICENSE), which includes a noncompete restriction. Review its terms before redistribution or offering a competing product.

The adapted [`swift-code-review`](skills/swift-code-review/) skill is distributed
under Apache-2.0 with its upstream attribution and license files; the repository
license applies to the remaining collection.

Apple frameworks, APIs, documentation, session content, and trademarks belong to Apple Inc. This independent project is not affiliated with, endorsed by, or sponsored by Apple.
