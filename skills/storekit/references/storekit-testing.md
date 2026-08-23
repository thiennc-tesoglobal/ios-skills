# StoreKit Test and Sandbox

Use this reference for StoreKit configuration files, `SKTestSession`, renewal
transitions, and release-boundary testing. Keep StoreKit Test-only APIs in a
test target that imports `StoreKitTest`.

## Test-only controls

```swift
import StoreKitTest

// `testSession` is an SKTestSession configured by the test target.
try await testSession.buyProduct(
    identifier: product.id,
    options: [.purchaseDate(Date(), renewalBehavior: .renewUntilNow)]
)

try await testSession.buyProduct(
    identifier: product.id,
    options: [.codeOffer(referenceName: "SUMMER2024")]
)
```

The valid renewal behaviors are `.renewUntilNow` and `.cancelImmediately`.
Use `product.purchase(options:)` for app purchase flows; use
`SKTestSession.buyProduct(identifier:options:)` for StoreKit Test state control.
Do not use `purchaseDate` or `codeOffer` as if they were production purchase
options.

## Minimum matrix

- Product load failure, unavailable product, and localized price/terms.
- Success, verification failure, `.pending`, `.userCancelled`, and duplicate
  observation through `Transaction.updates`.
- Ask to Buy approval/decline, refund, revocation, Family Sharing changes,
  grace period, billing retry, expiration, and unfinished transactions.
- Introductory, promotional, win-back, and offer-code eligibility and display.
- Clear purchase history and repeat tests so a previous transaction cannot hide
  a missing entitlement transition.

Use sandbox or a physical device for provider/App Store behavior that a local
StoreKit configuration cannot prove. Always verify the built paywall with real
localized product metadata before release.

For the complete configuration and transaction-manager recipes, read
[storekit-advanced-complete.md](storekit-advanced-complete.md#storekit-testing-in-xcode).
