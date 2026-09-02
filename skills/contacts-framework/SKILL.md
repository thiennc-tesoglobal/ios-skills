---
name: contacts-framework
description: "Read, create, update, and pick contacts using the Contacts and ContactsUI frameworks. Use when fetching contact data, saving new contacts, wrapping CNContactPickerViewController in SwiftUI, handling contact permissions, or working with CNContactStore fetch and save requests."
---

# Contacts Framework

Use `CNContactStore`, `CNSaveRequest`, and ContactsUI to fetch, mutate, or let
the user select contacts. Prefer the system picker when full address-book access
is unnecessary.

## Contents

- [Choose the access model](#choose-the-access-model)
- [Setup and authorization](#setup-and-authorization)
- [Fetch invariants](#fetch-invariants)
- [Mutation invariants](#mutation-invariants)
- [Concurrency and cache invalidation](#concurrency-and-cache-invalidation)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Choose the access model

| Need | API |
|---|---|
| User chooses one or more contacts without broad permission | `CNContactPickerViewController` |
| App reads or writes its authorized contact set | `CNContactStore` |
| User expands an iOS 18+ limited set | `ContactAccessButton` or `contactAccessPicker` |
| Import/export or sharing | `CNContactVCardSerialization` |

Read [Contacts extended patterns](references/contacts-patterns.md) for a complete
observable manager, SwiftUI lists, single/multi-select picker wrappers,
email-only selection, optimized search, vCard import/export, groups, and change
notification handling.

## Setup and authorization

- Add `NSContactsUsageDescription` before direct Contacts API access; missing it
  causes termination.
- Ordinary access needs no entitlement. Reading or writing `CNContact.note`
  requires the Apple-approved `com.apple.developer.contacts.notes` entitlement.
- The system contact picker does not require broad Contacts authorization; the
  app receives only selected data.

Treat authorization states explicitly:

| Status | Behavior |
|---|---|
| `.notDetermined` | Request only from a user-understood action |
| `.authorized` | Full access |
| `.limited` | Usable, but only for granted or app-created contacts |
| `.denied` | Explain the feature and route to Settings when appropriate |
| `.restricted` | Disable the operation; do not repeatedly prompt |

## Fetch invariants

Only fetch keys the caller will access. Reading an unfetched property raises
`CNContactPropertyNotFetchedException`.

```swift
@preconcurrency import Contacts

let keys: [CNKeyDescriptor] = [
    CNContactFormatter.descriptorForRequiredKeys(for: .fullName),
    CNContactPhoneNumbersKey as CNKeyDescriptor
]

let request = CNContactFetchRequest(keysToFetch: keys)
try store.enumerateContacts(with: request) { contact, stop in
    consume(contact)
}
```

Use `unifiedContacts(matching:keysToFetch:)` for predicate queries,
`unifiedContact(withIdentifier:keysToFetch:)` for known identifiers, and
enumeration for the authorized address book. Avoid full-resolution image data
unless the UI truly requires it. For large caches, fetch identifiers first and
hydrate details in bounded batches.

## Mutation invariants

- Create with `CNMutableContact` and `CNSaveRequest.add`.
- Update or delete by fetching the required properties, creating
  `mutableCopy()`, then adding the operation to a fresh save request.
- `store.execute(request)` returning without throwing is the success boundary.
  Advance app state or clear drafts only afterward.
- On failure, preserve the user's intent, surface the error, correct known
  authorization/container/input causes, refetch stale contacts when possible,
  and construct a new request. Do not blindly replay a destructive request.
- Serialize overlapping saves and never mutate a request while `execute` uses it.

```swift
let mutable = CNMutableContact()
mutable.givenName = "Taylor"

let request = CNSaveRequest()
request.add(mutable, toContainerWithIdentifier: nil)
try store.execute(request)
```

## Concurrency and cache invalidation

Enumeration is I/O-heavy; keep it off the main actor. With strict concurrency,
use `@preconcurrency import Contacts` only at the framework boundary or map
`CNContact` values into app-owned `Sendable` models before crossing actors.

Observe `.CNContactStoreDidChange`, invalidate cached `CNContact` objects, and
refetch the authorized set. Reuse one store instead of constructing stores per
row or query.

## Common mistakes

- Requesting full access when a picker satisfies the feature.
- Treating `.limited` as denial or assuming it exposes the full address book.
- Fetching every key, especially full image data.
- Accessing a property not included in `keysToFetch`.
- Attempting to mutate immutable `CNContact` directly.
- Updating UI/cache before `execute` succeeds.
- Enumerating contacts on the main actor or retaining stale contact objects.

## Review checklist

- [ ] Usage description and note entitlement requirements are correct.
- [ ] Picker is preferred when broad access is unnecessary.
- [ ] Every authorization state, including `.limited`, has product behavior.
- [ ] Fetch descriptors include exactly the accessed properties.
- [ ] Name formatting uses the formatter's required-key descriptor.
- [ ] Create/update/delete use fresh `CNSaveRequest` values and mutable contacts.
- [ ] App state changes only after a successful save; failures preserve intent.
- [ ] Heavy reads run off the main actor and cross actors safely.
- [ ] Store-change notification invalidates and refetches caches.
- [ ] One long-lived `CNContactStore` is reused.

## References

- [Contacts extended patterns](references/contacts-patterns.md)
- [Contacts documentation](https://sosumi.ai/documentation/contacts)
- [CNContactStore](https://sosumi.ai/documentation/contacts/cncontactstore)
- [CNSaveRequest](https://sosumi.ai/documentation/contacts/cnsaverequest)
- [CNContactPickerViewController](https://sosumi.ai/documentation/contactsui/cncontactpickerviewcontroller)
- [Contact access controls](https://sosumi.ai/documentation/contactsui/contactaccessbutton)
