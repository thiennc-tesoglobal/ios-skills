# StoreKit Recovery and State Transitions

Use this reference for subscription state, refunds, revocations, Family
Sharing, Ask to Buy, and unfinished transactions. Keep one retained
`Transaction.updates` listener during app initialization.

## Entitlement and subscription state

`Transaction.currentEntitlements` contains verified current access for
non-consumables, active or grace-period auto-renewable subscriptions, and
non-renewing subscription transactions. It does not contain consumables or
refunded/revoked products. Rebuild the entitlement set so removed access
disappears, and apply the app/server expiration policy for non-renewing access.

Treat `.subscribed` and `.inGracePeriod` as entitled when product policy allows;
distinguish billing retry, expiration, and revocation in the UI. A local Boolean
is not purchase authority.

## Recovery paths

- Deliver durable, idempotent fulfillment before `transaction.finish()`.
- Leave a transaction unfinished when delivery fails; reconcile it through the
  lifetime listener or `Transaction.unfinished`.
- Use `AppStore.sync()` only from an explicit Restore Purchases action because
  it can prompt for authentication; derive ordinary reinstall access from
  current entitlements.
- Keep `.pending` visible until a verified update arrives; it is not a failure.
- Revoke access after refund/revocation and refresh Family Sharing ownership
  from verified transaction data.

## Ask to Buy and billing recovery

Test approval/decline, grace period, billing retry, and expiration as distinct
states. Never unlock from an unverified result, and do not silently turn a
billing retry into an immediate permanent expiration unless product policy says
so.

For complete refund sheets, renewal-state examples, and unfinished-transaction
recipes, read
[storekit-advanced-complete.md](storekit-advanced-complete.md#subscription-renewal-states).
