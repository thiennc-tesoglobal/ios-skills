---
name: cryptotokenkit
description: "Builds CryptoTokenKit security-token and smart-card integrations. Use for token-driver extensions, token sessions, TKSmartCard communication, NFC smart-card sessions, token-backed Keychain queries, token watching, certificate authentication, APDU handling, or PIN workflows."
---

# CryptoTokenKit

Use CryptoTokenKit for token-driver extensions, smart-card sessions,
token-backed Keychain items, certificate authentication, and iOS/iPadOS 26+
NFC smart-card access.

API presence is not an access guarantee: extension points, entitlements,
hardware, and runtime support all matter. The login/keychain-unlock token
extension flow is macOS-specific, `TKSmartCardSlotManager.default` is optional,
and NFC smart-card slot creation requires iOS/iPadOS 26+.

## Contents

- [Choose the workflow](#choose-the-workflow)
- [Architecture and boundaries](#architecture-and-boundaries)
- [Core invariants](#core-invariants)
- [Platform and capability checks](#platform-and-capability-checks)
- [Error handling](#error-handling)
- [Common mistakes](#common-mistakes)
- [Review checklist](#review-checklist)
- [References](#references)

## Choose the workflow

- For the macOS driver/token/session classes, extension Info.plist, PIN auth,
  low-level APDU sessions, token-backed Keychain queries, NFC slot lifecycle,
  and certificate requirements, read
  [Token and smart-card workflows](references/token-and-smart-card-workflows.md).
- For PIV selection and signing, BER/compact TLV parsing, generic token drivers,
  command chaining, large responses, secure PIN operations, configuration,
  slot monitoring, and registration, read
  [CryptoTokenKit extended patterns](references/cryptotokenkit-patterns.md).

## Architecture and boundaries

CryptoTokenKit has three distinct modes:

1. A macOS smart-card token extension exposes hardware-backed keys and
   certificates to login and Keychain services.
2. An app queries token-backed items through Security.framework while the token
   is present.
3. An iOS/iPadOS 26+ app creates a temporary NFC smart-card slot and communicates
   through `TKSmartCard`.

Own token/smart-card sessions, token-backed items, APDUs, PIN operations, and
smart-card certificate authentication here. Route passkeys/WebAuthn and account
sign-in to `authentication`; route CryptoKit primitives, Secure Enclave,
ordinary Keychain architecture, pinning, and trust policy to `swift-security`.

| Type | Role | Important constraint |
|---|---|---|
| `TKTokenDriver`, `TKToken`, `TKTokenSession` | Driver/token/session primitives | Extension behavior depends on platform and extension point |
| `TKSmartCardTokenDriver` | Smart-card driver entry point | System login integration is a macOS extension flow |
| `TKSmartCard`, `TKSmartCardSlotManager` | Reader discovery and APDU transport | Default manager may be `nil` |
| `TKTokenWatcher` | Token insertion/removal | Retain it for the monitoring lifetime |
| `TKSmartCardSlotNFCSession` | Temporary NFC-backed slot | iOS/iPadOS 26+; always end the session |
| `TKSmartCardTokenRegistrationManager` | NFC token registration | iOS/iPadOS 26+ |

## Core invariants

- A token extension declares `com.apple.ctk-tokens` and the exact
  `com.apple.ctk.driver-class`; the host app is only its delivery vehicle.
- Populate `TKTokenKeychainContents` with stable, matching object IDs.
  `TKTokenKeychainKey` capabilities must reflect the hardware.
- `TKTokenSessionDelegate.supports` returns `true` only for algorithms and
  operations the token actually implements.
- Wrap structured `send` calls in `withSession`; for raw `transmit`, pair
  `beginSession` and `endSession` on every path.
- Check every APDU status word. Transport success does not mean command success.
- Verify token presence before queries. Persistent references become invalid
  after removal and must handle `errSecItemNotFound`.
- Configure `TKTokenSmartCardPINAuthOperation` from the real card format and
  APDU layout; never log or retain PIN bytes.
- End every `TKSmartCardSlotNFCSession`, including error and cancellation paths.

## Platform and capability checks

```swift
import CryptoTokenKit

guard let manager = TKSmartCardSlotManager.default else {
    // Missing entitlement/access, unsupported runtime, or no smart-card service.
    return
}
```

On iOS/iPadOS 26+, also require `manager.isNFCSupported()` before creating an
NFC slot. Keep macOS configuration and system-authentication guidance outside
iOS-only branches. Do not force unwrap a manager, slot, card, certificate, or
keychain item obtained from hardware.

## Error handling

Handle `TKError` according to recovery semantics:

| Error | Expected response |
|---|---|
| `.canceledByUser` | Stop quietly or restore prior UI state |
| `.authenticationFailed` / `.authenticationNeeded` | Present bounded retry or authentication UI |
| `.tokenNotFound` / `.objectNotFound` | Ask for reinsertion or refresh token contents |
| `.communicationError` | End the session and offer a fresh attempt |
| `.corruptedData` | Reject the response; do not parse or trust partial data |
| `.notImplemented` | Disable the unsupported operation |

Preserve smart-card-specific status information in app errors without exposing
secrets. Avoid blind retries of PIN or destructive card commands.

## Common mistakes

- Treating framework availability as proof that the manager, reader, or NFC
  capability exists.
- Sending APDUs outside a managed session or ignoring status words.
- Returning blanket algorithm support from the token-session delegate.
- Querying stale token references without observing insertion/removal.
- Declaring signing/decryption/login capabilities not supported by hardware.
- Reusing macOS extension setup in an iOS app target.

## Review checklist

- [ ] Exact platform, extension point, entitlement, and hardware requirements are documented.
- [ ] Optional manager/slot/card objects are guarded.
- [ ] Extension point and driver class are correct for macOS token extensions.
- [ ] Object IDs and key capabilities match real token contents.
- [ ] Delegate support is algorithm-specific.
- [ ] Every APDU runs in a session and validates its status word.
- [ ] PIN flow uses the card's real format and has bounded retry behavior.
- [ ] Token watcher lifetime covers every query that depends on presence.
- [ ] Persistent-reference invalidation is handled.
- [ ] NFC support is checked and every NFC session ends.

## References

- [Token and smart-card workflows](references/token-and-smart-card-workflows.md)
- [CryptoTokenKit extended patterns](references/cryptotokenkit-patterns.md)
- [CryptoTokenKit documentation](https://sosumi.ai/documentation/cryptotokenkit)
- [Smart-card entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.security.smartcard)
