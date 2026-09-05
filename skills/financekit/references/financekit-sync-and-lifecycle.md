# FinanceKit Sync Manager, Background Delivery, and Lifecycle

Use this reference when building resumable sync managers with history tokens, handling background delivery extensions, SwiftUI views, and FinanceKit error recovery.

## Contents

- [Resumable Sync Manager](#resumable-sync-manager)
- [SwiftUI Integration](#swiftui-integration)
- [Background Delivery Extension Lifecycle](#background-delivery-extension-lifecycle)
- [Error Handling](#error-handling)

---

## Resumable Sync Manager

A manager for catch-up sync (`isMonitoring: false`), live monitoring (`true`), token persistence, and explicit deletion removal.

```swift
import FinanceKit

@Observable
@MainActor
final class FinanceSyncManager {
    private let store = FinanceStore.shared
    private let tokenKey = "financekit.sync.token"

    private(set) var accounts: [Account] = []
    private(set) var balances: [UUID: [AccountBalance]] = [:]
    private(set) var transactions: [UUID: [Transaction]] = [:]
    private(set) var syncError: Error?

    // MARK: - Initial Load

    func performInitialLoad() async {
        guard FinanceStore.isDataAvailable(.financialData) else { return }

        do {
            let status = try await store.authorizationStatus()
            guard status == .authorized else { return }
            accounts = try await fetchAllAccounts()
            for account in accounts {
                balances[account.id] = try await fetchBalances(for: account.id)
            }
        } catch {
            syncError = error
        }
    }

    // MARK: - Catch-Up Sync

    func syncTransactions(for accountID: UUID) async {
        let token = loadToken(for: accountID)

        do {
            let history = store.transactionHistory(
                forAccountID: accountID,
                since: token,
                isMonitoring: false
            )

            for try await changes in history {
                applyChanges(changes, for: accountID)
                saveToken(changes.newToken, for: accountID)
            }
        } catch let error as FinanceError where error == .historyTokenInvalid {
            // Token expired: discard it, then immediately rebuild local state
            // and replacement token from a fresh catch-up sequence.
            clearToken(for: accountID)
            transactions[accountID] = []
            await syncTransactions(for: accountID)
        } catch {
            syncError = error
        }
    }

    // MARK: - Live Monitoring

    func startMonitoring(for accountID: UUID) async {
        let token = loadToken(for: accountID)

        do {
            let history = store.transactionHistory(
                forAccountID: accountID,
                since: token,
                isMonitoring: true
            )

            for try await changes in history {
                applyChanges(changes, for: accountID)
                saveToken(changes.newToken, for: accountID)
            }
        } catch {
            syncError = error
        }
    }

    // MARK: - Private

    private func fetchAllAccounts() async throws -> [Account] {
        let query = AccountQuery(
            sortDescriptors: [SortDescriptor(\Account.displayName)],
            predicate: nil,
            limit: nil,
            offset: nil
        )
        return try await store.accounts(query: query)
    }

    private func fetchBalances(for accountID: UUID) async throws -> [AccountBalance] {
        let predicate = #Predicate<AccountBalance> { $0.accountID == accountID }
        let query = AccountBalanceQuery(
            sortDescriptors: [SortDescriptor(\AccountBalance.id)],
            predicate: predicate,
            limit: nil,
            offset: nil
        )
        return try await store.accountBalances(query: query)
    }

    private func applyChanges(
        _ changes: FinanceStore.Changes<Transaction>,
        for accountID: UUID
    ) {
        var current = transactions[accountID] ?? []

        // Remove deleted IDs first so local storage matches Wallet removals.
        let deletedSet = Set(changes.deleted)
        current.removeAll { deletedSet.contains($0.id) }

        // Update existing
        for updated in changes.updated {
            if let index = current.firstIndex(where: { $0.id == updated.id }) {
                current[index] = updated
            }
        }

        // Insert new
        current.append(contentsOf: changes.inserted)

        // Sort by date descending
        current.sort { $0.transactionDate > $1.transactionDate }

        transactions[accountID] = current
    }

    private func applyBalanceChanges(
        _ changes: FinanceStore.Changes<AccountBalance>,
        for accountID: UUID
    ) {
        var current = balances[accountID] ?? []
        // Remove deleted IDs first so local storage matches Wallet removals.
        let deletedSet = Set(changes.deleted)
        current.removeAll { deletedSet.contains($0.id) }

        for updated in changes.updated {
            if let index = current.firstIndex(where: { $0.id == updated.id }) {
                current[index] = updated
            }
        }

        current.append(contentsOf: changes.inserted)
        balances[accountID] = current
    }

    private func saveToken(_ token: FinanceStore.HistoryToken, for accountID: UUID) {
        let key = "\(tokenKey).\(accountID.uuidString)"
        if let data = try? JSONEncoder().encode(token) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    private func loadToken(for accountID: UUID) -> FinanceStore.HistoryToken? {
        let key = "\(tokenKey).\(accountID.uuidString)"
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(FinanceStore.HistoryToken.self, from: data)
    }

    private func clearToken(for accountID: UUID) {
        let key = "\(tokenKey).\(accountID.uuidString)"
        UserDefaults.standard.removeObject(forKey: key)
    }
}
```

## SwiftUI Integration

### Account List View

```swift
import SwiftUI
import FinanceKit

struct AccountListView: View {
    @State private var accounts: [Account] = []

    var body: some View {
        NavigationStack {
            List(accounts, id: \.id) { account in
                NavigationLink(value: account.id) {
                    VStack(alignment: .leading) {
                        Text(account.displayName).font(.headline)
                        Text(account.institutionName).font(.subheadline).foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Accounts")
            .navigationDestination(for: UUID.self) { TransactionListView(accountID: $0) }
            .task { await loadAccounts() }
        }
    }

    private func loadAccounts() async {
        guard FinanceStore.isDataAvailable(.financialData) else { return }
        do {
            let status = try await FinanceStore.shared.requestAuthorization()
            guard status == .authorized else { return }
            let query = AccountQuery(
                sortDescriptors: [SortDescriptor(\Account.displayName)],
                predicate: nil, limit: nil, offset: nil
            )
            accounts = try await FinanceStore.shared.accounts(query: query)
        } catch { }
    }
}
```

### Transaction List View

```swift
struct TransactionListView: View {
    let accountID: UUID
    @State private var transactions: [Transaction] = []

    var body: some View {
        List(transactions, id: \.id) { transaction in
            HStack {
                VStack(alignment: .leading) {
                    Text(transaction.transactionDescription)
                    if let merchant = transaction.merchantName {
                        Text(merchant).font(.caption).foregroundStyle(.secondary)
                    }
                }
                Spacer()
                VStack(alignment: .trailing) {
                    let amount = transaction.transactionAmount
                    let sign = transaction.creditDebitIndicator == .debit ? "-" : "+"
                    Text("\(sign)\(amount.amount.formatted(.currency(code: amount.currencyCode)))")
                        .font(.body.monospacedDigit())
                    Text(transaction.transactionDate, style: .date)
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
        }
        .navigationTitle("Transactions")
        .task {
            let predicate = #Predicate<Transaction> { $0.accountID == accountID }
            let query = TransactionQuery(
                sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
                predicate: predicate, limit: 100, offset: nil
            )
            transactions = (try? await FinanceStore.shared.transactions(query: query)) ?? []
        }
    }
}
```

## Background Delivery Extension Lifecycle

### Extension Setup

The background delivery extension requires:
1. A new extension target using the Background Delivery Extension template.
2. Both app and extension in the same App Group for shared data access.
3. The FinanceKit entitlement on both targets.
4. Financial-data authorization requested in the main app before enabling delivery; the extension inherits the app's authorization.

### Shared Data with App Groups

Use a shared container for data accessible to both the app and extension:

```swift
let sharedDefaults = UserDefaults(suiteName: "group.com.myapp.finance")

// In extension: sync latest data to shared container
func processNewTransactions() async {
    let store = FinanceStore.shared
    for account in try await fetchAccounts() {
        let history = store.transactionHistory(
            forAccountID: account.id, since: loadSharedToken(), isMonitoring: false
        )
        for try await changes in history {
            persistToSharedStore(changes)
            saveSharedToken(changes.newToken)
        }
    }
}
```

### Extension Lifecycle

- `didReceiveData(for:)` is called when the system detects changes matching the registered data types.
- Returning from `didReceiveData(for:)` closes the extension, so save essential work before returning.
- `willTerminate()` provides a cleanup opportunity before the system terminates the extension.
- `willTerminate()` may not be called for every system termination path.
- The extension has limited runtime. Perform only essential work (data sync, cache updates).
- Do not start long-running tasks or network requests that may not complete.

## Error Handling

### FinanceError Cases

```swift
do {
    let transactions = try await store.transactions(query: query)
} catch let error as FinanceError {
    switch error {
    case .dataRestricted(let dataType):
        handleRestriction(dataType)  // Wallet unavailable or MDM restricted
    case .historyTokenInvalid:
        discardSavedToken()          // Token points to compacted history
    case .unknown:
        logError(error)
    @unknown default:
        logError(error)
    }
}
```

### Graceful Degradation

```swift
@Observable
@MainActor
final class FinanceDataProvider {
    enum State {
        case loading, available([Transaction]), unavailable(reason: String)
    }

    private(set) var state: State = .loading

    func load(accountID: UUID) async {
        guard FinanceStore.isDataAvailable(.financialData) else {
            state = .unavailable(reason: "Financial data is not available on this device.")
            return
        }
        do {
            let status = try await FinanceStore.shared.authorizationStatus()
            guard status == .authorized else {
                state = .unavailable(reason: "Access to financial data has not been granted.")
                return
            }
            let predicate = #Predicate<Transaction> { $0.accountID == accountID }
            let query = TransactionQuery(
                sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
                predicate: predicate, limit: 50, offset: nil
            )
            state = .available(try await FinanceStore.shared.transactions(query: query))
        } catch let error as FinanceError {
            state = .unavailable(reason: error == .dataRestricted(.financialData)
                ? "Financial data is temporarily restricted."
                : "Unable to load financial data.")
        } catch {
            state = .unavailable(reason: "An unexpected error occurred.")
        }
    }
}
```
