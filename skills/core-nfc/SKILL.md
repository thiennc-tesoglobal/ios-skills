---
name: core-nfc
description: "Read and write NFC tags using CoreNFC. Use when scanning NDEF tags, reading ISO7816/ISO15693/FeliCa/MIFARE tags, writing NDEF messages, handling NFC session lifecycle, configuring NFC entitlements, or implementing background tag reading in iOS apps."
---

# CoreNFC

Read and write NFC tags on iPhone using CoreNFC. Supports NDEF tag reader sessions, native ISO 7816/15693/FeliCa/MIFARE tag communication, and background tag reading.

## Contents

- [Setup & Entitlements](#setup--entitlements)
- [NDEF Reader Session](#ndef-reader-session)
- [Tag Reader Session & Writing](#tag-reader-session--writing)
- [NDEF Message Construction](#ndef-message-construction)
- [Background Tag Reading](#background-tag-reading)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Entitlements

1. Enable **Near Field Communication Tag Reading** capability in Xcode.
2. Add `NFCReaderUsageDescription` to Info.plist.
3. Configure the entitlement `com.apple.developer.nfc.readersession.formats` with array value `["TAG"]` (do not use legacy `NDEF`).
4. For ISO 7816 tags, add application identifiers to `com.apple.developer.nfc.readersession.iso7816.select-identifiers`.
5. For FeliCa tags, specify exact system codes in `com.apple.developer.nfc.readersession.felica.systemcodes` (no wildcards).

Always verify `NFCNDEFReaderSession.readingAvailable` before presenting NFC UI.

## NDEF Reader Session

Read NDEF tags using `NFCNDEFReaderSession`:

```swift
import CoreNFC

final class NFCReader: NSObject, NFCNDEFReaderSessionDelegate {
    var session: NFCNDEFReaderSession?

    func beginScan() {
        guard NFCNDEFReaderSession.readingAvailable else { return }
        session = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: true)
        session?.alertMessage = "Hold iPhone near NFC tag."
        session?.begin()
    }

    func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {
        for message in messages {
            for record in message.records {
                // Process payload
            }
        }
    }

    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        // Handle session timeout, cancellation, or hardware error
    }
}
```

## Tag Reader Session & Writing

Connect to tags and write NDEF messages using `NFCTagReaderSession`:

```swift
func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
    guard let tag = tags.first else { return }

    session.connect(to: tag) { error in
        guard error == nil else { session.invalidate(errorMessage: "Connection failed"); return }

        guard case let .ndef(ndefTag) = tag else { return }
        ndefTag.queryNDEFStatus { status, capacity, error in
            guard status == .readWrite else { return }

            let payload = NFCNDEFPayload.wellKnownTypeURIPayload(url: URL(string: "https://example.com")!)!
            let message = NFCNDEFMessage(records: [payload])

            ndefTag.writeNDEF(message) { error in
                if error == nil {
                    session.alertMessage = "Write successful!"
                    session.invalidate()
                }
            }
        }
    }
}
```

## NDEF Message Construction

Construct standardized NDEF payloads:

```swift
// URI Payload
let uriPayload = NFCNDEFPayload.wellKnownTypeURIPayload(url: destinationURL)!

// Text Payload
let textPayload = NFCNDEFPayload.wellKnownTypeTextPayload(string: "Device-101", locale: Locale(identifier: "en"))!

let message = NFCNDEFMessage(records: [uriPayload, textPayload])
```

## Background Tag Reading

Supported iPhones continuously scan for NDEF tags containing URL payloads when the screen is on:
- Universal links open the app directly without showing an NFC scanner UI.
- Handle background URLs via standard SwiftUI `.onOpenURL` or UIKit `scene(_:openURLContexts:)`.

## Common Mistakes

- **Using legacy NDEF entitlement value**: Use `TAG` in `com.apple.developer.nfc.readersession.formats`.
- **Failing to invalidate session on success**: The system NFC alert stays visible until `session.invalidate()` is explicitly called.
- **Calling NFC APIs without checking availability**: Crashes or throws on unsupported hardware or simulator targets.
- **Overlooking session timeout**: Sessions automatically time out after 60 seconds; handle `NFCReaderError.readerSessionInvalidationErrorSessionTimeout`.
- **Writing to read-only tags**: Always query `ndefTag.queryNDEFStatus` and verify `.readWrite` status before attempting writes.

## Review Checklist

- [ ] `NFCReaderUsageDescription` configured in Info.plist
- [ ] `com.apple.developer.nfc.readersession.formats` set to `["TAG"]`
- [ ] Reader availability checked before session creation
- [ ] Sessions properly invalidated upon successful read/write
- [ ] Errors handled for user cancellation and timeout

## References

- Extended patterns (ISO 7816 commands, multi-tag scanning, NDEF locking): [references/nfc-patterns.md](references/nfc-patterns.md)
- [Core NFC framework](https://sosumi.ai/documentation/corenfc)
- [NFCNDEFReaderSession](https://sosumi.ai/documentation/corenfc/nfcndefreadersession)
- [NFCTagReaderSession](https://sosumi.ai/documentation/corenfc/nfctagreadersession)
- [NFCNDEFMessage](https://sosumi.ai/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://sosumi.ai/documentation/corenfc/nfcndefpayload)
- [NFCNDEFTag](https://sosumi.ai/documentation/corenfc/nfcndeftag)
- [NFCNDEFReaderSessionDelegate](https://sosumi.ai/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSessionDelegate](https://sosumi.ai/documentation/corenfc/nfctagreadersessiondelegate-2joku)
- [Building an NFC Tag-Reader App](https://sosumi.ai/documentation/corenfc/building-an-nfc-tag-reader-app)
- [Adding Support for Background Tag Reading](https://sosumi.ai/documentation/corenfc/adding-support-for-background-tag-reading)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
