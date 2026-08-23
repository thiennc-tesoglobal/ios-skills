---
name: storekit
description: "Implement or review in-app purchases and subscriptions with StoreKit 2, including paywalls, transactions, entitlement verification, offers, renewal state, testing, Family Sharing, Ask to Buy, refunds, and billing recovery. Route physical-goods checkout to passkit."
---

# StoreKit 2 In-App Purchases and Subscriptions

Build, review, and debug digital-goods purchases with modern StoreKit. Preserve the project's deployment target and existing StoreKit abstraction. Use original `SKProduct`/`SKPaymentQueue` APIs only when legacy support or an existing migration boundary requires them.

Route physical goods and real-world services to `passkit`; full submission/privacy/rejection audits to `app-store-review`; metadata and conversion work to `app-store-optimization`.

## Contents

- [Route by task](#route-by-task)
- [Core invariants](#core-invariants)
- [Implementation workflow](#implementation-workflow)
- [Choose the purchase surface](#choose-the-purchase-surface)
- [Purchase and fulfillment](#purchase-and-fulfillment)
- [Transaction updates and entitlements](#transaction-updates-and-entitlements)
- [Subscriptions, restore, and recovery](#subscriptions-restore-and-recovery)
- [Correction reviews](#correction-reviews)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)

## Route by task

Read only the references required by the request:

- For product loading, StoreKit views, `PurchaseAction`, direct purchases, options, AppTransaction, or durable content delivery, read [products, merchandising, and purchases](references/products-and-purchases.md).
- For `Transaction.updates`, current entitlements, subscription status, revocation, Family Sharing, restore, or reconciliation, read [entitlements and subscription state](references/entitlements-and-subscriptions.md).
- For offer eligibility, subscription surfaces, offer codes, and disclosures, read [StoreKit offers and merchandising](references/storekit-offers.md).
- For StoreKit configuration files, `SKTestSession`, renewal controls, and test matrices, read [StoreKit Test and Sandbox](references/storekit-testing.md).
- For entitlement recovery, subscriptions, refunds, revocations, Family Sharing, Ask to Buy, or unfinished transactions, read [StoreKit recovery and state transitions](references/storekit-recovery.md).
- For the focused reference index, read [advanced StoreKit](references/storekit-advanced.md). Use [complete advanced StoreKit recipes](references/storekit-advanced-complete.md) only for broad end-to-end examples or migration.
- For digital-goods payment rules, reader/external-link boundaries, subscription disclosures, or IAP rejection risks, read [App Review IAP guidance](references/app-review-guidelines.md).

Do not load offer, compliance, or subscription material for a narrow consumable/non-consumable task.

## Core invariants

1. Verify every `VerificationResult` before granting access or using signed transaction state.
2. Deliver or persist fulfillment durably and idempotently before calling `transaction.finish()`.
3. Start one retained `Transaction.updates` listener during app initialization, not when a paywall appears.
4. Rebuild entitlement state from verified transaction sequences; don't use a local Boolean as purchase authority.
5. Handle `.pending`, `.userCancelled`, errors, refunds/revocations, and recovery as distinct states.
6. Use StoreKit-localized product names, descriptions, prices, and subscription terms.
7. Call `AppStore.sync()` only from an explicit user restore action because it may prompt for authentication.

## Implementation workflow

1. Confirm the business model, product types, identifiers, subscription groups, App Store Connect state, platforms, and deployment target.
2. Decide whether StoreKit views or a custom purchase surface best fits the product.
3. Define one verified, idempotent fulfillment boundary shared by purchase completion and transaction updates.
4. Start lifetime transaction observation and load current entitlement state.
5. Implement purchase, pending/cancel/error UI, restore, and subscription recovery paths.
6. Test with a StoreKit configuration, sandbox where needed, and realistic renewal/refund/revocation/Ask to Buy states.
7. Verify the built paywall on the target platform with real localized product data before release.

## Choose the purchase surface

Prefer StoreKit views for standard merchandising:

- `ProductView` for one product;
- `StoreView` for a collection;
- `SubscriptionStoreView` for auto-renewable subscriptions in one group.

They load localized product information and initiate purchases. Configure visible restore/redeem controls and policy destinations according to the product and platform.

For custom SwiftUI buttons, prefer `PurchaseAction`. Use `purchase(confirmIn:options:)` for UIKit/AppKit or lower-level `product.purchase(options:)` where the platform/custom flow requires it. Don't introduce a parallel purchasing abstraction when the project already centralizes verification and fulfillment correctly.

| Product type | Entitlement responsibility |
|---|---|
| Consumable | Persist delivered balance/history outside current entitlements |
| Non-consumable | Grant durable ownership from verified transaction state |
| Auto-renewable | Reconcile verified entitlement and subscription renewal state |
| Non-renewing | App/server defines and persists the access-expiration policy |

## Purchase and fulfillment

Handle all `PurchaseResult` cases:

```swift
switch try await purchase(product) {
case .success(let result):
    let transaction = try verified(result)
    try await fulfillment.deliver(transaction)
    await transaction.finish()

case .pending:
    purchaseState = .pendingApproval

case .userCancelled:
    purchaseState = .idle

@unknown default:
    purchaseState = .failed
}
```

Never use `unsafePayloadValue` to unlock content. Never finish before delivery. If durable delivery fails, leave the transaction unfinished and recover it through the lifetime listener or `Transaction.unfinished`.

Make fulfillment safe when the initiating purchase flow and `Transaction.updates` observe the same transaction. For consumables, reconcile server/app balance before finish; `currentEntitlements` doesn't retain consumed quantity.

## Transaction updates and entitlements

Start one listener at app launch. It can deliver Ask to Buy approvals, purchases from another device, renewals, refunds, revocations, Family Sharing changes, and unfinished transactions.

`Transaction.currentEntitlements` represents verified current access for non-consumables, active or grace-period auto-renewable subscriptions, and non-renewing subscription transactions. It excludes consumables and refunded/revoked products. Apply the app's expiration policy to non-renewing subscriptions.

Rebuild a fresh entitlement set so removed or revoked access disappears. Reconcile at launch and on transaction updates; refresh on foreground only where the product needs it, without creating duplicate listeners.

UI hints such as a StoreKit view's entitlement configuration can customize merchandising but aren't access authority. Grant access from verified transaction information.

## Subscriptions, restore, and recovery

Use verified subscription status/renewal information when the UI needs more than yes/no access. Treat `.subscribed` and `.inGracePeriod` as entitled; distinguish billing retry, expiration, and revocation according to product policy.

StoreKit automatically makes transaction information available after reinstall or on a new device. Derive access proactively from current entitlements and expose a user-initiated Restore Purchases path. Do not call `AppStore.sync()` automatically at launch.

Offers require both configured offer data and current eligibility. A raw `winBackOffers` list is not eligibility; compare it with verified renewal information. Keep StoreKit configuration and sandbox coverage for promotional offers, win-back, offer codes, Ask to Buy, renewal transitions, refunds, revocations, and Family Sharing.

## Correction reviews

When reviewing flawed StoreKit code, name the broken contract:

- No lifetime listener: start retained `Transaction.updates` observation during app initialization.
- Access from unverified result/local flag: verify and reconcile from transaction state.
- Finish immediately: deliver durably first; unfinished transactions are the recovery mechanism.
- Pending treated as failure/success: keep pending UI and wait for a verified update.
- Restore at launch: use current entitlements automatically and reserve `AppStore.sync()` for explicit user action.
- Hardcoded price/trial copy: use StoreKit localized product and offer data.
- Every win-back offer shown: filter raw offers by verified eligible IDs.
- Legacy offer fields: use current `transaction.offer?.type` and `.id` APIs for the supported SDK.
- Broad IAP/external-link claim: defer to current guideline, entitlement, region, and storefront evidence.

## Common mistakes

- Creating transaction listeners from paywalls or views.
- Updating UI but not durable fulfillment before finish.
- Treating consumables as current entitlements.
- Forgetting non-renewing subscription expiration policy.
- Keeping revoked/refunded products in a cached entitlement set.
- Hardcoding prices, duration, trial, or renewal terms.
- Starting duplicate purchases or swallowing `.pending`.
- Using StoreKit view configuration as authorization to unlock content.
- Testing only the immediate happy-path purchase.
- Mixing physical-goods checkout or full App Review work into StoreKit implementation.

## Review checklist

- [ ] Product types, IDs, groups, platforms, and deployment target are explicit.
- [ ] Purchase surface matches the product and existing architecture.
- [ ] StoreKit-localized product/price/terms are displayed.
- [ ] Verification precedes every entitlement or fulfillment decision.
- [ ] Fulfillment is durable and idempotent before finish.
- [ ] One retained transaction listener starts during app initialization.
- [ ] Current entitlement logic handles product type, expiration, and revocation.
- [ ] Pending, cancellation, error, refund, and recovery states are distinct.
- [ ] Restore is visible and `AppStore.sync()` is user initiated.
- [ ] Subscription policy links and required disclosures are present.
- [ ] Offers are filtered by current verified eligibility.
- [ ] StoreKit configuration/sandbox tests cover changed state transitions.
- [ ] Server reconciliation uses signed transaction data when the server is authoritative.
- [ ] App Review, ASO, and physical-goods work are routed to the correct skill.

## Official references

- [Choosing a StoreKit API](https://sosumi.ai/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [In-App Purchase](https://sosumi.ai/documentation/storekit/in-app-purchase)
- [Transaction.updates](https://sosumi.ai/documentation/storekit/transaction/updates)
- [Transaction.currentEntitlements](https://sosumi.ai/documentation/storekit/transaction/currententitlements)
- [SubscriptionStoreView](https://sosumi.ai/documentation/storekit/subscriptionstoreview)
