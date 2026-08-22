# Swift iOS Skills Community

[![GitHub stars](https://img.shields.io/github/stars/thiennc-tesoglobal/swift-ios-skills-community)](https://github.com/thiennc-tesoglobal/swift-ios-skills-community)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-87-2ea44f)](skills/)
[![Swift](https://img.shields.io/badge/Swift-6.3-F05138?logo=swift&logoColor=white)](https://swift.org)
[![Apple platforms](https://img.shields.io/badge/Apple%20Platforms-iOS%20%7C%20iPadOS%20%7C%20macOS-black?logo=apple)](https://developer.apple.com)
[![Specification](https://img.shields.io/badge/Agent%20Skills-compatible-6f42c1)](https://agentskills.io)
[![License](https://img.shields.io/badge/License-PolyForm%20Perimeter-blue)](LICENSE)
[![Validation](https://github.com/thiennc-tesoglobal/swift-ios-skills-community/actions/workflows/validate-repository.yml/badge.svg)](https://github.com/thiennc-tesoglobal/swift-ios-skills-community/actions/workflows/validate-repository.yml)

A practical Agent Skills toolkit for building complete Swift and Apple-platform applications with coding agents.

The repository contains **87 focused skills** covering Swift, SwiftUI, app architecture, Apple frameworks, testing, performance, accessibility, security, App Store delivery, and Simulator verification.

> **Tiếng Việt:** Đây là bộ kỹ năng dành cho AI coding agent phát triển ứng dụng Swift và SwiftUI theo quy trình thực tế: hiểu dự án, chọn đúng chuyên môn, tổ chức source code, triển khai tính năng, build, test và kiểm tra trên Simulator.

## What this project is

Swift iOS Skills Community is a reusable knowledge and delivery layer for AI coding agents. It is not an app template, a framework dependency, or a collection of copy-paste prompts.

Each skill gives an agent focused instructions for one engineering area. The central [`ios-app-workflow`](skills/ios-app-workflow/) skill coordinates those specialists when a request spans an entire app or a substantial feature.

The goal is simple: help agents move from a product request to a maintainable, verified implementation instead of stopping after generating an isolated code sample.

## Development direction

| Principle | Direction |
|---|---|
| Complete delivery | Cover the path from project discovery and architecture to implementation, tests, Simulator validation, and release readiness. |
| Focused context | Load only the skills relevant to the current task instead of overwhelming the agent with the entire collection. |
| Maintainable source | Encourage domain-based names, clear file boundaries, predictable state ownership, and architecture appropriate to the project size. |
| Evidence over assumption | Require real build, test, runtime, accessibility, and persistence checks whenever the environment supports them. |
| Modern Apple development | Track current Swift, SwiftUI, Xcode, SDK, concurrency, privacy, and platform conventions while respecting deployment targets. |
| Community quality | Keep skills independently useful, reviewable, testable, and easy to improve through issues and pull requests. |

Near-term development focuses on strengthening the end-to-end workflow, improving the core SwiftUI and Swift engineering skills, expanding real-world evaluations, and keeping framework guidance aligned with current Apple platforms.

## How the collection works

For a complete app or a multi-file feature, start with `ios-app-workflow`. It performs project preflight, identifies the smallest set of specialist skills, guides implementation, and defines the evidence needed before the work is considered complete.

```text
Product request
    ↓
ios-app-workflow
    ↓
Relevant specialist skills only
    ↓
Implementation in maintainable vertical slices
    ↓
Build → Test → Simulator verification
```

For a narrow task, use the matching specialist directly. Examples:

- `swift-concurrency` for actor isolation, `Sendable`, and async code
- `swiftdata` for models, queries, relationships, and migrations
- `swiftui-animation` for transitions, springs, and Reduce Motion behavior
- `ios-accessibility` for VoiceOver, Dynamic Type, and accessible interactions
- `storekit` for purchases and subscriptions
- `ios-simulator` for building, installing, launching, and verifying an app

## Quick start

### Install with the Agent Skills CLI

Choose skills interactively:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community
```

Install the complete collection when you genuinely need broad framework coverage:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community --all
```

For most projects, prefer interactive selection or a focused bundle. Smaller installations give agents a cheaper, more precise discovery surface.

Install only the end-to-end workflow:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community \
  --skill ios-app-workflow
```

Install a practical SwiftUI app set:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community \
  --skill ios-app-workflow \
  --skill swiftui-patterns \
  --skill swiftui-layout-components \
  --skill swiftui-navigation \
  --skill swiftui-animation \
  --skill swiftdata \
  --skill ios-accessibility \
  --skill swift-testing \
  --skill ios-simulator
```

The repository follows the open [Agent Skills specification](https://agentskills.io) and can be used by tools that support the same skill-directory format, including [Codex](https://learn.chatgpt.com/docs/build-skills) and other compatible coding agents.

### Install as a Claude Code plugin

Add the marketplace:

```sh
/plugin marketplace add thiennc-tesoglobal/swift-ios-skills-community
```

Install all skills:

```sh
/plugin install all-ios-skills@swift-ios-skills-community
```

Or install a focused bundle:

```sh
/plugin install swiftui-skills@swift-ios-skills-community
/plugin install swift-core-skills@swift-ios-skills-community
/plugin install ios-engineering-skills@swift-ios-skills-community
```

### Manual installation

Download or clone the repository, then copy the required folders from [`skills/`](skills/) into the skills directory supported by your agent. Keep each skill folder intact so its `SKILL.md`, references, scripts, and evaluations remain together.

## Recommended usage

Ask the agent to use a skill explicitly when you want deterministic routing.

Build a complete app:

```text
Use $ios-app-workflow to build a polished SwiftUI todo app with SwiftData,
accessible interactions, smooth reduced-motion-aware animations, tests,
and verified Simulator behavior.
```

Handle one focused problem:

```text
Use $swift-concurrency to review this view model for isolation and Sendable issues.
```

Review release readiness:

```text
Use $app-store-review and $ios-accessibility to audit this app before submission.
```

Installing all skills does not mean every skill should be loaded for every request. The collection is designed for selective routing: one workflow skill plus only the specialists required by the actual task.

## Skill bundles

| Bundle | Skills | Coverage |
|---|---:|---|
| `all-ios-skills` | 87 | Complete collection |
| `swiftui-skills` | 10 | SwiftUI patterns, layout, navigation, gestures, animation, performance, Liquid Glass, UIKit, and WebKit interop |
| `swift-core-skills` | 10 | Swift language, architecture, concurrency, data, testing, Codable, Charts, formatting, and API design |
| `ios-app-framework-skills` | 15 | Widgets, Live Activities, StoreKit, App Intents, notifications, maps, media, PDFs, and CarPlay |
| `ios-data-framework-skills` | 8 | CloudKit, HealthKit, EventKit, Contacts, MusicKit, PassKit, WeatherKit, and FinanceKit |
| `ios-ai-ml-skills` | 5 | Foundation Models, Core ML, Vision, Natural Language, and speech recognition |
| `ios-engineering-skills` | 17 | App workflow, networking, accessibility, security, diagnostics, Simulator, linting, and App Store readiness |
| `ios-hardware-skills` | 8 | Bluetooth, NFC, motion, PencilKit, RealityKit, accessories, and sensors |
| `ios-platform-skills` | 10 | HomeKit, SharePlay, CallKit, and specialized Apple-platform integrations |
| `ios-gaming-skills` | 4 | GameKit, SpriteKit, SceneKit, and TabletopKit |
| `apple-kit-skills` | 39 | Framework-focused Apple Kit subset |

Browse the complete catalog in [`skills/`](skills/).

## Repository structure

```text
swift-ios-skills-community/
├── skills/
│   ├── ios-app-workflow/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── swiftui-patterns/
│   ├── swift-concurrency/
│   ├── swiftdata/
│   └── ...
├── evals/
├── tests/
├── .claude-plugin/
├── .tessl-plugin/
└── tessl.json
```

A skill may contain:

- `SKILL.md` — concise routing and implementation guidance loaded by the agent
- `references/` — detailed material loaded only when relevant
- `scripts/` — reusable diagnostics or automation where appropriate

Repository-level cases in `evals/` contain scenarios and assertions that protect expected agent behavior.

## Quality standard

Changes should preserve:

- valid skill names and frontmatter
- clear trigger and boundary descriptions
- concise primary instructions with progressive disclosure
- accurate deployment-target and framework guidance
- valid local references and plugin metadata
- meaningful evaluation assertions for behavior changes
- compatibility of the complete 87-skill bundle

Pull requests run structural validation, repository tests, and an Agent Skills discovery smoke test. Run the same checks locally with:

```sh
python3 .github/scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

## Updating installed skills

For installations managed by the Agent Skills CLI:

```sh
npx skills update
```

For Claude Code, update the marketplace and reinstall the selected bundle when a new version is released.

Notable project changes are documented in [`CHANGELOG.md`](CHANGELOG.md).

## Contributing

Issues and pull requests are welcome. A useful contribution should solve a concrete agent behavior problem and remain focused enough to review and evaluate.

When contributing:

1. Keep each skill independently usable.
2. Define when the skill should and should not be selected.
3. Prefer primary Apple and Swift documentation for technical claims.
4. Move conditional or lengthy guidance into focused references.
5. Add or update evaluation assertions when behavior changes.
6. Avoid unrelated rewrites in the same pull request.

Use [Issues](https://github.com/thiennc-tesoglobal/swift-ios-skills-community/issues) for bugs and proposals, or [Discussions](https://github.com/thiennc-tesoglobal/swift-ios-skills-community/discussions) for broader ideas and roadmap conversations.

## License

This is a source-available community project distributed under the [PolyForm Perimeter License 1.0.0](LICENSE). The license includes a noncompete restriction, so review its terms before redistributing the collection or offering a competing product.

Apple frameworks, APIs, documentation, session content, and trademarks belong to Apple Inc. This project is independent and is not affiliated with, endorsed by, or sponsored by Apple.
