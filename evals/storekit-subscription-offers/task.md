A subscription app wants to target cancelled subscribers with win-back and promotional offers. The current plan calls `Product.SubscriptionInfo.Status.status(for:)`, shows every `product.subscription?.winBackOffers` entry, uses `.subscriptionPromotionalOffer(offer: signature:)` on a StoreKit SwiftUI view, logs applied offers with `transaction.offerType` and `transaction.offerID`, and drives StoreKit Test with `product.purchase(options: [.purchaseDate(Date(), renewalBehavior: .default), .codeOffer(...)])`.

Correct the plan using current StoreKit APIs and explain how to test the offer paths.
