---
name: browserenginekit
description: "Build alternative browser engines using BrowserEngineKit. Use when developing a non-WebKit browser engine for iOS/iPadOS in supported regions, managing web content/rendering/networking extension processes, configuring GPU and networking process capabilities, checking alternative-engine device eligibility, or reviewing BrowserEngineKit entitlements and Info.plist setup."
---

# BrowserEngineKit

Framework for building web browsers with alternative (non-WebKit) rendering
engines on iOS and iPadOS. Provides process isolation, XPC communication,
capability management, and system integration for browser apps that implement
their own HTML/CSS/JavaScript engine. Examples target Swift 6.3 and current
Apple SDKs.

BrowserEngineKit is a specialized framework. Alternative browser engines are
available only through Apple-approved entitlement profiles and supported-region
device eligibility. EU support applies to eligible users on iOS 17.4+ and
iPadOS 18+; Japan support starts with iOS 26.2 and adds explicit PAC/MIE
security requirements for browser apps. Development and testing can occur
anywhere. The companion frameworks BrowserEngineCore (low-level primitives) and
BrowserKit (eligibility checks, data transfer) support the overall workflow.

## Workflow

1. Verify regional eligibility, default-browser requirements, device capability, and approved entitlements before implementation.
2. Model the host plus web-content, networking, and rendering extensions and follow the required bootstrap order.
3. Create, retain, invalidate, and reconnect extension processes/XPC channels as explicit lifecycle states.
4. Request only the capabilities each extension needs and keep JIT, sandbox, media, layer, text, and download responsibilities separated.
5. Verify eligible/ineligible devices, process crashes, relaunch, backgrounding, downloads, memory pressure, and security boundaries.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for eligibility, entitlements, architecture, process management, capabilities, sandboxing, JIT, and downloads.
- Read [extended BrowserEngineKit patterns](references/browserenginekit-patterns.md) for text interaction, layer hosting, scroll coordination, bookmarks, content filtering, and XPC recipes.

## Core Decisions

- Treat entitlement approval and runtime eligibility as separate gates.
- Launch extensions only from the host and discard process objects after invalidation.
- Apply JIT-related entitlements only to the intended content process.
- Never weaken sandbox boundaries to simplify cross-process communication.

## Common Mistakes

### DON'T: Skip the bootstrap sequence

```swift
// WRONG - content extension has no path to other extensions
let contentProcess = try await WebContentProcess(
    bundleIdentifier: nil, onInterruption: {}
)
// Immediately start sending work without connecting to networking/rendering

// CORRECT - broker connections through the host app
let networkEndpoint = try await networkProxy.getEndpoint()
let renderEndpoint = try await renderProxy.getEndpoint()
try await contentProxy.bootstrap(
    renderingExtension: renderEndpoint,
    networkExtension: networkEndpoint
)
```

### DON'T: Launch extensions from other extensions

```swift
// WRONG - extensions cannot launch other extensions
// (inside a WebContentExtension)
let network = try await NetworkingProcess(...)

// CORRECT - only the host app launches extensions
// Host app creates all processes, then brokers connections
```

### DON'T: Use extension process objects after invalidation

```swift
// WRONG
contentProcess.invalidate()
let conn = try contentProcess.makeLibXPCConnection()  // Error

// CORRECT - create a new process if needed
let newProcess = try await WebContentProcess(
    bundleIdentifier: nil, onInterruption: {}
)
```

### DON'T: Apply JIT entitlements to non-content extensions

JIT compilation entitlements (`com.apple.security.cs.allow-jit`) are valid
only on web content extensions. Adding them to the host app, rendering
extension, or networking extension causes App Store rejection.

### DON'T: Hard-code region eligibility

```swift
// WRONG
if Locale.current.region?.identifier == "DE" {
    useAlternativeEngine()
}

// CORRECT - use the system eligibility API
let eligible = try await BEAvailability.isEligible(for: .webBrowser)
if eligible {
    useAlternativeEngine()
}
```

### DON'T: Forget to set UIRequiredDeviceCapabilities

Without `web-browser-engine` in `UIRequiredDeviceCapabilities`, users on
unsupported devices can download the app and hit runtime failures.

## Review Checklist

- [ ] `com.apple.developer.web-browser-engine.host` entitlement on host app
- [ ] Each extension has its type-specific entitlement
- [ ] `UIRequiredDeviceCapabilities` includes `web-browser-engine`
- [ ] `arm64e` instruction set configured for all iOS device targets
- [ ] `arm64e` is not set for Simulator targets
- [ ] Swift packages built with `iOSPackagesShouldBuildARM64e` workspace setting
- [ ] Extension point identifiers set correctly in each extension's Info.plist
- [ ] Interruption handlers implemented for all process types
- [ ] Bootstrap sequence connects content extension to networking and rendering
- [ ] Capabilities granted before work begins and invalidated when done
- [ ] Visibility propagation interaction added to browser content views
- [ ] Restricted sandbox applied to content extensions after initialization
- [ ] `BEAvailability` used for eligibility checks instead of manual region logic
- [ ] Memory attribution entitlements use the host app bundle ID as their value
- [ ] Download progress reported via `BEDownloadMonitor` for active downloads on iOS 18.2+
- [ ] Memory tagging enabled for Japan distribution on iOS 26.2+ (recommended for EU)

## References
- Extended patterns (text interaction, layer hosting, scroll views, file bookmarks, XPC communication, content filtering): [references/browserenginekit-patterns.md](references/browserenginekit-patterns.md)
- [BrowserEngineKit framework](https://sosumi.ai/documentation/browserenginekit)
- [Designing your browser architecture](https://sosumi.ai/documentation/browserenginekit/designing-your-browser-architecture)
- [Creating browser extensions in Xcode](https://sosumi.ai/documentation/browserenginekit/creating-browser-extensions-in-xcode)
- [Managing the browser extension life cycle](https://sosumi.ai/documentation/browserenginekit/managing-the-browser-extension-lifecycle)
- [Using XPC to communicate with browser extensions](https://sosumi.ai/documentation/browserenginekit/using-xpc-to-communicate-with-browser-extensions)
- [Web Browser Engine Entitlement](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.web-browser-engine.host)
- [BrowserKit framework](https://sosumi.ai/documentation/browserkit)
- [BrowserEngineCore framework](https://sosumi.ai/documentation/browserenginecore)
- [Sample: Developing a browser app with an alternative engine](https://sosumi.ai/documentation/browserenginekit/developing-a-browser-app-that-uses-an-alternative-browser-engine)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
