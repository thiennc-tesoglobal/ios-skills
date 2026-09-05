---
name: swiftui-uikit-interop
description: "Bridges UIKit and SwiftUI with representables, hosting controllers/configurations, coordinators, and shared observable state. Use for wrapping UIKit or third-party views/controllers, embedding SwiftUI in UIKit, system controller surfaces, or incremental UIKit-to-SwiftUI migration."
---

# SwiftUI-UIKit Interop

Bridge UIKit and SwiftUI in both directions: wrap UIKit views and controllers for use in SwiftUI, embed SwiftUI views into existing UIKit view hierarchies, and coordinate state updates safely. Targets Swift 6.3 / iOS 26+.

## Contents

- [Bridging Directions](#bridging-directions)
- [Representable Lifecycle and Coordinator](#representable-lifecycle-and-coordinator)
- [State Synchronization and Feedback Loops](#state-synchronization-and-feedback-loops)
- [Embedding SwiftUI in UIKit](#embedding-swiftui-in-uikit)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Bridging Directions

1. **UIKit into SwiftUI**:
   - `UIViewRepresentable`: Wraps a custom `UIView` (e.g., text views, maps, custom controls).
   - `UIViewControllerRepresentable`: Wraps a `UIViewController` (e.g., camera controllers, document pickers, share sheets).
2. **SwiftUI into UIKit**:
   - `UIHostingController`: Embeds SwiftUI views into UIKit view controller hierarchies.
   - `UIHostingConfiguration`: Embeds SwiftUI views directly into `UICollectionView` and `UITableView` cells (iOS 16+).

## Representable Lifecycle and Coordinator

```
makeCoordinator() ──> makeUIView(context:) ──> updateUIView(uiView, context:) ──> dismantleUIView(uiView, coordinator:)
```

- **`makeCoordinator()`**: Called once to create the delegate/coordinator object.
- **`makeUIView(context:)`**: Called once to instantiate the UIKit view and assign delegates.
- **`updateUIView(_:context:)`**: Called on **every** SwiftUI state change affecting the view. Must be idempotent.
- **`dismantleUIView(_:coordinator:)`**: Cleanup point when the view leaves the hierarchy. Invalidate timers, unregister observers.

## State Synchronization and Feedback Loops

> [!WARNING]
> Prevent infinite update cycles:
> When UIKit notifies the coordinator of a change (e.g., `textViewDidChange`), the coordinator updates SwiftUI state via `@Binding`. This triggers `updateUIView`.
> Always check for value equality before applying updates to the UIKit view:
> ```swift
> if uiView.text != text { uiView.text = text }
> ```

## Embedding SwiftUI in UIKit

When adding a `UIHostingController` as a child view controller:
1. `addChild(hostingController)`
2. `view.addSubview(hostingController.view)`
3. Set Auto Layout constraints
4. `hostingController.didMove(toParent: self)`

Use `UIHostingConfiguration` for modern cell layouts in `UICollectionView`/`UITableView` without manual controller management.

## Route by Task

- For wrapping `MKMapView`, `UITextView`, and camera capture controllers, read [Map, Text, and Camera Wrappers](references/map-text-and-camera-wrappers.md).
- For `PHPickerViewController`, `MFMailComposeViewController`, `UIActivityViewController`, and search controllers, read [Picker, Mail, Share, and Search Wrappers](references/picker-mail-share-and-search-wrappers.md).
- For `PDFView`, `QLPreviewController`, and `MFMessageComposeViewController`, read [PDF and Message Wrappers](references/pdf-and-message-wrappers.md).
- For embedding SwiftUI in UIKit table/collection cells, navigation transitions, and full hosting migration, read [Hosting Migration](references/hosting-migration.md).

## Common Mistakes

- Re-creating heavy UIKit objects inside `updateUIView` instead of configuring the existing instance.
- Omitting equality checks in `updateUIView`, triggering continuous render feedback loops.
- Adding a `UIHostingController`'s view without calling `addChild` and `didMove(toParent:)`.
- Forgetting to clean up delegates, KVO, or NotificationCenter observers in `dismantleUIView`.
- Ignoring safe area insets and sizing calculations (`sizeThatFits`) in custom representables.

## Review Checklist

- [ ] `makeCoordinator` used for delegates, target-actions, and data sources
- [ ] `updateUIView` guards against redundant assignments to avoid feedback loops
- [ ] Child view controller containment calls (`addChild`, `didMove`) properly paired
- [ ] Cell layouts in UIKit use `UIHostingConfiguration` where available
- [ ] Subscribed observers and display links invalidated in `dismantleUIView`
- [ ] Auto Layout constraints configured with `translatesAutoresizingMaskIntoConstraints = false`

## References

- [Map, text, and camera representable recipes](references/map-text-and-camera-wrappers.md)
- [Picker, mail, share, and search recipes](references/picker-mail-share-and-search-wrappers.md)
- [PDF, QuickLook, and message composer recipes](references/pdf-and-message-wrappers.md)
- [Hosting migration and UIHostingController guide](references/hosting-migration.md)
- [UIViewRepresentable](https://sosumi.ai/documentation/swiftui/uiviewrepresentable)
- [UIViewControllerRepresentable](https://sosumi.ai/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIHostingController](https://sosumi.ai/documentation/swiftui/uihostingcontroller)
