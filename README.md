# Swift iOS Skills Community

[![GitHub stars](https://img.shields.io/github/stars/thiennc-tesoglobal/swift-ios-skills-community)](https://github.com/thiennc-tesoglobal/swift-ios-skills-community)
[![Skills](https://img.shields.io/badge/Agent%20Skills-87-2ea44f)](skills/)
[![Swift](https://img.shields.io/badge/Swift-6.3-F05138?logo=swift&logoColor=white)](https://swift.org)
[![Platform](https://img.shields.io/badge/Apple%20Platforms-iOS%20%7C%20iPadOS%20%7C%20macOS-black?logo=apple)](https://developer.apple.com)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-6f42c1)](https://agentskills.io)
[![License](https://img.shields.io/badge/License-PolyForm%20Perimeter-blue)](LICENSE)

A practical collection of **87 Agent Skills** for building modern Swift and Apple-platform apps with Codex, Claude Code, Cursor, GitHub Copilot, and other Agent Skills-compatible tools.

Maintained by [Thien Ngo](https://github.com/thiennc-tesoglobal). This is a community fork of [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills), customized around concise instructions, progressive disclosure, project structure, and complete build-to-Simulator delivery.

> **Tiếng Việt:** Đây là bộ skill iOS community do Thien Ngo duy trì, hướng đến việc giúp AI agent làm app SwiftUI thực tế: biết tổ chức source code, chọn đúng skill chuyên môn, build, test và kiểm tra trên Simulator thay vì chỉ sinh một đoạn code rời rạc.

## What this version is

This repository keeps the broad Apple-framework coverage of the upstream project and adds a more opinionated delivery layer for real projects.

| Focus | This community version |
|---|---|
| End-to-end delivery | Adds `ios-app-workflow` to coordinate project preflight, implementation, persistence, accessibility, testing, and Simulator verification. |
| Context efficiency | Core skill entrypoints are shorter and route detailed material to focused references. |
| Project organization | Adds concrete SwiftUI folder, filename, composition-root, and refactor guidance. |
| Skill boundaries | Encourages loading only the specialist skills needed for the current task. |
| Evaluation | Uses the Agent Skills `assertions` format consistently across all 87 local eval files. |
| Compatibility | Preserves the open Agent Skills directory format and Claude Code plugin bundles. |

This is an independently maintained community fork, not an official Apple project and not an official release from the upstream maintainer.

## Quick install

### Any supported agent

Interactive selection:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community
```

Install all 87 skills:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community --all
```

Install only the end-to-end workflow:

```sh
npx skills add thiennc-tesoglobal/swift-ios-skills-community --skill ios-app-workflow
```

Recommended set for building a complete SwiftUI app:

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

### OpenAI Codex

Install one skill directly:

```sh
$skill-installer install https://github.com/thiennc-tesoglobal/swift-ios-skills-community/tree/main/skills/<skill-name>
```

Example:

```sh
$skill-installer install https://github.com/thiennc-tesoglobal/swift-ios-skills-community/tree/main/skills/ios-app-workflow
```

### Claude Code plugin

Add this repository as a marketplace:

```sh
/plugin marketplace add thiennc-tesoglobal/swift-ios-skills-community
```

Install everything:

```sh
/plugin install all-ios-skills@swift-ios-skills-community
```

Or install a smaller bundle:

```sh
/plugin install swiftui-skills@swift-ios-skills-community
/plugin install swift-core-skills@swift-ios-skills-community
/plugin install ios-engineering-skills@swift-ios-skills-community
```

### Claude Desktop and ChatGPT

1. Download the desired folder from [`skills/`](skills/).
2. Zip that individual skill folder.
3. Open the product's Skills settings and upload the zip.

## Start with `ios-app-workflow`

`ios-app-workflow` is the main addition in this fork. Use it when the request spans multiple parts of an app rather than one isolated API question.

It coordinates:

- project, target, deployment, architecture, and Git preflight
- source structure and domain-based file naming
- focused SwiftUI, persistence, accessibility, concurrency, and testing skills
- build and test verification
- explicit Simulator selection, launch, interaction, screenshots, and persistence checks
- behavior-preserving multi-file refactors

Example prompt:

```text
Use $ios-app-workflow to build a polished SwiftUI todo app with SwiftData,
accessible interactions, smooth reduced-motion-aware animations, tests,
and verified Simulator behavior.
```

For a narrow problem, use only the matching specialist skill—for example `swift-concurrency` for an isolation diagnostic or `swiftdata` for a migration issue.

## Skill bundles

| Bundle | Skills | Main coverage |
|---|---:|---|
| `all-ios-skills` | 87 | Complete collection |
| `swiftui-skills` | 10 | Views, layout, navigation, gestures, animation, Liquid Glass, performance, UIKit/WebKit interop |
| `swift-core-skills` | 10 | Swift language, architecture, concurrency, data, testing, Codable, charts, formatting, API design |
| `ios-app-framework-skills` | 15 | Widgets, Live Activities, StoreKit, App Intents, notifications, maps, media, CarPlay |
| `ios-data-framework-skills` | 8 | CloudKit, HealthKit, EventKit, Contacts, MusicKit, PassKit, WeatherKit, FinanceKit |
| `ios-ai-ml-skills` | 5 | Foundation Models, Core ML, Vision, Natural Language, speech recognition |
| `ios-engineering-skills` | 17 | App workflow, networking, accessibility, security, diagnostics, Simulator, App Store readiness |
| `ios-hardware-skills` | 8 | Bluetooth, NFC, motion, PencilKit, RealityKit, accessories and sensors |
| `ios-platform-skills` | 10 | HomeKit, SharePlay, CallKit and specialized Apple integrations |
| `ios-gaming-skills` | 4 | GameKit, SpriteKit, SceneKit and TabletopKit |
| `apple-kit-skills` | 39 | Apple Kit framework-focused subset |

Browse every skill in [`skills/`](skills/). Each folder contains its own `SKILL.md`, optional references, and local evaluation cases.

## Repository structure

```text
skills/
  ios-app-workflow/
    SKILL.md
    references/
    evals/
  swiftui-patterns/
  swift-concurrency/
  swiftdata/
  ...

.claude-plugin/
  marketplace.json

evals/
tests/
```

The skills follow the [Agent Skills specification](https://agentskills.io). Main entrypoints stay focused; detailed API patterns and edge cases are loaded from references only when relevant.

## Quality checks

Changes to this fork are checked for:

- valid Agent Skills frontmatter and folder naming
- valid plugin and evaluation JSON
- complete `all-ios-skills` bundle registration
- valid local Markdown references
- repository helper tests
- concise `SKILL.md` entrypoints with progressively disclosed references
- preserved Sosumi links for Apple documentation that agents can read

See [CHANGELOG.md](CHANGELOG.md) for notable changes.

## Update

If installed with the skills CLI:

```sh
npx skills update
```

For Claude Code bundles, update the marketplace and reinstall the bundle when a new release is published.

## Contributing

Issues and pull requests are welcome at [thiennc-tesoglobal/swift-ios-skills-community](https://github.com/thiennc-tesoglobal/swift-ios-skills-community).

When contributing:

- keep each skill independently usable
- preserve deployment-target and toolchain accuracy
- prefer official Apple/Swift sources and readable Sosumi links
- keep the main `SKILL.md` concise and route conditional detail to references
- add or update meaningful eval assertions for behavior changes

## Maintainer

- **Thien Ngo**
- GitHub: [@thiennc-tesoglobal](https://github.com/thiennc-tesoglobal)
- Email: [thienngo.tech@gmail.com](mailto:thienngo.tech@gmail.com)

## Credits and license

This project is derived from [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) by Derek Pearson. Thank you to the upstream author and contributors for the original skill collection.

Distributed under the [PolyForm Perimeter License 1.0.0](LICENSE). The original required copyright notice is preserved in the license file. PolyForm Perimeter includes a noncompete restriction, so review the license before redistributing or offering a competing product.

Apple frameworks, APIs, documentation, session content, and trademarks belong to Apple Inc. This project is not affiliated with, endorsed by, or sponsored by Apple.
