---
name: device-integrity
description: "Protects apps and APIs with DeviceCheck and App Attest. Use for per-device fraud state, App Attest key generation and attestation, request assertions, server verification, compromised-device signals, app authenticity, replay resistance, or sensitive endpoint protection."
---

# Device Integrity

Verify that requests to your server originate from genuine Apple devices running legitimate instances of your app. `DCDevice` provides per-device bits for persistent state (e.g., promo redemption), while `DCAppAttestService` provides cryptographic proof of app authenticity using Secure Enclave keys.

**Security Boundary:** App Attest proves client hardware/app integrity; it does not replace user authentication, TLS, authorization, or certificate pinning. Always enforce user authentication after App Attest verification succeeds.

## Contents

- [DCDevice (DeviceCheck)](#dcdevice-devicecheck)
- [DCAppAttestService (App Attest)](#dcappattestservice-app-attest)
- [Key Generation & Attestation Flow](#key-generation--attestation-flow)
- [Assertion Flow](#assertion-flow)
- [Error Handling & Key Lifecycle](#error-handling--key-lifecycle)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## DCDevice (DeviceCheck)

`DCDevice` generates ephemeral, single-use tokens sent to your backend, which communicates with Apple to read or update two per-device bits that persist across app reinstallation.

```swift
import DeviceCheck

func generateDeviceToken() async throws -> Data {
    guard DCDevice.current.isSupported else {
        throw DeviceIntegrityError.deviceCheckUnsupported
    }
    return try await DCDevice.current.generateToken()
}
```

Treat each token as strictly single-use. Generate a fresh token for every server interaction.

## DCAppAttestService (App Attest)

Available on iOS 14+. Validates app-instance integrity through three stages:
1. **Key Generation**: Create a hardware-backed key in the Secure Enclave once per user account/device.
2. **Attestation**: Apple certifies that the key belongs to a genuine app instance.
3. **Assertion**: Sign sensitive API requests using the attested key.

```swift
let service = DCAppAttestService.shared
guard service.isSupported else { throw DeviceIntegrityError.unsupported }
```

## Key Generation & Attestation Flow

Generate a key and request attestation from Apple before sending it to your backend:

```swift
// 1. Generate key once and persist keyId
let keyId = try await service.generateKey()

// 2. Fetch one-time challenge from server
let challenge = try await fetchAttestationChallenge()
let clientDataHash = Data(SHA256.hash(data: challenge))

// 3. Attest key with Apple and send to server
let attestation = try await service.attestKey(keyId, clientDataHash: clientDataHash)
try await sendAttestationToServer(keyId: keyId, attestation: attestation)
```

The server verifies the CBOR attestation object against Apple's App Attest root CA, checking that the certificate extension nonce matches `SHA256(authData || SHA256(challenge))`.

## Assertion Flow

Sign request payloads and server challenges with the attested key to prove ongoing legitimacy:

```swift
// clientData contains one-time challenge + request context
let clientDataHash = Data(SHA256.hash(data: clientData))
let assertion = try await service.generateAssertion(keyId, clientDataHash: clientDataHash)

var request = URLRequest(url: endpointURL)
request.setValue(assertion.base64EncodedString(), forHTTPHeaderField: "X-App-Attest-Assertion")
request.setValue(clientData.base64EncodedString(), forHTTPHeaderField: "X-App-Attest-Client-Data")
```

The server recomputes the hash, validates the assertion signature with the stored public key, and verifies the counter strictly increases to prevent replay attacks.

## Error Handling & Key Lifecycle

Handle `DCError` codes gracefully:

- **`.serverUnavailable`**: Retry attestation with the **same `keyId`** and the same `clientDataHash` using exponential backoff.
- **`.invalidKey`**: Discard the corrupted/rejected `keyId` and generate a fresh key before retrying.
- **`.featureUnsupported`**: Fall back to `DCDevice` token validation or server-side risk scoring.

## Common Mistakes

- **Generating a new key on every launch**: Generate once per user account on a device and persist the `keyId`.
- **Reusing DCDevice tokens**: Tokens are single-use; cached tokens will fail server validation.
- **Signing only the raw request body**: Assertion client data must include a one-time server challenge and request context for replay resistance.
- **Verifying the wrong attestation nonce on server**: Nonce must equal `SHA256(authData || SHA256(challenge))`, not `SHA256(challenge)` alone.
- **Mixing development and production environments**: Development keys fail in production. Configure `com.apple.developer.devicecheck.appattest-environment` entitlement appropriately.
- **Trusting attestation client-side**: Verification must strictly occur on your secure backend.

## Review Checklist

- [ ] `DCAppAttestService.isSupported` verified with fallback for unsupported devices/extensions
- [ ] Key generated once per account/device and `keyId` persisted in Keychain
- [ ] Server verifies attestation certificate chain, RP ID, counter, and composite nonce
- [ ] Assertions bind request context to a one-time challenge with monotonic counter validation
- [ ] `.serverUnavailable` retried with identical key/hash; `.invalidKey` regenerates key
- [ ] Protected endpoints still enforce normal user authentication and TLS
- [ ] Entitlements match target environment (`development` vs `production`)

## References

- Server verification algorithms, retry strategies, and integration manager: [references/device-integrity-patterns.md](references/device-integrity-patterns.md)
- [DeviceCheck framework](https://sosumi.ai/documentation/devicecheck)
- [DCDevice](https://sosumi.ai/documentation/devicecheck/dcdevice)
- [DCAppAttestService](https://sosumi.ai/documentation/devicecheck/dcappattestservice)
- [Establishing your app's integrity](https://sosumi.ai/documentation/devicecheck/establishing-your-app-s-integrity)
- [Validating apps that connect to your server](https://sosumi.ai/documentation/devicecheck/validating-apps-that-connect-to-your-server)
- [Attestation Object Validation Guide](https://sosumi.ai/documentation/devicecheck/attestation-object-validation-guide)
- [App Attest Environment Entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.devicecheck.appattest-environment)
