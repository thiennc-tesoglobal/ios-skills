---
name: adattributionkit
description: "Measure ad effectiveness with privacy-preserving attribution using AdAttributionKit. Use when registering ad impressions, handling attribution postbacks, updating conversion values, implementing re-engagement attribution, configuring publisher or advertiser apps, or replacing SKAdNetwork with AdAttributionKit for ad measurement."
---

# AdAttributionKit

Privacy-preserving ad attribution for iOS 17.4+. AdAttributionKit enables ad networks and advertisers to measure app installs and re-engagements across the App Store and alternative marketplaces without disclosing user-level identity.

Three distinct roles participate in attribution:
- **Ad Network**: Signs ad impressions with JWS and receives cryptographically validated postbacks.
- **Publisher App**: Hosts and renders ads using `UIEventAttributionView` or StoreKit overlays.
- **Advertised App**: Registers conversions, updates conversion values, and receives copy postbacks.

## Contents

- [Privacy Model & Attribution Arbitration](#privacy-model--attribution-arbitration)
- [Publisher App Configuration](#publisher-app-configuration)
- [Advertiser App Setup](#advertiser-app-setup)
- [Impressions & StoreKit Overlays](#impressions--storekit-overlays)
- [Conversion Values & Postbacks](#conversion-values--postbacks)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Privacy Model & Attribution Arbitration

- **Crowd Anonymity Tiers (0-3)**: The system restricts postback granularity based on crowd volume. Low crowd tiers return coarse conversions and shorter source IDs; Tier 3 returns full 4-digit source IDs and fine values.
- **Delayed Postbacks**: Postbacks are queued and dispatched randomly (24-48h for the first conversion window; 24-144h for second/third windows).
- **Interoperability & Arbitration**: AdAttributionKit and SKAdNetwork impressions are evaluated together. Exactly one impression wins: click-through beats view-through; within the same interaction type, the most recent impression wins.

## Publisher App Configuration

Declare supported ad networks in `Info.plist` with lowercase identifiers:

```xml
<key>AdNetworkIdentifiers</key>
<array>
    <string>example123.adattributionkit</string>
    <string>partner456.skadnetwork</string>
</array>
```

For custom click-through ads, overlay a `UIEventAttributionView` directly above the tappable surface:

```swift
import UIKit

let attributionView = UIEventAttributionView()
attributionView.frame = adContainer.bounds
attributionView.isUserInteractionEnabled = true
adContainer.addSubview(attributionView)
```

## Advertiser App Setup

Opt in to receive copies of winning conversion and re-engagement postbacks at your HTTPS endpoint:

```xml
<key>AdAttributionKit</key>
<dict>
    <key>AttributionCopyEndpoint</key>
    <string>https://example.com</string>
    <key>OptInForReengagementPostbackCopies</key>
    <true/>
</dict>
```

The system sends postbacks to `https://example.com/.well-known/appattribution/report-attribution/`.

## Impressions & StoreKit Overlays

Register signed JWS impressions provided by the ad network:

```swift
import AdAttributionKit
import StoreKit

// Check device availability
guard AppImpression.isSupported else { return }

let impression = try await AppImpression(compactJWS: signedJWS)

// Option A: Custom view-through or click-through
try await impression.handleView()
try await impression.handleTap() // Must be called within 15 minutes of creation

// Option B: StoreKit overlay automatic tracking
let config = SKOverlay.AppConfiguration(appIdentifier: "123456789", position: .bottom)
config.appImpression = impression
```

## Conversion Values & Postbacks

Update conversion values on launch and key milestone completions:

```swift
// Initial window start
try await Postback.updateConversionValue(0, lockPostback: false)

// Milestone update with coarse tier and early lock
try await Postback.updateConversionValue(
    42,
    coarseConversionValue: .high,
    lockPostback: true // Finalizes window early to accelerate postback receipt
)
```

## Common Mistakes

- **Uppercase AdNetworkIdentifiers**: Ad network IDs in Info.plist must be strictly lowercase.
- **Missing UIEventAttributionView**: Custom click-through ads without an overlying `UIEventAttributionView` fail attribution registration.
- **Delayed initial conversion call**: Failing to call `Postback.updateConversionValue` on initial launch prevents the conversion window from starting.
- **Missing 15-minute click window**: `impression.handleTap()` must be invoked within 15 minutes of `AppImpression` initialization.
- **Treating eligibility and conversion windows as identical**: Attribution eligibility windows (interaction to install) are separate from postback conversion windows (install to measurement).

## Review Checklist

- [ ] All ad network identifiers in `Info.plist` are lowercase
- [ ] `UIEventAttributionView` covers the interactive ad area without touch interception
- [ ] `AttributionCopyEndpoint` configured with valid HTTPS and `.well-known` route
- [ ] Initial conversion value registered promptly on app first launch
- [ ] High-value actions lock postback early when subsequent conversions are not expected
- [ ] Cryptographic JWS signatures verified before counting conversions server-side

## References

- Postback verification, server handling, testing, and SKAdNetwork migration: [references/adattributionkit-patterns.md](references/adattributionkit-patterns.md)
- [Apple: AdAttributionKit](https://sosumi.ai/documentation/adattributionkit)
- [Apple: Presenting ads in your app](https://sosumi.ai/documentation/adattributionkit/presenting-ads-in-your-app)
- [Apple: Receiving ad attributions and postbacks](https://sosumi.ai/documentation/adattributionkit/receiving-ad-attributions-and-postbacks)
- [Apple: Verifying a postback](https://sosumi.ai/documentation/adattributionkit/verifying-a-postback)
- [Apple: SKAdNetwork interoperability](https://sosumi.ai/documentation/adattributionkit/adattributionkit-skadnetwork-interoperability)
