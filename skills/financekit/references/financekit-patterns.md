# FinanceKit Extended Patterns

Overflow reference for the `financekit` skill. Contains advanced query patterns, currency handling, and background delivery details that exceed the main skill file's scope.

## Contents

- [Predicate-Based Queries](#predicate-based-queries)
- [Transaction Field Reference](#transaction-field-reference)
- [Sorting and Pagination](#sorting-and-pagination)
- [Merchant Category Codes](#merchant-category-codes)
- [Currency Formatting](#currency-formatting)
- [Transaction Status Handling](#transaction-status-handling)
- [Balance History and Trends](#balance-history-and-trends)
- [Credit/Debit Interpretation by Account Type](#creditdebit-interpretation-by-account-type)

## Predicate-Based Queries

### Combining Predicates

FinanceKit queries accept Swift `#Predicate` macros. Combine conditions directly within the predicate.

```swift
import FinanceKit

func fetchRecentDebits(
    for accountID: UUID,
    since date: Date
) async throws -> [Transaction] {
    let store = FinanceStore.shared

    let predicate = #Predicate<Transaction> { transaction in
        transaction.accountID == accountID &&
        transaction.transactionDate > date &&
        transaction.creditDebitIndicator == .debit
    }

    let query = TransactionQuery(
        sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
        predicate: predicate,
        limit: nil,
        offset: nil
    )

    return try await store.transactions(query: query)
}
```

### Using Built-In Predicate Factories

FinanceKit provides static factory methods on query types for common patterns:

```swift
// Transactions by status
let bookedPredicate = TransactionQuery.predicate(forStatuses: [.booked])

// Transactions by type
let purchasePredicate = TransactionQuery.predicate(
    forTransactionTypes: [.pointOfSale, .directDebit, .billPayment]
)

// Transactions by merchant category code
let diningPredicate = TransactionQuery.predicate(
    forMerchantCategoryCodes: [
        MerchantCategoryCode(rawValue: 5812),  // Restaurants
        MerchantCategoryCode(rawValue: 5814),  // Fast food
    ]
)

// Balances by date range (available balance)
let balancePredicate = AccountBalanceQuery.predicate(
    availableSince: startDate,
    until: endDate
)

// Balances by date range (booked balance)
let bookedBalancePredicate = AccountBalanceQuery.predicate(
    bookedSince: startDate,
    until: endDate
)
```

### Date Range Queries

```swift
func fetchTransactionsInRange(
    accountID: UUID,
    from startDate: Date,
    to endDate: Date
) async throws -> [Transaction] {
    let predicate = #Predicate<Transaction> { transaction in
        transaction.accountID == accountID &&
        transaction.transactionDate >= startDate &&
        transaction.transactionDate <= endDate
    }

    let query = TransactionQuery(
        sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
        predicate: predicate,
        limit: nil,
        offset: nil
    )

    return try await FinanceStore.shared.transactions(query: query)
}
```

### Filtering by Posted Date

Some transactions have a `postedDate` (when booked by the institution) distinct from `transactionDate`:

```swift
let predicate = #Predicate<Transaction> { transaction in
    transaction.postedDate != nil &&
    transaction.status == .booked
}
```

## Transaction Field Reference

| Property | Type | Notes |
|---|---|---|
| `id` | `UUID` | Unique internal ID; WWDC24 notes it is unique per device |
| `accountID` | `UUID` | Links the transaction to its parent account |
| `transactionDate` | `Date` | Time the transaction took place; may differ from posting time |
| `postedDate` | `Date?` | Posting time; if absent, use `transactionDate` as the posted date |
| `transactionAmount` | `CurrencyAmount` | Positive decimal amount plus ISO 4217 currency code |
| `creditDebitIndicator` | `CreditDebitIndicator` | `.debit` or `.credit`; interpret by account type |
| `transactionDescription` | `String` | Display-friendly description |
| `originalTransactionDescription` | `String` | Unmodified institution description |
| `merchantName` | `String?` | Merchant name if available |
| `merchantCategoryCode` | `MerchantCategoryCode?` | ISO 18245 code wrapper with `Int16` raw value |
| `transactionType` | `TransactionType` | Includes `.pointOfSale`, `.transfer`, `.refund`, `.unknown`, and other documented cases |
| `status` | `TransactionStatus` | `.authorized`, `.pending`, `.booked`, `.memo`, or `.rejected` |
| `foreignCurrencyAmount` | `CurrencyAmount?` | Original foreign-currency amount if applicable |
| `foreignCurrencyExchangeRate` | `Decimal?` | Exchange rate if applicable |

## Sorting and Pagination

### Multiple Sort Descriptors

```swift
let query = TransactionQuery(
    sortDescriptors: [
        SortDescriptor(\Transaction.transactionDate, order: .reverse),
        SortDescriptor(\Transaction.transactionDescription)
    ],
    predicate: nil,
    limit: 20,
    offset: nil
)
```

### Paginated Loading

Use `limit` and `offset` for paged access:

```swift
@Observable
@MainActor
final class TransactionPager {
    private let store = FinanceStore.shared
    private let pageSize = 25
    private var currentOffset = 0
    private(set) var transactions: [Transaction] = []
    private(set) var hasMore = true

    let accountID: UUID

    init(accountID: UUID) {
        self.accountID = accountID
    }

    func loadNextPage() async throws {
        guard hasMore else { return }

        let predicate = #Predicate<Transaction> { transaction in
            transaction.accountID == self.accountID
        }

        let query = TransactionQuery(
            sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
            predicate: predicate,
            limit: pageSize,
            offset: currentOffset
        )

        let page = try await store.transactions(query: query)
        transactions.append(contentsOf: page)
        currentOffset += page.count
        hasMore = page.count == pageSize
    }

    func reset() {
        transactions = []
        currentOffset = 0
        hasMore = true
    }
}
```

### Account Sorting

```swift
let accountQuery = AccountQuery(
    sortDescriptors: [
        SortDescriptor(\Account.institutionName),
        SortDescriptor(\Account.displayName)
    ],
    predicate: nil,
    limit: nil,
    offset: nil
)
```

## Merchant Category Codes

`MerchantCategoryCode` wraps an `Int16` raw value conforming to ISO 18245. Common codes:

| Code | Category |
|---|---|
| 5411 | Grocery stores |
| 5541 | Gas stations |
| 5812 | Restaurants |
| 5814 | Fast food |
| 5912 | Pharmacies |
| 5999 | Miscellaneous retail |
| 7011 | Hotels and motels |
| 7832 | Movie theaters |
| 4121 | Rideshare / taxis |
| 5311 | Department stores |

### Grouping Transactions by Category

```swift
func groupByCategory(_ transactions: [Transaction]) -> [Int16: [Transaction]] {
    var groups: [Int16: [Transaction]] = [:]
    for transaction in transactions {
        let code = transaction.merchantCategoryCode?.rawValue ?? -1
        groups[code, default: []].append(transaction)
    }
    return groups
}
```

### Category Display Name Mapping

`MerchantCategoryCode` conforms to `CustomStringConvertible`, providing a `description` property for display:

```swift
if let mcc = transaction.merchantCategoryCode {
    print("Category: \(mcc.description)")
}
```

## Currency Formatting

FinanceKit stores amounts as `CurrencyAmount` with a `Decimal` amount and a currency code string. Use `FormatStyle` for localized display.

### Basic Formatting

```swift
func formatCurrency(_ amount: CurrencyAmount) -> String {
    amount.amount.formatted(
        .currency(code: amount.currencyCode)
    )
}
```

### Signed Amount Display

Amounts are always positive. Apply sign based on `creditDebitIndicator`:

```swift
func formatSignedAmount(
    _ amount: CurrencyAmount,
    indicator: CreditDebitIndicator,
    accountType: Account
) -> String {
    var value = amount.amount
    switch accountType {
    case .asset:
        if indicator == .debit { value = -value }
    case .liability:
        if indicator == .debit { value = -value }
    }
    return value.formatted(.currency(code: amount.currencyCode))
}
```

### Foreign Currency Transactions

```swift
func displayForeignTransaction(_ transaction: Transaction) -> String {
    var result = formatCurrency(transaction.transactionAmount)

    if let foreign = transaction.foreignCurrencyAmount {
        result += " (originally \(formatCurrency(foreign))"
        if let rate = transaction.foreignCurrencyExchangeRate {
            result += " at rate \(rate)"
        }
        result += ")"
    }

    return result
}
```

## Transaction Status Handling

Transactions progress through statuses as they are processed by the institution.

| Status | Meaning |
|---|---|
| `.authorized` | Transaction approved but not yet processed |
| `.pending` | Processing by the institution |
| `.memo` | Informational entry, not yet settled |
| `.booked` | Fully settled and posted |
| `.rejected` | Declined by the institution |

### Filtering by Status

```swift
func fetchPendingTransactions(for accountID: UUID) async throws -> [Transaction] {
    let predicate = #Predicate<Transaction> { transaction in
        transaction.accountID == accountID &&
        (transaction.status == .pending || transaction.status == .authorized)
    }

    let query = TransactionQuery(
        sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
        predicate: predicate,
        limit: nil,
        offset: nil
    )

    return try await FinanceStore.shared.transactions(query: query)
}
```

### Status Display

```swift
func statusLabel(for status: TransactionStatus) -> String {
    switch status {
    case .authorized: "Authorized"
    case .pending:    "Pending"
    case .memo:       "Memo"
    case .booked:     "Posted"
    case .rejected:   "Declined"
    @unknown default: "Unknown"
    }
}
```

## Balance History and Trends

Use paginated balance queries to build historical balance charts.

```swift
func fetchBalanceHistory(
    for accountID: UUID,
    limit: Int = 30
) async throws -> [AccountBalance] {
    let predicate = #Predicate<AccountBalance> { balance in
        balance.accountID == accountID
    }

    let query = AccountBalanceQuery(
        sortDescriptors: [SortDescriptor(\AccountBalance.id)],
        predicate: predicate,
        limit: limit,
        offset: nil
    )

    return try await FinanceStore.shared.accountBalances(query: query)
}
```

### Date-Ranged Balance Queries

Use the built-in predicate factories:

```swift
let thirtyDaysAgo = Calendar.current.date(byAdding: .day, value: -30, to: Date())!

let query = AccountBalanceQuery(
    sortDescriptors: [SortDescriptor(\AccountBalance.id)],
    predicate: AccountBalanceQuery.predicate(
        availableSince: thirtyDaysAgo,
        until: nil
    ),
    limit: nil,
    offset: nil
)
```

### Extracting Chart Data

```swift
struct BalanceDataPoint: Identifiable {
    let id: UUID
    let date: Date
    let amount: Decimal
    let currencyCode: String
}

func balanceChartData(from balances: [AccountBalance]) -> [BalanceDataPoint] {
    balances.compactMap { balance in
        switch balance.currentBalance {
        case .available(let bal), .booked(let bal):
            let signed = bal.creditDebitIndicator == .credit ? bal.amount.amount : -bal.amount.amount
            return BalanceDataPoint(
                id: balance.id,
                date: bal.asOfDate,
                amount: signed,
                currencyCode: bal.currencyCode
            )
        case .availableAndBooked(let available, _):
            let signed = available.creditDebitIndicator == .credit
                ? available.amount.amount : -available.amount.amount
            return BalanceDataPoint(
                id: balance.id,
                date: available.asOfDate,
                amount: signed,
                currencyCode: balance.currencyCode
            )
        @unknown default:
            return nil
        }
    }
}
```

## Credit/Debit Interpretation by Account Type

The meaning of `CreditDebitIndicator` varies by account type. This is a common source of confusion.

### Asset Accounts (Apple Cash, Savings)

| Indicator | Balance Effect | Example |
|---|---|---|
| `.debit` | Decreases balance | Sending money via Apple Cash |
| `.credit` | Increases balance | Receiving a payment |

### Liability Accounts (Apple Card)

| Indicator | Balance Effect | Example |
|---|---|---|
| `.debit` | Decreases available credit | Making a purchase |
| `.credit` | Increases available credit | Payment or refund |

### Unified Interpretation

```swift
enum MoneyDirection {
    case incoming, outgoing
}

func direction(
    of transaction: Transaction,
    in account: Account
) -> MoneyDirection {
    // For both asset and liability accounts, debit represents money going out
    // (balance decrease for assets, credit decrease for liabilities)
    transaction.creditDebitIndicator == .debit ? .outgoing : .incoming
}
```

