---
name: financekit
description: "Access eligible Wallet financial data using FinanceKit and FinanceKitUI. Use when querying transactions or balances, reading Apple Card, Apple Cash, Savings, or U.K. connected-account data, requesting financial-data authorization, using TransactionPicker, enabling iOS 26 background delivery, or saving and checking Wallet orders."
---

# FinanceKit

Use FinanceKit for eligible Wallet financial data, selective transaction
imports, Wallet order storage/querying, and iOS 26+ background delivery. Query
APIs start at iOS/iPadOS 17.4, `TransactionPicker` at 18, and background
delivery at 26.

Route Apple Pay checkout to `passkit`, widget rendering/timelines to
`widgetkit`, and merchant email/Business Connect optimization outside this skill.

## Contents

- [Eligibility and setup](#eligibility-and-setup)
- [Choose the access workflow](#choose-the-access-workflow)
- [Data and sync invariants](#data-and-sync-invariants)
- [Background delivery](#background-delivery)
- [Wallet orders](#wallet-orders)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Eligibility and setup

FinanceKit financial-data access is a managed capability. Verify all of these
before implementation:

- Organization Apple Developer account and Account Holder request.
- Eligible Finance-category iPhone app distributed through the U.S. or U.K.
  App Store with a genuine financial-management feature.
- Apple approval for `com.apple.developer.financekit` on the exact bundle ID.
- Clear `NSFinancialDataUsageDescription`.
- Required regulatory/account-connectivity obligations for apps offering
  financial products.

U.S. support covers eligible Apple Card, Apple Cash, and Savings data; family
exclusions apply. U.K. support starts at iOS/iPadOS 18.4 for supported open
banking institutions. Check current Apple eligibility before promising coverage.

Always guard availability before any financial-data or order API:

```swift
import FinanceKit

guard FinanceStore.isDataAvailable(.financialData) else { return }
let status = try await FinanceStore.shared.requestAuthorization()
```

Calling financial APIs when unavailable can terminate the app. Availability
does not guarantee accounts exist, and temporary restrictions surface as
`FinanceError.dataRestricted`.

## Choose the access workflow

| Need | API |
|---|---|
| Ongoing account, balance, or transaction access | `FinanceStore` authorization and queries |
| Selective immediate transaction import | FinanceKitUI `TransactionPicker` |
| Resumable catch-up or monitoring | Account/balance/transaction history sequences |
| Save/check a Wallet order | Orders availability plus `saveOrder`/`containsOrder` |
| Receive changes outside app lifetime | iOS 26+ background delivery extension |

Read [FinanceKit extended patterns](references/financekit-patterns.md) for
predicate factories, pagination, fields, currency formatting, credit/debit
interpretation, a resumable sync manager, SwiftUI integration, extension
lifecycle, and detailed error handling.

## Data and sync invariants

- Query only the data the feature needs. The user chooses accounts and the
  earliest exposed transaction date.
- Monetary amounts are positive. Apply `creditDebitIndicator`; do not infer sign
  from `Decimal`.
- Interpret credits in account context: a credit on a liability account may be
  a payment/refund increasing available credit, not income.
- Model ongoing sync across authorized accounts, balances, and transactions—not
  transactions alone.
- History changes contain inserted, updated, and deleted IDs. Commit local
  deletes/upserts before persisting `newToken`.
- Keep separate tokens per stream/account. On
  `FinanceError.historyTokenInvalid`, discard only the affected token and run a
  fresh catch-up for that scope.
- Use `isMonitoring: false` for finite catch-up and a separate
  `isMonitoring: true` sequence for live monitoring.
- Delete locally retained financial data when access is revoked or no longer
  justified.

## Background delivery

iOS 26+ registration methods are synchronous and nonthrowing:

```swift
FinanceStore.shared.enableBackgroundDelivery(
    for: [.accounts, .accountBalances, .transactions],
    frequency: .daily
)
```

The app and background extension both need the FinanceKit entitlement and a
shared App Group for durable state. Implement `didReceiveData(for:)` and return
only after essential writes complete. `willTerminate()` is the final chance to
save partial work, not a guarantee of unlimited cleanup time.

Hourly/daily/weekly frequencies are expected minimum intervals when data
changes; they are not exact schedules. Register every data type the local model
depends on.

## Wallet orders

Guard `.orders` availability independently. Handle every `SaveOrderResult`
(`added`, `cancelled`, `newerExisting`) and every contains result. A signed
archive is a server/merchant contract; do not fabricate or mutate it client-side.
Use `AddOrderToWalletButton` when the system presentation fits the product.

## Common mistakes

- Calling authorization or queries before `isDataAvailable`.
- Treating authorized status as proof that data exists or remains unrestricted.
- Treating positive amounts as already signed.
- Replacing resumable history with repeated full snapshots.
- Persisting a history token before local changes commit.
- Using a full authorization flow when `TransactionPicker` is sufficient.
- Adding the entitlement only to the app while the extension also uses FinanceKit.
- Assuming background frequency is an exact delivery schedule.

## Review checklist

- [ ] Eligibility, managed entitlement, bundle ID, region, and usage string are verified.
- [ ] Availability is checked before every data family and restriction errors are handled.
- [ ] Authorization and selective picker workflows follow least access.
- [ ] Amount signs and asset/liability interpretation are correct.
- [ ] Queries cover only needed fields and use bounded pagination where relevant.
- [ ] History applies deletes/upserts before token persistence and recovers invalid tokens by scope.
- [ ] Ongoing sync covers accounts, balances, and transactions as required.
- [ ] Background extension entitlement, App Group, data types, and save boundary are correct.
- [ ] Orders handle all save/existence outcomes.
- [ ] Revoked or obsolete financial data is removed.

## References

- [FinanceKit extended patterns](references/financekit-patterns.md)
- [FinanceKit documentation](https://sosumi.ai/documentation/financekit)
- [FinanceKitUI documentation](https://sosumi.ai/documentation/financekitui)
- [FinanceKit entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [Background delivery extension](https://sosumi.ai/documentation/financekit/implementing-a-background-delivery-extension)
- [FinanceKit eligibility](https://developer.apple.com/financekit/)
