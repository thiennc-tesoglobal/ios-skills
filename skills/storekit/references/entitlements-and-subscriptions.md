# Entitlements and Subscription State

Use this reference for app-lifetime transaction observation, current entitlements, subscription status, revocation, Family Sharing, restore, and reconciliation. Product merchandising and the initiating purchase call are covered in `products-and-purchases.md`.

## Contents

- Lifetime transaction observation
- Current entitlement reconciliation
- Product-specific access
- Subscription status and renewal state
- Restore purchases
- Recovery and server coordination

## Lifetime transaction observation

Start one `Transaction.updates` listener during app initialization and retain it for the app lifetime. It receives transactions created or changed outside the initiating purchase call, including Ask to Buy approval, purchases on another device, renewals, refunds, revocations, Family Sharing changes, and unfinished transactions StoreKit emits after launch.

```swift
final class StoreManager: Sendable {
    let updatesTask: Task<Void, Never>

    init(fulfillment: FulfillmentService) {
        updatesTask = Task(priority: .background) {
            for await result in Transaction.updates {
                guard case .verified(let transaction) = result else { continue }
                do {
                    try await fulfillment.reconcile(transaction)
                    await transaction.finish()
                } catch {
                    // Leave unfinished for durable retry and surface diagnostics.
                }
            }
        }
    }
}
```

Choose actor or `@MainActor` isolation from the state the manager owns; don't copy this shape blindly. Keep UI mutations on the appropriate actor and make fulfillment idempotent.

## Current entitlement reconciliation

`Transaction.currentEntitlements` emits the latest transaction that currently entitles the customer to:

- each non-consumable;
- each auto-renewable subscription whose renewal state is active or in grace period;
- each non-renewing subscription, including finished transactions.

It excludes consumables and refunded/revoked products. Apply the app's expiration policy to non-renewing subscriptions. Rebuild entitlement state from a fresh local set so removed/revoked products disappear.

```swift
func loadEntitledProductIDs() async -> Set<String> {
    var result = Set<String>()

    for await verification in Transaction.currentEntitlements {
        guard case .verified(let transaction) = verification,
              transaction.revocationDate == nil else { continue }

        if transaction.productType == .nonRenewing,
           transaction.expirationDate.map({ $0 <= .now }) ?? true {
            continue
        }

        result.insert(transaction.productID)
    }

    return result
}
```

Reconcile on launch and when transaction updates arrive. Refreshing on foreground can be appropriate for entitlement-sensitive screens, but don't start duplicate lifetime listeners from views.

## Product-specific access

Use transaction information as the access authority. UI configuration values such as `hasCurrentEntitlement` can customize merchandising but aren't a substitute for verified entitlement checks.

Where available for the deployment target, product-scoped current-entitlement sequences or SwiftUI entitlement task modifiers can drive a focused screen. Preserve the same verification, revocation, and product-type rules as collection-wide reconciliation.

Consumables require a separate delivered-balance/history source. Non-renewing subscriptions require app/server expiration persistence because StoreKit doesn't define their access window for the product.

## Subscription status and renewal state

Use `Product.SubscriptionInfo.status(for:)` or the subscription information associated with loaded products when the UI needs renewal details beyond a yes/no entitlement.

Verify both transaction and renewal information. Interpret states deliberately:

| State | Typical access policy |
|---|---|
| `.subscribed` | Grant access |
| `.inGracePeriod` | Grant access while billing recovery continues |
| `.inBillingRetryPeriod` | Follow product policy; don't report as a successful renewal |
| `.expired` | Remove subscription access unless another entitlement applies |
| `.revoked` | Remove access and reconcile immediately |

Use renewal information for auto-renew status, expiration reason, billing retry, price-increase consent, and eligible offer IDs. Do not infer these details from a single product purchase result.

Family Sharing ownership and revocation arrive through verified transactions. Avoid permanently binding shared access to a local Boolean.

## Restore purchases

StoreKit automatically makes current transactions available after reinstall or on another device. Always derive access proactively from `Transaction.currentEntitlements`.

Provide a visible Restore Purchases mechanism when expected by the store/paywall. `AppStore.sync()` forces synchronization and may prompt for App Store authentication, so call it only in response to an explicit user action—not automatically at launch.

```swift
func restore() async throws {
    try await AppStore.sync()
    entitledProductIDs = await loadEntitledProductIDs()
}
```

For non-renewing subscriptions and consumables, restoration depends on the app or server's own durable records.

## Recovery and server coordination

- Process `Transaction.unfinished` or launch updates when durable fulfillment needs explicit recovery.
- Keep server and device decisions consistent; use signed JWS representations when the server participates in entitlement authority.
- Handle App Store Server Notifications idempotently and reconcile rather than applying blind incremental toggles.
- Remove access on verified revocation/refund and make UI reflect the new state.
- Preserve original transaction identity where subscription lineage or durable non-consumable ownership requires it.

Advanced offers, billing recovery UI, refund requests, server validation, testing, and unfinished-transaction patterns are detailed in [storekit-advanced.md](storekit-advanced.md).

## Sources

- [Transaction.updates](https://sosumi.ai/documentation/storekit/transaction/updates)
- [Transaction.currentEntitlements](https://sosumi.ai/documentation/storekit/transaction/currententitlements)
- [Product.SubscriptionInfo.status(for:)](https://sosumi.ai/documentation/storekit/product/subscriptioninfo/status%28for%3A%29)
- [AppStore.sync](https://sosumi.ai/documentation/storekit/appstore/sync%28%29)
- [Transaction.unfinished](https://sosumi.ai/documentation/storekit/transaction/unfinished)
