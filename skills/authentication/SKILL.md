---
name: authentication
description: "Builds iOS authentication with AuthenticationServices and LocalAuthentication. Use for Sign in with Apple, passkeys/WebAuthn, credential state or revocation, OAuth/web sessions, Password AutoFill, identity-token server validation, and local biometric reauthentication."
---

# Authentication

Implement authentication flows on iOS using AuthenticationServices and LocalAuthentication, including Sign in with Apple, passkeys (WebAuthn), OAuth web sessions, Password AutoFill, and biometric verification. Targets Swift 6.3 / iOS 26+.

## Contents

- [Sign in with Apple](#sign-in-with-apple)
- [Passkeys (WebAuthn)](#passkeys-webauthn)
- [OAuth & ASWebAuthenticationSession](#oauth--aswebauthenticationsession)
- [Password AutoFill](#password-autofill)
- [Biometric Authentication (LocalAuthentication)](#biometric-authentication-localauthentication)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Sign in with Apple

Add the **Sign in with Apple** capability in Xcode.

In SwiftUI, use `SignInWithAppleButton`:

```swift
import SwiftUI
import AuthenticationServices

struct LoginView: View {
    var body: some View {
        SignInWithAppleButton(.signIn) { request in
            request.requestedScopes = [.fullName, .email]
        } onCompletion: { result in
            switch result {
            case .success(let authorization):
                if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
                    let userIdentifier = appleIDCredential.user
                    let identityToken = appleIDCredential.identityToken
                    // Forward identityToken to backend for JWT validation
                }
            case .failure(let error):
                // Handle authorization error
                break
            }
        }
        .signInWithAppleButtonStyle(.black)
        .frame(height: 50)
    }
}
```

Check credential state on app launch using `ASAuthorizationAppleIDProvider().getCredentialState(forUserID:)`.

## Passkeys (WebAuthn)

Authenticate without passwords using hardware-backed credentials synced via iCloud Keychain:

```swift
let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(relyingPartyIdentifier: "example.com")
let request = provider.createCredentialAssertionRequest(challenge: serverChallenge)

let controller = ASAuthorizationController(authorizationRequests: [request])
controller.delegate = self
controller.presentationContextProvider = self
controller.performRequests()
```

Configure Associated Domains with `webcredentials:example.com` and host `/.well-known/apple-app-site-association`.

## OAuth & ASWebAuthenticationSession

For third-party OAuth providers, use `ASWebAuthenticationSession`:

```swift
let session = ASWebAuthenticationSession(
    url: authURL,
    callbackURLScheme: "myapp"
) { callbackURL, error in
    guard let callbackURL, error == nil else { return }
    // Extract authorization code from callbackURL
}
session.presentationContextProvider = self
session.prefersEphemeralWebBrowserSession = false // true prevents shared cookie login
session.start()
```

## Password AutoFill

Support keychain password entry alongside passkeys via `ASAuthorizationPasswordProvider`:

```swift
let passwordRequest = ASAuthorizationPasswordProvider().createCredentialRequest()
let controller = ASAuthorizationController(authorizationRequests: [passkeyRequest, passwordRequest])
```

## Biometric Authentication (LocalAuthentication)

Verify device owner identity using Face ID / Touch ID:

```swift
import LocalAuthentication

func authenticateUser() async throws {
    let context = LAContext()
    var error: NSError?

    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
        throw AuthError.biometricsUnavailable
    }

    let success = try await context.evaluatePolicy(
        .deviceOwnerAuthenticationWithBiometrics,
        localizedReason: "Unlock your account"
    )
    guard success else { throw AuthError.failed }
}
```

## Common Mistakes

- **Assuming user profile data is returned on every sign-in**: Apple ID credentials return full name and email **only on the first authorization**. Persist them immediately.
- **Client-side token trust**: Always validate `identityToken` signatures against Apple's public keys on your server.
- **Missing webcredentials entitlement for passkeys**: Passkeys require `webcredentials:domain` in Associated Domains.
- **Not retaining ASWebAuthenticationSession**: The session must be retained in an instance variable or it deallocates before the callback fires.
- **Using biometrics without checking canEvaluatePolicy**: Calling `evaluatePolicy` without pre-checking triggers immediate runtime exceptions on unsupported hardware.

## Review Checklist

- [ ] Sign in with Apple capability added to project
- [ ] User full name and email persisted on first sign-in
- [ ] Identity tokens verified cryptographically on the server
- [ ] Credential state verified via `getCredentialState(forUserID:)` on launch
- [ ] Associated Domains configured with `webcredentials:` for passkeys
- [ ] `ASWebAuthenticationSession` instance retained until completion
- [ ] `NSFaceIDUsageDescription` included in Info.plist for biometric auth

## References

- Keychain & biometric patterns: [references/keychain-biometric.md](references/keychain-biometric.md)
- Passkey patterns: [references/passkeys.md](references/passkeys.md)
- [AuthenticationServices](https://sosumi.ai/documentation/authenticationservices)
- [ASAuthorizationAppleIDProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDCredential](https://sosumi.ai/documentation/authenticationservices/asauthorizationappleidcredential)
- [ASAuthorizationController](https://sosumi.ai/documentation/authenticationservices/asauthorizationcontroller)
- [ASWebAuthenticationSession](https://sosumi.ai/documentation/authenticationservices/aswebauthenticationsession)
- [Supporting passkeys](https://sosumi.ai/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPasswordProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationpasswordprovider)
- [SignInWithAppleButton](https://sosumi.ai/documentation/authenticationservices/signinwithapplebutton)
- [Implementing User Authentication with Sign in with Apple](https://sosumi.ai/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
