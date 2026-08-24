# BrowserEngineKit Core Implementation Details

Read this reference when the task needs concrete setup, API wiring, or implementation recipes. Keep scope, workflow, non-obvious invariants, mistakes, and review gates in the parent `SKILL.md`.

## Overview and Eligibility

### Eligibility Checking

Use `BEAvailability` from the BrowserKit framework to check whether the device
is eligible for alternative browser engines. `BEAvailability` is available on
iOS/iPadOS 18.4+:

```swift
import BrowserKit

do {
    let eligible = try await BEAvailability.isEligible(for: .webBrowser)
    guard eligible else { return /* fall back or explain */ }
    // Device supports alternative browser engines
} catch {
    // Handle eligibility lookup failure
}
```

Eligibility depends on the device region and OS version. Do not hard-code
region checks; rely on the system API.

Availability anchors: process APIs are iOS/iPadOS 17.4+, `BEDownloadMonitor`
is iOS 18.2+, `.revision2` restricted sandbox is iOS 26+, and
`RenderingExtensionFeature.coreML` is iOS 26.2+.

## Entitlements

### Browser App (Host)

The host app requires two entitlements:

| Entitlement | Purpose |
|---|---|
| `com.apple.developer.web-browser` | Enables default-browser candidacy |
| `com.apple.developer.web-browser-engine.host` | Enables alternative engine extensions |

Both must be requested from Apple. The request process varies by region.

### Extension Entitlements

Each extension target requires its type-specific entitlement set to `true`:

| Extension Type | Entitlement |
|---|---|
| Web content | `com.apple.developer.web-browser-engine.webcontent` |
| Networking | `com.apple.developer.web-browser-engine.networking` |
| Rendering | `com.apple.developer.web-browser-engine.rendering` |

### Optional Entitlements

| Entitlement | Extension | Purpose |
|---|---|---|
| `com.apple.security.cs.allow-jit` | Web content | JIT compilation of scripts |
| `com.apple.developer.kernel.extended-virtual-addressing` | Web content | Required alongside JIT |
| `com.apple.developer.memory.transfer_send` | Rendering | Send memory attribution; value is host app bundle ID |
| `com.apple.developer.memory.transfer_accept` | Web content | Accept memory attribution; value is host app bundle ID |
| `com.apple.developer.web-browser-engine.restrict.notifyd` | Web content | Restrict notification daemon access |

### Embedded Browser Engine (Non-Browser Apps)

Apps that are not browsers but embed an alternative engine for in-app browsing
use different entitlements:

| Entitlement | Purpose |
|---|---|
| `com.apple.developer.embedded-web-browser-engine` | Enable embedded engine |
| `com.apple.developer.embedded-web-browser-engine.engine-association` | Declare engine ownership |

`engine-association` is available starting iOS/iPadOS/Mac Catalyst 26.2 and is
set to `first-party` when you own the engine or `third-party` when another
developer owns it. Embedded engines use `arm64` only (not `arm64e`), cannot
include browser extensions, and cannot use JIT compilation.

### Japan-Specific Requirements

Browser apps distributed in Japan are supported on iOS 26.2+ and must adopt the
current security mitigations Apple lists for Japan, including Pointer
Authentication Codes and Memory Integrity Enforcement for relevant allocators
and extension processes. Enable hardware memory tagging with
`com.apple.security.hardened-process.checked-allocations`; Apple strongly
recommends enabling it in the EU as well.

## Architecture

A browser built with BrowserEngineKit consists of four components running in
separate processes:

```
Host App (UI, coordination)
  |
  |-- XPC --> Web Content Extension (HTML parsing, JS, DOM)
  |-- XPC --> Networking Extension (URLSession, sockets)
  |-- XPC --> Rendering Extension (Metal, GPU, media)
```

The host app launches and manages all extensions. Extensions cannot launch
other extensions. Extensions communicate with each other through anonymous XPC
endpoints brokered by the host app.

### Bootstrap Sequence

1. Host launches web content, networking, and rendering extensions
2. Host creates XPC connections to each extension
3. Host requests anonymous XPC endpoints from networking and rendering
4. Host sends both endpoints to the web content extension via a bootstrap
   message
5. Web content extension connects directly to networking and rendering

This architecture follows the principle of least privilege: the web content
extension works with untrusted data but has no direct OS resource access.

## Process Management

### Launching Extensions

Each extension type has a corresponding process class in the host app:

```swift
import BrowserEngineKit

// Web content (one per tab or iframe)
let contentProcess = try await WebContentProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // Handle crash or OS interruption
    }
)

// Networking (typically one instance)
let networkProcess = try await NetworkingProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // Handle interruption
    }
)

// Rendering / GPU (typically one instance)
let renderingProcess = try await RenderingProcess(
    bundleIdentifier: nil,
    onInterruption: {
        // Handle interruption
    }
)
```

Pass `nil` for `bundleIdentifier` to use the default extension target. The
interruption handler fires if the extension crashes or is terminated by the OS.

### Creating XPC Connections

```swift
let connection = try contentProcess.makeLibXPCConnection()
// Use connection for inter-process messaging
```

Each process type provides `makeLibXPCConnection()` to create an
`xpc_connection_t` for communication.

### Stopping Extensions

```swift
contentProcess.invalidate()
```

After calling `invalidate()`, no further method calls on the process object
are valid.

## Extension Types

### Web Content Extension

Hosts the browser engine's HTML parser, CSS engine, JavaScript interpreter,
and DOM. Conform to `WebContentExtension` to handle incoming XPC connections:

