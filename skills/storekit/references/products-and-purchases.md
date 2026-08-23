# Products, Merchandising, and Purchases

Use this reference for product loading, StoreKit views, custom purchase controls, purchase options, result handling, AppTransaction, and durable delivery. Entitlement reconciliation and subscription state are covered in `entitlements-and-subscriptions.md`.

## Contents

- Product types and loading
- Choose a merchandising surface
- Custom purchase flow
- Purchase options
- Durable delivery and finishing
- App purchase verification

## Product types and loading

| Type | StoreKit case | Product responsibility |
|---|---|---|
| Consumable | `.consumable` | Deliver and persist quantity outside current entitlements |
| Non-consumable | `.nonConsumable` | Grant durable ownership after verified transaction |
| Auto-renewable subscription | `.autoRenewable` | Reconcile access from subscription transaction/status |
| Non-renewing subscription | `.nonRenewing` | App defines and persists expiration policy |

Keep identifiers centralized and load products from the App Store. Treat missing identifiers as configuration or availability failures, not empty prices to hardcode around.

```swift
enum ProductID {
    static let premium = "com.example.premium"
    static let monthly = "com.example.pro.monthly"
    static let yearly = "com.example.pro.yearly"
    static let all = [premium, monthly, yearly]
}

let products = try await Product.products(for: ProductID.all)
```

Display `displayName`, `description`, and `displayPrice`. Do not hardcode currency symbols, trial copy, or localized price strings.

## Choose a merchandising surface

Prefer StoreKit views for standard stores and paywalls:

- `ProductView` for one product;
- `StoreView` for a product collection;
- `SubscriptionStoreView` for auto-renewable options in one subscription group.

StoreKit views load localized product data and initiate purchases. Configure restore/redeem controls and subscription policy destinations as required by the product and platform.

```swift
SubscriptionStoreView(groupID: subscriptionGroupID)
    .subscriptionStoreControlStyle(.prominentPicker)
    .storeButton(.visible, for: .restorePurchases)
    .subscriptionStorePolicyDestination(url: termsURL, for: .termsOfService)
    .subscriptionStorePolicyDestination(url: privacyURL, for: .privacyPolicy)
```

For custom SwiftUI buttons, use `PurchaseAction` from the environment. Use `purchase(confirmIn:options:)` for UIKit/AppKit presentation and lower-level `product.purchase(options:)` when the platform or custom flow requires it. Preserve existing project abstraction when it already applies these contracts correctly.

## Custom purchase flow

Handle every result. Verification, durable delivery, and finish order are non-negotiable.

```swift
@Environment(\.purchase) private var purchase

func buy(_ product: Product) async throws {
    let result = try await purchase(product, options: [
        .appAccountToken(accountToken)
    ])

    switch result {
    case .success(let verification):
        let transaction = try verified(verification)
        try await fulfillment.deliver(transaction)
        await transaction.finish()

    case .pending:
        // Ask to Buy or other deferred approval. Don't unlock yet.
        purchaseState = .pending

    case .userCancelled:
        purchaseState = .idle

    @unknown default:
        purchaseState = .failed(.unsupportedResult)
    }
}

func verified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .verified(let value): value
    case .unverified(_, let error): throw error
    }
}
```

Disable or serialize duplicate purchase attempts according to the UI design. Keep cancellation distinct from an error and pending distinct from success.

## Purchase options

- `.appAccountToken(UUID)` associates a stable app account with App Store transactions for reconciliation. Use a random UUID assigned to the account, not an email or other personal identifier.
- `.quantity(Int)` applies to eligible consumables and must match fulfillment.
- Promotional and win-back offer options require eligibility and offer-specific handling; read [storekit-advanced.md](storekit-advanced.md).
- `.simulatesAskToBuyInSandbox(true)` is a test option, not production business logic.

SwiftUI store views can provide options with `inAppPurchaseOptions`. Use start/completion callbacks for UI state and analytics, but keep verified fulfillment idempotent because the launch transaction listener can observe the same transaction path.

## Durable delivery and finishing

The fulfillment boundary must make duplicate verified transaction delivery safe. Use the transaction/original transaction identifiers appropriate to the product model and store fulfillment state durably before finishing.

Call `transaction.finish()` only after the content or service is delivered. If delivery fails, preserve enough information to retry and leave the transaction unfinished so `Transaction.updates` or `Transaction.unfinished` can recover it.

Consumables require app/server persistence because `Transaction.currentEntitlements` does not represent consumed balance or delivery history. Never grant balance solely from a local button state.

## App purchase verification

Use `AppTransaction.shared` when the business model depends on the app's original purchase, original version, or migration from a paid app. Verify its `VerificationResult` before using it. Do not use AppTransaction as a replacement for individual In-App Purchase entitlement checks.

```swift
let result = try await AppTransaction.shared
guard case .verified(let appTransaction) = result else {
    throw PurchaseError.unverifiedAppTransaction
}

let originalVersion = appTransaction.originalAppVersion
let originalPurchaseDate = appTransaction.originalPurchaseDate
```

## Sources

- [In-App Purchase](https://sosumi.ai/documentation/storekit/in-app-purchase)
- [Product](https://sosumi.ai/documentation/storekit/product)
- [PurchaseAction](https://sosumi.ai/documentation/storekit/purchaseaction)
- [StoreView](https://sosumi.ai/documentation/storekit/storeview)
- [SubscriptionStoreView](https://sosumi.ai/documentation/storekit/subscriptionstoreview)
- [Transaction.finish](https://sosumi.ai/documentation/storekit/transaction/finish%28%29)
