---
name: cryptokit
description: "Use Apple CryptoKit for Swift cryptographic primitives. Use when hashing with SHA-2 or SHA-3, generating HMACs, encrypting with AES-GCM or ChaChaPoly, signing with P256/P384/P521/Curve25519 or ML-DSA keys, performing ECDH, HPKE, ML-KEM, or X-Wing key exchange, using Secure Enclave CryptoKit keys, or migrating CommonCrypto code to CryptoKit."
---

# CryptoKit

Apple CryptoKit provides a Swift-native API for cryptographic operations:
hashing, message authentication, symmetric encryption, public-key signing,
key agreement, HPKE, quantum-secure key encapsulation/signing, and Secure
Enclave-backed keys. Most core primitives are available on iOS 13+; check
availability for HPKE (iOS 17+) and SHA-3 / post-quantum APIs (iOS 26+).
Prefer CryptoKit over CommonCrypto or raw Security framework APIs for new
cryptographic primitive code targeting Swift 6.3+.

## Workflow

1. Define the security property: hashing, authentication, authenticated encryption, signing, key agreement, or envelope encryption.
2. Choose a current CryptoKit primitive and verify platform/peer interoperability before designing storage formats.
3. Define key generation, persistence, rotation, access control, serialization, and deletion as one lifecycle.
4. Bind context with authenticated data or a KDF and make nonce/sequence ownership impossible to reuse accidentally.
5. Verify round trips, tampering, wrong keys, malformed inputs, rotation, Secure Enclave availability, and cross-platform vectors.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for hashes, HMAC, AEAD, signatures, key agreement, HPKE, post-quantum APIs, and Secure Enclave usage.
- Read [extended CryptoKit patterns](references/cryptokit-patterns.md) for serialization, Keychain integration, AES key wrapping, insecure legacy migration, and interoperability recipes.

## Core Decisions

- Use authenticated encryption; never reuse a nonce with the same key.
- Derive keys from shared secrets instead of using raw agreement output.
- Treat authentication/tag failures as hard failures without partial plaintext use.
- Store long-lived secrets in Keychain or Secure Enclave-backed keys, not preferences.

## Common Mistakes

### 1. Using the shared secret directly as a key

```swift
// DON'T
let badKey = sharedSecret.withUnsafeBytes { bytes in
    SymmetricKey(data: Data(bytes))
}

// DO -- derive with HKDF
let goodKey = sharedSecret.hkdfDerivedSymmetricKey(
    using: SHA256.self,
    salt: salt,
    sharedInfo: info,
    outputByteCount: 32
)
```

### 2. Reusing nonces

```swift
// DON'T -- hardcoded nonce
let nonce = try AES.GCM.Nonce(data: Data(repeating: 0, count: 12))
let box = try AES.GCM.seal(data, using: key, nonce: nonce)

// DO -- let CryptoKit generate a random nonce (default behavior)
let box = try AES.GCM.seal(data, using: key)
```

### 3. Ignoring authentication tag verification

```swift
// DON'T -- manually strip tag and decrypt
// DO -- always use AES.GCM.open() or ChaChaPoly.open()
// which verifies the tag automatically
```

### 4. Using Insecure hashes for security

```swift
// DON'T -- MD5/SHA1 for integrity or security
import CryptoKit
let bad = Insecure.MD5.hash(data: data)

// DO -- use SHA256 or stronger
let good = SHA256.hash(data: data)
```

`Insecure.MD5` and `Insecure.SHA1` exist only for legacy compatibility
(checksum verification, protocol interop). Never use them for new
security-sensitive operations.

### 5. Storing symmetric keys in UserDefaults

```swift
// DON'T
UserDefaults.standard.set(rawKeyData, forKey: "encryptionKey")

// DO -- store in Keychain
// See references/cryptokit-patterns.md for Keychain storage patterns
```

### 6. Not checking Secure Enclave availability

```swift
// DON'T -- crash on simulator or unsupported hardware
let key = try SecureEnclave.P256.Signing.PrivateKey()

// DO
guard SecureEnclave.isAvailable else { /* fallback */ }
let key = try SecureEnclave.P256.Signing.PrivateKey()
```

## Review Checklist

- [ ] Using CryptoKit, not CommonCrypto or raw Security framework
- [ ] SHA256+ for hashing; no MD5/SHA1 for security purposes
- [ ] HMAC verification uses `isValidAuthenticationCode` (constant-time)
- [ ] AES-GCM or ChaChaPoly for symmetric encryption; 256-bit keys
- [ ] Nonces are random (default) -- not hardcoded or reused
- [ ] Authenticated data (AAD) used where metadata needs integrity
- [ ] SharedSecret derived via HKDF, not used directly
- [ ] sharedInfo parameter is non-empty and context-specific
- [ ] HPKE used instead of custom ECDH+HKDF+AEAD for recipient public-key encryption on iOS 17+
- [ ] SHA-3 and post-quantum APIs guarded with iOS 26+ availability
- [ ] Secure Enclave availability checked before use
- [ ] Secure Enclave key `dataRepresentation` stored in Keychain
- [ ] Private keys not logged, printed, or serialized unnecessarily
- [ ] Symmetric keys stored in Keychain, not UserDefaults or files
- [ ] Encryption export compliance considered (`ITSAppUsesNonExemptEncryption`)

## References

- Extended patterns (key serialization, Insecure module, Keychain integration, AES key wrapping, HPKE): [references/cryptokit-patterns.md](references/cryptokit-patterns.md)
- Apple documentation: [CryptoKit](https://sosumi.ai/documentation/cryptokit)
- Apple documentation: [HPKE](https://sosumi.ai/documentation/cryptokit/hpke)
- Apple documentation: [Quantum-secure workflows](https://sosumi.ai/documentation/cryptokit/enhancing-your-app-s-privacy-and-security-with-quantum-secure-workflows)
- Apple sample: [Performing Common Cryptographic Operations](https://sosumi.ai/documentation/cryptokit/performing-common-cryptographic-operations)
- Apple sample: [Storing CryptoKit Keys in the Keychain](https://sosumi.ai/documentation/cryptokit/storing-cryptokit-keys-in-the-keychain)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
