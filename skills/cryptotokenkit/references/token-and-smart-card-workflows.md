# Token and Smart-Card Workflows

## Contents

- [macOS token extension](#macos-token-extension)
- [Token session and PIN authentication](#token-session-and-pin-authentication)
- [Smart-card communication](#smart-card-communication)
- [NFC smart-card session](#nfc-smart-card-session)
- [Token-backed Keychain queries](#token-backed-keychain-queries)
- [Certificate authentication requirements](#certificate-authentication-requirements)
- [Token watching](#token-watching)

## macOS token extension

A smart-card token extension uses a `TKSmartCardTokenDriver`,
`TKSmartCardToken`, and `TKSmartCardTokenSession`. The token reads hardware
objects and fills its Keychain representation; the session performs operations.

```swift
import CryptoTokenKit

final class TokenDriver: TKSmartCardTokenDriver,
                         TKSmartCardTokenDriverDelegate {
    func tokenDriver(
        _ driver: TKSmartCardTokenDriver,
        createTokenFor smartCard: TKSmartCard,
        aid: Data?
    ) throws -> TKSmartCardToken {
        try Token(
            smartCard: smartCard,
            aid: aid,
            instanceID: "com.example.token:\(smartCard.slot.name)",
            tokenDriver: driver
        )
    }
}
```

The extension Info.plist must contain:

```text
NSExtension
  NSExtensionAttributes
    com.apple.ctk.driver-class = $(PRODUCT_MODULE_NAME).TokenDriver
  NSExtensionPointIdentifier = com.apple.ctk-tokens
```

Populate certificate and key objects with stable object IDs. Set `canSign`,
`canDecrypt`, and `isSuitableForLogin` only when the real hardware and
certificate support those uses. Register the installed extension by launching
its host as `_securityagent` when the deployment workflow requires it:

```sh
sudo -u _securityagent /Applications/TokenHost.app/Contents/MacOS/TokenHost
```

## Token session and PIN authentication

The session delegate must gate each operation by the exact algorithm:

```swift
final class TokenSession: TKSmartCardTokenSession, TKTokenSessionDelegate {
    func tokenSession(
        _ session: TKTokenSession,
        supports operation: TKTokenOperation,
        keyObjectID: TKToken.ObjectID,
        algorithm: TKTokenKeyAlgorithm
    ) -> Bool {
        switch operation {
        case .signData:
            algorithm.isAlgorithm(.rsaSignatureDigestPKCS1v15SHA256)
                || algorithm.isAlgorithm(.ecdsaSignatureDigestX962SHA256)
        case .decryptData:
            algorithm.isAlgorithm(.rsaEncryptionOAEPSHA256)
        case .performKeyExchange:
            algorithm.isAlgorithm(.ecdhKeyExchangeStandard)
        default:
            false
        }
    }
}
```

Perform signing/decryption inside `smartCard.withSession`. For PIN entry, return
a `TKTokenSmartCardPINAuthOperation` whose charset, lengths, APDU template, and
byte offset match the card specification. Do not store PINs in token state.

## Smart-card communication

Discover slots through the optional manager:

```swift
guard let manager = TKSmartCardSlotManager.default else { return }

for name in manager.slotNames {
    manager.getSlot(withName: name) { slot in
        guard let slot,
              slot.state == .validCard,
              let card = slot.makeSmartCard() else { return }
        communicate(with: card)
    }
}
```

Use `send(ins:p1:p2:data:le:)` for structured APDUs and check the returned
status word:

```swift
func selectApplication(card: TKSmartCard, aid: Data) throws {
    try card.withSession {
        let (statusWord, _) = try card.send(
            ins: 0xA4,
            p1: 0x04,
            p2: 0x00,
            data: aid,
            le: nil
        )
        guard statusWord == 0x9000 else {
            throw TKError(.communicationError)
        }
    }
}
```

Use raw `transmit(_:reply:)` only when structured `send` cannot represent the
command. Pair manual session start/end and preserve APDU status details in a
domain error. Extended response chaining and TLV parsing are in
[CryptoTokenKit extended patterns](cryptotokenkit-patterns.md).

## NFC smart-card session

iOS/iPadOS 26+ can create a temporary NFC slot:

```swift
@available(iOS 26.0, iPadOS 26.0, *)
func readContactlessCard() {
    guard let manager = TKSmartCardSlotManager.default,
          manager.isNFCSupported() else { return }

    manager.createNFCSlot(message: "Hold card near iPhone") { session, error in
        guard let session else {
            handleNFCError(error)
            return
        }
        defer { session.end() }

        guard let slotName = session.slotName,
              let slot = manager.slotNamed(slotName),
              let card = slot.makeSmartCard() else { return }
        communicate(with: card)
    }
}
```

Never retain the temporary slot beyond its session. Cancellation and background
transitions must end cleanly.

## Token-backed Keychain queries

Token items appear through Security.framework while the token is present:

```swift
import Security

func tokenKey(tokenID: String) throws -> SecKey {
    let query: [String: Any] = [
        kSecClass as String: kSecClassKey,
        kSecAttrTokenID as String: tokenID,
        kSecReturnRef as String: true
    ]
    var result: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess, let key = result else {
        throw TKError(.objectNotFound)
    }
    return key as! SecKey
}
```

Use `kSecReturnPersistentRef` when a stable reference is required, but treat
`errSecItemNotFound` after token removal as expected recovery. Query
certificates with `kSecClassCertificate` and validate trust according to the
deployment policy.

## Certificate authentication requirements

For user login, the token needs a signing key supported by the system, such as
EC X9.62 digest signing or RSA PSS/PKCS#1 v1.5 digest signing. Keychain unlock
requires either a 256-bit EC key supporting standard ECDH or a supported
2048/3072/4096-bit RSA key supporting OAEP SHA-256 decryption.

macOS smart-card policy is configured in `com.apple.security.smartcard` through
MDM or system configuration. Treat `allowSmartCard`, certificate trust level,
pairing, and enforcement as deployment policy—not defaults to silently change.

## Token watching

Retain one `TKTokenWatcher`, inspect its initial `tokenIDs`, install an insertion
handler, and attach removal handlers for observed tokens. Invalidate app caches
and persistent references when removal occurs. Use slot monitoring from the
extended reference when reader-level state matters independently of token IDs.

## Apple documentation

- [TKTokenDriver](https://sosumi.ai/documentation/cryptotokenkit/tktokendriver)
- [TKTokenSession](https://sosumi.ai/documentation/cryptotokenkit/tktokensession)
- [TKSmartCard](https://sosumi.ai/documentation/cryptotokenkit/tksmartcard)
- [TKSmartCardSlotManager](https://sosumi.ai/documentation/cryptotokenkit/tksmartcardslotmanager)
- [TKSmartCardSlotNFCSession](https://sosumi.ai/documentation/cryptotokenkit/tksmartcardslotnfcsession)
- [TKTokenWatcher](https://sosumi.ai/documentation/cryptotokenkit/tktokenwatcher)
