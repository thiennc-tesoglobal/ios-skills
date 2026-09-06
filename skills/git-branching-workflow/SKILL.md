---
name: git-branching-workflow
description: "Standardized Git branch creation, naming taxonomies (feat/, fix/, refactor/, hotfix/, release/, chore/), trunk-based integration, and PR isolation lifecycles. Use when creating branches, preparing pull requests, or standardizing team git workflows; do not use for resolving merge conflicts or low-level git plumbing."
---

# Git Branching Workflow

Standardized Git branch creation, naming conventions, and lifecycle hygiene for Apple platform and mobile engineering teams.

## Contents

- [Trigger Boundary](#trigger-boundary)
- [Branch Naming Taxonomy](#branch-naming-taxonomy)
- [Branch Lifecycle Rules](#branch-lifecycle-rules)
- [Standard Commands](#standard-commands)
- [AI Agent Branch Isolation](#ai-agent-branch-isolation)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Trigger Boundary

Use this skill when creating branches for new features, bug fixes, refactoring, emergency hotfixes, or release preparation. Use it to establish consistent branch names and isolate work units before opening pull requests.

Do not use this skill for resolving complex three-way merge conflicts, debugging git index corruptions, or configuring low-level git hooks.

## Branch Naming Taxonomy

Branch names must be lowercase, hyphen-separated (kebab-case), and prefixed by type:

| Prefix | Scope | Example |
|---|---|---|
| `feat/` | New user-facing feature or architecture capability | `feat/apple-pay-checkout` |
| `fix/` | Bug fix during development or QA cycles | `fix/dark-mode-contrast` |
| `refactor/` | Code reorganization without changing observable behavior | `refactor/modularize-network-layer` |
| `perf/` | Performance optimization, memory leak fix, launch time | `perf/table-view-prefetching` |
| `test/` | Adding unit tests, UI tests, benchmarks, or eval suites | `test/storekit-purchase-evals` |
| `release/` | Version bump, metadata freeze, and release candidate staging | `release/v1.3.0` |
| `hotfix/` | Critical production patch branched directly from production base | `hotfix/crash-on-launch-ios26` |
| `chore/` | Tooling, dependency updates, CI/CD pipeline changes | `chore/update-fastlane-actions` |

When tracking a project management or issue tracker ticket, place the ticket key immediately after the prefix:
- `feat/IOS-1042-biometric-auth`
- `fix/CORE-89-keychain-migration`

## Branch Lifecycle Rules

1. **Always branch from up-to-date base**: Fetch remote state (`git fetch origin`) before branching off `origin/main` (or `origin/develop`). Never branch off stale local tracking branches.
2. **Single responsibility**: One branch must address one conceptual deliverable. Do not combine feature work with broad cleanup or unrelated refactors.
3. **Short-lived branches**: Keep feature branches short-lived (1–3 days). Integrate changes incrementally to prevent massive merge divergence.
4. **Clean commit history**: Group commits logically with imperative commit titles (`feat: add passkey enrollment coordinator`). Avoid intermediate commit noise ("wip", "fix typo") before final merge.
5. **Protected base branches**: Never commit directly to `main` or release branches. All integrations must pass CI verification via pull request.

## Standard Commands

### Create Feature Branch
```bash
git fetch origin
git checkout -b feat/passkey-enrollment origin/main
```

### Create Production Hotfix
```bash
git fetch origin
git checkout -b hotfix/expired-auth-token origin/main
```

### Sync Feature Branch with Base (Rebase)
```bash
git fetch origin
git rebase origin/main
```

### Delete Branch After Merge
```bash
git branch -d feat/passkey-enrollment
git push origin --delete feat/passkey-enrollment
```

## AI Agent Branch Isolation

When an AI agent is tasked with building a feature or executing a migration:
- Check out a dedicated branch (`feature/` or `feat/`) before making filesystem changes.
- Never perform destructive edits or broad refactoring on `main`.
- Verify that untracked or scratch files do not pollute the git working directory before opening a pull request.

## Common Mistakes

- **Ambiguous or generic branch names**: Using `temp`, `test`, `my-work`, or `fix-bug` without domain context.
- **Branching from stale local refs**: Creating a branch without running `git fetch origin` first, causing old base commit divergence.
- **Scope creep**: Adding feature work into a branch named `fix/...` or mixing architecture rewrites into a bugfix branch.
- **Using uppercase or snake_case**: Naming branches `Feat/NewUI` or `fix/crash_issue` instead of `feat/new-ui` and `fix/crash-issue`.
- **Rebasing public shared branches**: Rebasing branches where multiple developers collaborate, causing commit history rewrites.

## Review Checklist

- [ ] Branch name strictly adheres to `<prefix>/<kebab-case-description>` or `<prefix>/<TICKET>-<description>`.
- [ ] Branch was created from the latest remote base (`origin/main` or `origin/develop`).
- [ ] Branch changes match the declared prefix scope (no feature code in a `fix/` branch).
- [ ] No extraneous files (`.DS_Store`, build artifacts, temporary scratch scripts) are tracked.
- [ ] Branch is rebased onto the target base branch before opening PR.

## References

- [Branch Conventions and Lifecycle](references/branch-conventions.md) — Comprehensive guide on branching strategies, PR workflows, CI/CD trigger automation, and team hygiene.