```swift
import BrowserEngineKit

@main
struct MyWebContentExtension: WebContentExtension {
    func handle(xpcConnection: xpc_connection_t) {
        // Set up message handlers on the connection
    }
}
```

Configure via `WebContentExtensionConfiguration` in the extension's
`EXAppExtensionAttributes`.

### Networking Extension

Handles all network requests using `URLSession` or socket APIs. One instance
serves all tabs:

```swift
import BrowserEngineKit

@main
struct MyNetworkingExtension: NetworkingExtension {
    func handle(xpcConnection: xpc_connection_t) {
        // Handle network request messages
    }
}
```

Configure via `NetworkingExtensionConfiguration`.

### Rendering Extension

Accesses the GPU via Metal for video decoding, compositing, and complex
rendering. One instance typically serves the entire browser:

```swift
import BrowserEngineKit

@main
struct MyRenderingExtension: RenderingExtension {
    init() {
        if #available(iOS 26.2, macOS 26.2, *) {
            enableFeature(.coreML)
        }
    }

    func handle(xpcConnection: xpc_connection_t) {
        // Handle rendering commands
    }
}
```

Configure via `RenderingExtensionConfiguration`.

## Capabilities

Grant capabilities to extensions so the OS schedules them appropriately:

```swift
// Grant foreground priority to an extension
let grant = try contentProcess.grantCapability(.foreground)

// ... extension does foreground work ...

// Relinquish when done
grant.invalidate()
```

### Available Capabilities

| Capability | Use Case |
|---|---|
| `.foreground` | Active tab rendering, visible content |
| `.background` | Background tasks, prefetching |
| `.suspended` | Minimal activity, pending cleanup |
| `.mediaPlaybackAndCapture(environment:)` | Audio/video playback, camera/mic capture |

### Media Environment

For media capabilities, create a `MediaEnvironment` tied to a page URL.
The environment supports `AVCaptureSession` for camera/mic access and is
XPC-serializable for cross-process transport:

```swift
let mediaEnv = MediaEnvironment(webPage: pageURL)
let grant = try contentProcess.grantCapability(
    .mediaPlaybackAndCapture(environment: mediaEnv)
)
try mediaEnv.activate()
let captureSession = try mediaEnv.makeCaptureSession()
```

### Visibility Propagation

Attach a visibility propagation interaction to browser views so extensions
know when content is on screen. Both `WebContentProcess` and
`RenderingProcess` provide `createVisibilityPropagationInteraction()`.

## Layer Hosting and View Coordination

The rendering extension draws into a `LayerHierarchy`, whose content the
host app displays via `LayerHierarchyHostingView`. Handles are passed over
XPC. Use `LayerHierarchyHostingTransactionCoordinator` to synchronize layer
updates atomically across processes.

See [references/browserenginekit-patterns.md](browserenginekit-patterns.md) for detailed layer hosting
examples and transaction coordination.

## Text Interaction

Adopt `BETextInput` on custom text views to integrate with UIKit's text
system. This enables standard text selection, autocorrect, dictation, and
keyboard interactions.

Key integration points:

- `asyncInputDelegate` for communicating text changes to the system
- `handleKeyEntry(_:completionHandler:)` for keyboard events
- `BETextInteraction` for selection gestures, edit menus, and context menus
- `BEScrollView` and `BEScrollViewDelegate` for custom scroll handling

See [references/browserenginekit-patterns.md](browserenginekit-patterns.md) for detailed text interaction
implementation.

## Sandbox and Security

### Restricted Sandbox

After initialization, lock down content extensions using the restricted
sandbox:

```swift
// In the web content extension, after setup:
if #available(iOS 26.0, macOS 26.0, *) {
    applyRestrictedSandbox(revision: .revision2)
} else {
    applyRestrictedSandbox(revision: .revision1)
}
```

This removes access to resources the extension used during startup but no
longer needs. Use the latest available revision for the strongest restrictions.

### JIT Compilation

Web content extensions that JIT-compile JavaScript must transition pages with BrowserEngineKit's witnessed APIs:

```swift
import BrowserEngineCore

be_memory_inline_jit_restrict_rwx_to_rw_with_witness(...)
// write generated code
be_memory_inline_jit_restrict_rwx_to_rx_with_witness(...)
```

Requires the `com.apple.security.cs.allow-jit` and
`com.apple.developer.kernel.extended-virtual-addressing` entitlements on
the web content extension only. If an implementation instead uses `pthread_jit_write_with_callback_np`, it also needs the JIT write allowlist entitlement; do not present `BE_JIT_WRITE_PROTECT_TAG` alone as a complete protection strategy.

### arm64e Requirement

Distribution builds must satisfy the current alternative-browser entitlement profile's device architecture, PAC, and MIE requirements. Keep the host and extension configuration consistent, include the required device slices, and test the signed archive on eligible devices. Embedded engines differ: they are arm64-only and cannot use JIT. Do not force `arm64e` onto Simulator builds or copy a one-line `ARCHS` override that drops required slices.

## Downloads

Report download progress to the system using `BEDownloadMonitor`. Create an
access token, initialize the monitor with source/destination URLs and a
`Progress` object, then call `beginMonitoring()` to show the system download
UI. Use `resumeMonitoring(placeholderURL:)` to resume interrupted downloads.
`BEDownloadMonitor` is available on iOS 18.2+.

See [references/browserenginekit-patterns.md](browserenginekit-patterns.md) for full download management
examples.
