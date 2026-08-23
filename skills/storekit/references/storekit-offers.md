# StoreKit Offers and Merchandising

Use this reference for subscription-store presentation, introductory,
promotional, win-back, and offer-code flows. Eligibility is a verified state,
not a reason to show every raw offer returned by StoreKit.

## Choose the surface

- Use `ProductView` for one product, `StoreView` for a collection, and
  `SubscriptionStoreView` for one subscription group.
- Use `.storeButton(.visible, for: .redeemCode)` or
  `.offerCodeRedemption(isPresented:)` for a user-initiated code path.
- Keep price, duration, renewal, trial conversion, and cancellation terms
  visible before purchase; use StoreKit-localized values rather than hardcoded
  copy.

## Eligibility and purchase

Check introductory eligibility and verified renewal information before showing
promotional or win-back choices. Pass the selected offer through the current
StoreKit 2 purchase option; do not invent legacy offer fields.

```swift
let eligibleIDs = statuses.flatMap { status -> [String] in
    guard case .verified(let renewalInfo) = status.renewalInfo else { return [] }
    return renewalInfo.eligibleWinBackOfferIDs
}

let eligibleOffers = winBackOffers.filter { offer in
    guard let id = offer.id else { return false }
    return eligibleIDs.contains(id)
}

if let offer = eligibleOffers.first {
    let result = try await product.purchase(options: [.winBackOffer(offer)])
    // Verify and fulfill the resulting transaction before finish.
}
```

Promotional offers require the server-signed offer data expected by the
supported SDK. An introductory offer is applied automatically when the user is
eligible; it is not a separate arbitrary purchase option.

## Offer-code redemption

Test the user-facing redemption UI separately from the StoreKit Test API. In an
Xcode StoreKit Test target, use the configured reference name with
`SKTestSession.buyProduct(identifier:options:)`; do not paste that test-only API
into production purchase code.

```swift
// Production/UI surface
.storeButton(.visible, for: .redeemCode)

// StoreKit Test target only
try await testSession.buyProduct(
    identifier: product.id,
    options: [.codeOffer(referenceName: "SUMMER2024")]
)
```

After redemption, verify the transaction and inspect
`transaction.offer?.type == .code` and the expected `transaction.offer?.id`.

For full view customization and server signing examples, read
[storekit-advanced-complete.md](storekit-advanced-complete.md).
