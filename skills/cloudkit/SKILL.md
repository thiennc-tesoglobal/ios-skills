---
name: cloudkit
description: "Builds or reviews CloudKit and iCloud synchronization with records, queries, subscriptions, CKSyncEngine, shares, SwiftData CloudKit configuration, key-value storage, or iCloud Drive. Use for sync architecture, conflicts, account state, retries, quota, and offline behavior."
---

# CloudKit

Sync data across devices using CloudKit, iCloud key-value storage, and iCloud
Drive. Covers container setup, record CRUD, queries, subscriptions, CKSyncEngine,
SwiftData integration, conflict resolution, and error handling.

## Workflow

1. Choose container, public/private/shared database, record ownership, zone strategy, and offline expectations.
2. Define stable record types, identifiers, references, assets, and conflict fields before writing CRUD code.
3. Use queries for bounded reads and `CKSyncEngine` or change tokens for durable incremental synchronization.
4. Handle account changes, partial failures, rate limits, retries, conflicts, deletions, and local persistence explicitly.
5. Verify offline edits, concurrent devices, account switching, quota, schema deployment, sharing, and production environment behavior.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for containers, records, queries, subscriptions, `CKSyncEngine`, SwiftData, key-value storage, iCloud Drive, and error handling.
- Read [extended CloudKit patterns](references/cloudkit-patterns.md) for change tokens, shares, assets, batch operations, custom zones, and Dashboard procedures.

## Core Decisions

- Treat record saves as conflict-prone distributed writes, not local CRUD.
- Persist sync state/change tokens and recover from token expiration.
- Inspect per-item errors in partial failures and honor retry guidance.
- Keep SwiftData CloudKit configuration constraints separate from direct CloudKit workflows.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Syncing without an account gate | Check `accountStatus()` and model `.noAccount` as a user-visible state. |
| Personal data in the public database | Use private scope for user data; public scope is app-wide content. |
| Timer polling | Use database subscriptions or `CKSyncEngine`. |
| Immediate retry after throttling | Respect `retryAfterSeconds` and preserve pending work. |
| Assuming the engine resolves conflicts | Three-way merge `failedRecordSaves`, then reschedule the save. |
| Starting every fetch with a nil token | Persist tokens/state; reset only on the documented expiry path. |

## Review Checklist

- [ ] iCloud + CloudKit capability enabled in Signing & Capabilities
- [ ] Account status checked before sync; `.noAccount` handled gracefully
- [ ] Private database used for user data; public only for shared content
- [ ] Custom record zones created in private DB; shared DB zones discovered from shares
- [ ] `CKError.serverRecordChanged` handled with three-way merge into `serverRecord`
- [ ] Network failures queued for retry; `retryAfterSeconds` respected
- [ ] `CKDatabaseSubscription` or `CKSyncEngine` used for push-based sync; Remote notifications enabled for background delivery
- [ ] Change tokens persisted to disk; `changeTokenExpired` resets and refetches
- [ ] `.partialFailure` errors inspected per-item via `partialErrorsByItemID`
- [ ] `.userDeletedZone` handled by recreating zone and resyncing
- [ ] SwiftData CloudKit review reports model compatibility and schema rollout: initialized/verified development schema, promoted before release, and additive-only production changes
- [ ] `NSUbiquitousKeyValueStore.didChangeExternallyNotification` observed
- [ ] Encryption review says `CKRecord.Reference` cannot use `encryptedValues` because CloudKit needs it server-side; no query/sort on encrypted fields; `CKAsset` is encrypted by default
- [ ] `CKSyncEngine` state serialization persisted across launches (iOS 17+)

## References

- See [references/cloudkit-patterns.md](references/cloudkit-patterns.md) for incremental sync, CKShare, zones, CKAsset storage, batch operations, and Dashboard usage.
- [CloudKit Framework](https://sosumi.ai/documentation/cloudkit)
- [CKContainer](https://sosumi.ai/documentation/cloudkit/ckcontainer)
- [CKRecord](https://sosumi.ai/documentation/cloudkit/ckrecord)
- [CKQuery](https://sosumi.ai/documentation/cloudkit/ckquery)
- [CKSubscription](https://sosumi.ai/documentation/cloudkit/cksubscription)
- [CKSyncEngine](https://sosumi.ai/documentation/cloudkit/cksyncengine)
- [CKShare](https://sosumi.ai/documentation/cloudkit/ckshare)
- [CKError](https://sosumi.ai/documentation/cloudkit/ckerror)
- [NSUbiquitousKeyValueStore](https://sosumi.ai/documentation/foundation/nsubiquitouskeyvaluestore)
- [SwiftData CloudKit sync](https://sosumi.ai/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
