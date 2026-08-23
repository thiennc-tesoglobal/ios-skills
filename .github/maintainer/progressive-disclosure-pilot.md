# Progressive Disclosure Pilot

This record protects content coverage and evaluation evidence for the `push-notifications` and `storekit` entrypoint refactor.

## Baseline

| Skill | Before | Existing references | Local/published evals |
|---|---:|---:|---:|
| `push-notifications` | 498 lines / 2,234 words | 2 files / 1,430 lines | 3 / 3 |
| `storekit` | 490 lines / 1,791 words | 2 files / 913 lines | 3 / 3 |

Both entrypoints mixed shared contracts with long code recipes. The pilot preserves safety, lifecycle, routing, and verification in `SKILL.md`, while moving conditional implementation detail behind direct links.

## Content mapping

### Push notifications

| Previous entrypoint content | New location |
|---|---|
| Scope and sibling boundaries | `SKILL.md` opening and route table |
| Permission, APNs registration, tokens, remote payloads, background pushes | `references/apns-lifecycle.md` plus core invariants in `SKILL.md` |
| Local content, triggers, scheduling, update/removal | `references/local-notifications.md` |
| App delegate, center delegate, deep links, categories, badges, device testing | `references/notification-patterns.md` |
| Service/content extensions, attachments, communication notifications | `references/rich-notifications.md` |
| Correction rules, mistakes, review gate | Concise sections retained in `SKILL.md` |

### StoreKit

| Previous entrypoint content | New location |
|---|---|
| Scope, sibling boundaries, core purchase invariants | `SKILL.md` opening and core invariants |
| Product types/loading, StoreKit views, PurchaseAction/options, AppTransaction, fulfillment | `references/products-and-purchases.md` |
| Transaction updates, current entitlements, subscriptions, restore, revocation | `references/entitlements-and-subscriptions.md` |
| View customization, offers, server validation, testing, refunds, recovery | `references/storekit-advanced.md` |
| Digital-goods rules, subscription disclosures, IAP rejection boundaries | `references/app-review-guidelines.md` |
| Correction rules, mistakes, review gate | Concise sections retained in `SKILL.md` |

## Outcome

| Skill | After | Entrypoint line reduction | Entrypoint word reduction | Local/published evals |
|---|---:|---:|---:|---:|
| `push-notifications` | 160 lines / 1,172 words | 67.9% | 47.5% | 4 / 4 |
| `storekit` | 169 lines / 1,279 words | 65.5% | 28.6% | 4 / 4 |

The shorter-than-planned entrypoints are intentional: they retain more than 1,100 words of shared decision guidance each and avoid padding to a target line count. Conditional detail remains available through four direct references per skill.

## Acceptance gates

- Every reference is linked directly from its skill entrypoint with a loading trigger.
- Existing local and published eval scenarios remain unchanged and valid.
- Each skill adds one focused-routing regression case.
- Repository validation, unit tests, Claude plugin validation, Agent Skills discovery, and skill quick validation pass.
- GitNexus change detection reports only the intended skill, reference, eval, documentation, and generated index-block changes.
