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
| App delegate, center delegate, deep links, categories | `references/notification-runtime.md` plus the complete archive |
| Simulator/provider/device testing and delivery diagnosis | `references/notification-testing.md` |
| Service extensions and exactly-once fallback | `references/service-extension.md` |
| Content UI and communication notifications | `references/content-extension.md` and `references/communication-notifications.md` |
| Full combined examples | `references/notification-patterns-complete.md` and `references/rich-notifications-complete.md` |
| Correction rules, mistakes, review gate | Concise sections retained in `SKILL.md` |

### StoreKit

| Previous entrypoint content | New location |
|---|---|
| Scope, sibling boundaries, core purchase invariants | `SKILL.md` opening and core invariants |
| Product types/loading, StoreKit views, PurchaseAction/options, AppTransaction, fulfillment | `references/products-and-purchases.md` |
| Transaction updates, current entitlements, subscriptions, restore, revocation | `references/entitlements-and-subscriptions.md` |
| Offers and merchandising | `references/storekit-offers.md` |
| StoreKit Test and sandbox controls | `references/storekit-testing.md` |
| Entitlement recovery and state transitions | `references/storekit-recovery.md` |
| View customization, server validation, and full recipes | `references/storekit-advanced-complete.md` |
| Digital-goods rules, subscription disclosures, IAP rejection boundaries | `references/app-review-guidelines.md` |
| Correction rules, mistakes, review gate | Concise sections retained in `SKILL.md` |

## Outcome

| Skill | After | Entrypoint line reduction | Entrypoint word reduction | Local/published evals |
|---|---:|---:|---:|---:|
| `push-notifications` | 160 lines / 1,172 words | 67.9% | 47.5% | 4 / 4 |
| `storekit` | 169 lines / 1,279 words | 65.5% | 28.6% | 4 / 4 |

The shorter-than-planned entrypoints are intentional: they retain shared decision guidance and avoid padding to a target line count. Conditional detail now routes through focused references, while the former long recipes remain opt-in archives.

## Acceptance gates

- Every reference is linked directly from its skill entrypoint with a loading trigger.
- Existing local and published eval scenarios remain unchanged and valid.
- Each skill adds one focused-routing regression case.
- APNs and extension evals include the corrected Simulator and exactly-once completion contracts.
- Behavioral A/B routes each scenario to its owning skill, uses the same model and prompts for baseline/candidate, and records an unauthenticated runner as unavailable rather than scoring a pass.
- Repository validation, unit tests, Claude plugin validation, Agent Skills discovery, and skill quick validation pass.
- GitNexus change detection reports only the intended skill, reference, eval, documentation, and generated index-block changes.
