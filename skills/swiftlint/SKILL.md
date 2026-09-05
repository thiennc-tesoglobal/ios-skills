---
name: swiftlint
description: "Configure and enforce SwiftLint through build-tool plugins, Xcode scripts, Swift Package plugins, or CI. Use for rule configuration, suppressions, baselines, autocorrection, reporters, strictness, multi-config setups, and staged rollout in existing Swift projects."
---

# SwiftLint

Enforce Swift style, formatting, and conventions using SwiftLint. Covers build-tool plugins, `.swiftlint.yml` configuration, staged rollouts, baselines, and CI integration.

> **Scope Boundary:** SwiftLint is a linting and style enforcement tool. For underlying API naming, conventions, and architectural rules, see `swift-api-design-guidelines` and `swift-code-review`.

## Contents

- [Recommended Setup (Build Tool Plugin)](#recommended-setup-build-tool-plugin)
- [Configuration (.swiftlint.yml)](#configuration-swiftlintyml)
- [Rule Selection & Rollout](#rule-selection--rollout)
- [Suppressions & Baselines](#suppressions--baselines)
- [Autocorrect & CI Pipeline](#autocorrect--ci-pipeline)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Recommended Setup (Build Tool Plugin)

Prefer the build tool plugin from `SimplyDanny/SwiftLintPlugins` for Xcode projects and Swift Packages. It avoids global machine installs and runs automatically during target compilation:

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/SimplyDanny/SwiftLintPlugins", from: "0.58.0")
],
targets: [
    .target(
        name: "MyFeature",
        plugins: [
            .plugin(name: "SwiftLintBuildToolPlugin", package: "SwiftLintPlugins")
        ]
    )
]
```

## Configuration (.swiftlint.yml)

Place `.swiftlint.yml` in the project root:

```yaml
included:
  - Sources
  - Tests

excluded:
  - Pods
  - .build
  - DerivedData

opt_in_rules:
  - empty_count
  - missing_docs
  - fatal_error_message

disabled_rules:
  - line_length
  - todo

line_length:
  warning: 120
  error: 160
```

## Rule Selection & Rollout

Adopt rules incrementally in existing codebases:
1. Start with high-confidence default rules; disable noisy formatting rules initially.
2. Fix autocorrectable violations with `swiftlint --fix`.
3. Introduce stricter opt-in rules team-by-team.

## Suppressions & Baselines

Suppress legitimate exceptions in code:

```swift
// swiftlint:disable:next force_cast
let cell = tableView.dequeueReusableCell(withIdentifier: "Cell") as! CustomCell

// Entire block suppression
// swiftlint:disable cyclomatic_complexity
func complexAlgorithm() { ... }
// swiftlint:enable cyclomatic_complexity
```

For legacy codebases, capture existing violations into a baseline to prevent regressions without blocking existing files: `swiftlint analyze --compiler-log-path xcodebuild.log`.

## Autocorrect & CI Pipeline

Run in CI before running unit tests:

```bash
# Lint with strict error exit codes
swiftlint --strict --reporter github-actions-logging

# Automatically fix whitespace and mechanical violations locally
swiftlint --fix
```

## Common Mistakes

- **Enabling all opt-in rules at once**: Overwhelms teams with thousands of warnings. Enable rules iteratively.
- **Global Homebrew dependency without version pinning**: Causes divergent lint errors across different team machines. Use Swift Package plugins or pin tool versions.
- **Not excluding build and dependency directories**: Linting `Pods/` or `.build/` dramatically slows down compilation.
- **Overusing broad inline suppressions**: Prefer `// swiftlint:disable:next rule_id` over disabling rules for entire files.
- **Running autocorrect in CI without automated commit**: Autocorrect should run locally pre-commit; CI should verify with `--strict`.

## Review Checklist

- [ ] SwiftLint version pinned across developer environments
- [ ] `.swiftlint.yml` excludes derived data and third-party dependencies
- [ ] Build tool plugin configured on active app and framework targets
- [ ] Suppressions target specific rules and are scoped narrowly
- [ ] CI pipeline fails on lint errors via `--strict`

## References

- [Adoption and configuration](references/adoption-and-configuration.md)
- [Plugins and run scripts](references/plugins-run-scripts-and-integrations.md)
- [Rules, suppressions, and baselines](references/rules-suppressions-and-baselines.md)
- [Rule reference index](references/rule-reference.md)
- [Custom rules and analyze](references/custom-rules-and-analyze.md)
- [Official SwiftLint Documentation](https://realm.github.io/SwiftLint/)
- [SwiftLint Rule Directory](https://realm.github.io/SwiftLint/rule-directory.html)
- [SimplyDanny/SwiftLintPlugins](https://github.com/SimplyDanny/SwiftLintPlugins)
