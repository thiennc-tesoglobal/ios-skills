---
name: passkit
description: "Integrate Apple Pay and Wallet passes with PassKit. Use for payment buttons and requests, authorization, merchant and shipping fields, pass creation or updates, Add to Wallet flows, and eligible physical-goods, service, donation, or recurring-payment checkout."
---

# PassKit

Accept Apple Pay payments for physical goods, real-world services, donations, and recurring subscriptions, and manage Wallet passes. Targets Swift 6.3 / iOS 26+.

> **Constraint:** A single `PKPaymentRequest` supports at most one optional advanced request type (recurring, automatic reload, deferred, Apple Pay Later, or multi-token). Use separate requests if a transaction requires multiple modes.

## Contents

- [Setup & Availability](#setup--availability)
- [Apple Pay Button](#apple-pay-button)
- [Creating a Payment Request](#creating-a-payment-request)
- [Authorizing Payments](#authorizing-payments)
- [Wallet Passes](#wallet-passes)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Availability

1. Enable the **Apple Pay** capability in Xcode and configure a Merchant ID (`merchant.com.example`).
2. Verify payment readiness before rendering checkout controls:

```swift
import PassKit

func isApplePayAvailable() -> Bool {
    guard PKPaymentAuthorizationController.canMakePayments() else { return false }
    return PKPaymentAuthorizationController.canMakePayments(
        usingNetworks: [.visa, .masterCard, .amex],
        capabilities: .threeDSecure
    )
}
```

If `canMakePayments(usingNetworks:capabilities:)` returns true, Apple HIG requires Apple Pay to be presented as a primary payment method.

## Apple Pay Button

Always use Apple-provided button views. Never draw custom Apple Pay logos:

```swift
// SwiftUI
import SwiftUI
import PassKit

PayWithApplePayButton(.buy) {
    startPayment()
}
.payWithApplePayButtonStyle(.black)
.frame(height: 48)

// UIKit
let button = PKPaymentButton(paymentButtonType: .buy, paymentButtonStyle: .black)
button.addTarget(self, action: #selector(startPayment), for: .touchUpInside)
```

## Creating a Payment Request

Construct a `PKPaymentRequest` with required merchant details and summary items. The final summary item represents the total charged and must use the merchant or company name:

```swift
func makePaymentRequest() -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = "merchant.com.example.app"
    request.countryCode = "US"
    request.currencyCode = "USD"
    request.supportedNetworks = [.visa, .masterCard, .amex]
    request.merchantCapabilities = .threeDSecure

    request.paymentSummaryItems = [
        PKPaymentSummaryItem(label: "Coffee Beans", amount: NSDecimalNumber(string: "18.00")),
        PKPaymentSummaryItem(label: "Shipping", amount: NSDecimalNumber(string: "4.50")),
        PKPaymentSummaryItem(label: "Roasters Co.", amount: NSDecimalNumber(string: "22.50")) // Merchant total
    ]
    return request
}
```

## Authorizing Payments

Present the payment sheet with `PKPaymentAuthorizationController` and process token data on your payment processor:

```swift
final class CheckoutCoordinator: NSObject, PKPaymentAuthorizationControllerDelegate {
    func paymentAuthorizationController(
        _ controller: PKPaymentAuthorizationController,
        didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        // Send payment.token.paymentData to payment gateway (e.g. Stripe, Adyen)
        Task {
            do {
                try await PaymentGateway.charge(token: payment.token)
                completion(PKPaymentAuthorizationResult(status: .success, errors: nil))
            } catch {
                completion(PKPaymentAuthorizationResult(status: .failure, errors: [error]))
            }
        }
    }

    func paymentAuthorizationControllerDidFinish(_ controller: PKPaymentAuthorizationController) {
        controller.dismiss()
    }
}
```

## Wallet Passes

Add passes (`.pkpass`) to Apple Wallet:

```swift
let pass = try PKPass(data: passData)
if PKPassLibrary().containsPass(pass) {
    // Pass already exists in user's Wallet
} else {
    let addController = PKAddPassesViewController(pass: pass)!
    present(addController, animated: true)
}
```

## Common Mistakes

- **Incorrect final summary item**: The last item in `paymentSummaryItems` MUST be the grand total and its label MUST be the business name.
- **Custom Apple Pay buttons**: Drawing custom text or logos violates App Store guidelines and HIG.
- **Mixing multiple advanced payment modes**: A single `PKPaymentRequest` can specify only one advanced mode (e.g. recurring or deferred).
- **Hardcoding currency or country**: Use ISO 4217 currency codes and ISO 3166 country codes matching your merchant account.
- **Dismissing sheet without completion call**: Always invoke the authorization `completion(...)` handler before dismissing the payment controller.

## Review Checklist

- [ ] Apple Pay capability and merchant identifier configured in Xcode
- [ ] `canMakePayments(usingNetworks:capabilities:)` checked before rendering button
- [ ] Official `PayWithApplePayButton` or `PKPaymentButton` used
- [ ] Final payment summary item matches grand total and displays merchant name
- [ ] Payment token dispatched securely to processor backend
- [ ] Authorization result completion handler called in all code paths

## References

- Extended patterns (recurring/deferred payments, coupon codes, pass updates): [references/wallet-passes.md](references/wallet-passes.md)
- [PassKit framework](https://sosumi.ai/documentation/passkit)
- [PKPaymentRequest](https://sosumi.ai/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://sosumi.ai/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentButton](https://sosumi.ai/documentation/passkit/pkpaymentbutton)
- [PayWithApplePayButton](https://sosumi.ai/documentation/passkit/paywithapplepaybutton)
- [AddPassToWalletButton](https://sosumi.ai/documentation/passkit/addpasstowalletbutton)
- [PKPass](https://sosumi.ai/documentation/passkit/pkpass)
- [PKAddPassesViewController](https://sosumi.ai/documentation/passkit/pkaddpassesviewcontroller)
- [PKPassLibrary](https://sosumi.ai/documentation/passkit/pkpasslibrary)
- [PKPaymentNetwork](https://sosumi.ai/documentation/passkit/pkpaymentnetwork)
- [Apple Pay HIG](https://sosumi.ai/design/human-interface-guidelines/apple-pay)
