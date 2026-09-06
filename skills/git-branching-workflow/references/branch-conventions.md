# Git Branch Conventions and Lifecycle Reference

Detailed reference for team branching workflows, CI/CD automation triggers, rebase hygiene, and pull request management in Apple platform and mobile engineering repositories.

## Contents

- [Branching Models](#branching-models)
- [Naming Taxonomy and Ticket Binding](#naming-taxonomy-and-ticket-binding)
- [Integration Strategies](#integration-strategies)
- [CI/CD Branch Triggers](#cicd-branch-triggers)
- [Multi-Agent and Team Isolation](#multi-agent-and-team-isolation)
- [Emergency Hotfix Workflows](#emergency-hotfix-workflows)
- [Branch Cleanup and Pruning](#branch-cleanup-and-pruning)
- [Common Anti-Patterns](#common-anti-patterns)

---

## Branching Models

Mobile applications have distinct release requirements compared to backend services because app binaries must be reviewed by Apple and deployed to App Store Connect / TestFlight. Choosing the correct branching strategy prevents pipeline congestion and release blockers.

### 1. Trunk-Based Development (Recommended for Modern Mobile Teams)

- **Trunk (`main`)**: The single source of truth. Always compilable, green, and testable.
- **Short-Lived Feature Branches**: Developers and AI agents cut branches off `origin/main` that live for 1–3 days max.
- **Feature Flags**: Larger features spanning multiple days are merged into `main` behind runtime flags (e.g., via `UserDefaults`, AppStorage, or Remote Config) rather than maintaining long-lived feature branches.
- **Release Branches**: When cutting a release build, branch `release/vX.Y.Z` from `main`. Only release-blocking fixes are cherry-picked into this branch.

### 2. GitHub Flow

- Everything in `main` is deployable.
- Create branch off `main`, open PR early for discussion, merge after CI checks and code review approve.
- Well-suited for open-source frameworks, Swift packages, and utility libraries.

### 3. Gitflow (Legacy / Enterprise)

- Uses persistent `develop` and `main` branches.
- Feature branches branch from and merge back into `develop`.
- `release/*` branches bridge `develop` to `main`.
- `hotfix/*` branches branch off `main` and merge into both `main` and `develop`.
- Use only when mandated by strict enterprise release train cadences.

---

## Naming Taxonomy and Ticket Binding

A structured naming taxonomy enables automated tooling, changelog generators, and bot reviewers to understand the exact scope of a branch.

### Branch Prefix Matrix

| Prefix | Intent | Lifecycle | Allowed Changes |
|---|---|---|---|
| `feat/` | New user capability or feature architecture | 1–3 days | New UI, business logic, domain models, feature tests |
| `fix/` | Correcting unintended behavior or crash | < 1 day | Bug fix, regression test, minimal touch footprint |
| `refactor/` | Code structure improvement without behavior change | 1–2 days | File extraction, renaming, dependency inversion, zero UI diff |
| `perf/` | Profiling optimization (CPU, memory, launch time) | 1–2 days | Instruments optimizations, prefetching, lazy loading |
| `test/` | Adding test coverage or eval scenarios | < 1 day | Unit tests, UI tests, mocks, test fixtures, evals |
| `release/` | Release staging and candidate freeze | 2–5 days | Version bumps, changelog finalization, App Store metadata |
| `hotfix/` | Production crash or critical business failure | Emergency (<hours) | Minimal targeted hotfix, isolated patch |
| `chore/` | CI/CD, dependency upgrades, build configs | < 1 day | Fastlane scripts, GitHub Actions, SPM versions, linter rules |

### Issue Tracker Integration

When using Jira, Linear, or GitHub Issues, standardizing the ticket identifier in the branch name facilitates two-way automation:

```
feat/<PROJECT>-<ISSUE_NUMBER>-<short-description>
```

Examples:
- `feat/IOS-412-passkey-registration`
- `fix/AUTH-89-refresh-token-race-condition`
- `refactor/NET-201-async-urlsession-adapter`

Do not include special characters, underscores, or slashes inside the slug:
- **Good**: `feat/IOS-412-passkey-registration`
- **Bad**: `feat/IOS_412/passkey_registration!`
- **Bad**: `feat/IOS-412-passkey/registration`

---

## Integration Strategies

### 1. Rebase vs. Merge Commit

For feature branch synchronization before merging:

```bash
# Fetch latest state from upstream
git fetch origin

# Rebase feature commits on top of latest origin/main
git rebase origin/main
```

**Why rebase during development:**
- Keeps a linear, clean history without unnecessary "Merge branch 'main' into feat/..." merge bubbles.
- Allows bisecting bugs (`git bisect`) reliably without navigating intertwined branches.

### 2. PR Merge Options

- **Squash and Merge (Recommended default)**: Condenses all intermediate commits (including typos, incremental work) into a single clean commit on `main`. Keeps main history readable.
- **Rebase and Merge**: Retains individual commits while maintaining a linear history. Requires all commits on the branch to be independently compilable and meaningful.
- **Merge Commit**: Preserves the exact branch topology. Only recommended when merging `release/*` into `main` to retain full release history.

---

## CI/CD Branch Triggers

Branch naming conventions allow CI/CD systems to run targeted lanes instead of triggering heavy full-suite builds on every commit.

### Example: GitHub Actions Triggers

```yaml
name: CI Pipeline

on:
  push:
    branches:
      - 'main'
      - 'release/**'
  pull_request:
    branches:
      - 'main'

jobs:
  lint:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - name: SwiftLint
        run: swiftlint lint --strict

  test:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - name: Fast Unit Tests
        run: xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 16'

  build-testflight:
    if: startsWith(github.ref, 'refs/heads/release/')
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - name: Archive and Upload to TestFlight
        run: fastlane beta
```

---

## Multi-Agent and Team Isolation

When autonomous AI agents work alongside human developers or other agents:

1. **Dedicated Agent Branching**:
   - The agent must always establish a unique branch:
     `feat/agent-<task-id>-<slug>` or `fix/agent-<task-id>-<slug>`.
   - Never let an agent execute edits on `main` or uncommitted working trees.
2. **Untracked Artifact Hygiene**:
   - AI tools frequently generate scratch scripts, diffs, or debug logs.
   - Always run `git status --porcelain` before staging.
   - Add temporary paths to `.gitignore` or clean them before committing:
     ```bash
     git clean -nd  # Dry-run check for untracked clutter
     ```
3. **Atomic Commits**:
   - Avoid generic commit messages like `update code` or `agent modifications`.
   - Use Conventional Commits:
     ```bash
     git commit -m "feat(auth): integrate ASAuthorizationController for passkeys"
     ```

---

## Emergency Hotfix Workflows

When a critical bug affects the production App Store build:

1. Identify the exact release tag deployed to production:
   ```bash
   git tag -l "v*"
   git fetch --tags
   ```

2. Cut the hotfix branch directly from that release tag:
   ```bash
   git checkout -b hotfix/v1.2.1-iap-receipt-validation v1.2.0
   ```

3. Apply the minimal fix:
   - Do NOT update dependencies.
   - Do NOT reformat unrelated code.
   - Do NOT introduce new feature code.

4. Validate and cut the hotfix release:
   - Tag the new release: `v1.2.1`.
   - Merge the hotfix back into `main` so the bug does not regress in subsequent releases.

---

## Branch Cleanup and Pruning

Stale, merged branches clutter remote repositories and slow down developer tooling.

### Local Cleanup
Delete local branch after remote merge:
```bash
git branch -d feat/apple-pay-checkout
```

Force delete abandoned branch:
```bash
git branch -D feat/abandoned-experiment
```

Prune remote tracking references that no longer exist on remote:
```bash
git fetch --prune
```

### Scripted Cleanup for Stale Local Branches
To remove all local branches whose upstreams have been deleted:
```bash
git fetch -p && git branch -vv | awk '/: gone]/{print $1}' | xargs -r git branch -D
```

---

## Common Anti-Patterns

1. **The Megabranch**: A feature branch that lives for 4 weeks with 60 commits touching 80 files. Conflict resolution becomes an all-day ordeal. Split into small, incremental PRs merged behind feature flags.
2. **Dirty Base Branch**: Developing directly on `main` and then retroactively creating a branch. Any accidental commit on `main` risks being pushed prematurely.
3. **Commit Sprawl ("WIP Commits")**: Committing messages like `wip`, `fix typo`, `try again`, `test 3`. Clean up via interactive rebase (`git rebase -i HEAD~4`) or squash merge.
4. **Branch Re-use After Merge**: Continuing to work on a branch that was already merged into `main`. Always delete the merged branch and cut a fresh branch from the updated `main`.
