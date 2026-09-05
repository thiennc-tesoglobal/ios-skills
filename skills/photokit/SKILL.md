---
name: photokit
description: "Builds or reviews photo-library picking, image loading, camera capture, and video recording with PhotoKit, PhotosPicker/PHPicker, and AVFoundation. Use for photo or camera permissions, media selection, capture sessions, library changes, caching, or media export."
---

# PhotoKit

Build media selection, camera capture, photo library queries, and image caching workflows with `PhotosUI` (`PhotosPicker`), `PhotoKit` (`PHPhotoLibrary`), and `AVFoundation`. Targets Swift 6.3 / iOS 26+.

## Contents

- [Picker Selection Strategy](#picker-selection-strategy)
- [Privacy and Permissions](#privacy-and-permissions)
- [Image Loading and Caching](#image-loading-and-caching)
- [Camera Capture Boundaries](#camera-capture-boundaries)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Picker Selection Strategy

| Approach | UI Framework | Permissions Needed | Use Case |
|---|---|---|---|
| `PhotosPicker` | SwiftUI | **None** (runs out-of-process) | User selects photos/videos for import |
| `PHPickerViewController` | UIKit | **None** (runs out-of-process) | UIKit equivalent of PhotosPicker |
| `PHPhotoLibrary` | Direct API | `NSPhotoLibraryUsageDescription` | Custom gallery, background sync, asset deletion |
| `AVCaptureSession` | Custom UI | `NSCameraUsageDescription` | Real-time camera viewfinder, photo/video capture |

Prefer `PhotosPicker` for standard media selection. It preserves user privacy and eliminates permission friction.

## Privacy and Permissions

When accessing `PHPhotoLibrary` directly, request authorization and handle `.limited` access:

```swift
let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
switch status {
case .authorized:
    // Full photo library access granted
case .limited:
    // User selected specific photos (present PHPhotoLibrary.shared().presentLimitedLibraryPicker)
case .denied, .restricted:
    // Direct user to Settings
case .notDetermined:
    break
@unknown default:
    break
}
```

Include `NSPhotoLibraryUsageDescription` (read/write) or `NSPhotoLibraryAddUsageDescription` (write-only save) in `Info.plist`.

## Image Loading and Caching

Use `PHCachingImageManager` for fast grid thumbnail generation:
1. **Prepare caching**: Call `startCachingImages(for:targetSize:contentMode:options:)` when scrolling into view.
2. **Reuse options**: Use `PHImageRequestOptions` with `deliveryMode = .opportunistic` for quick thumbnails followed by high-res data.
3. **Cancel obsolete requests**: Cancel pending request IDs when cells scroll out of viewport.

## Camera Capture Boundaries

For custom camera viewfinders using `AVCaptureSession`:
- Configure sessions on a dedicated serial background queue, never on `@MainActor`.
- Balance every transaction with `session.beginConfiguration()` and `defer { session.commitConfiguration() }`.
- Embed viewfinders in SwiftUI using `UIViewRepresentable` backed by `AVCaptureVideoPreviewLayer`.

## Route by Task

- For SwiftUI `PhotosPicker` single/multi-selection and media filtering recipes, read [PhotosPicker Recipes](references/photokit-patterns.md).
- For complete camera controllers, photo capture, video recording, and barcode scanning, read [Camera Capture Patterns](references/camera-capture.md).
- For asset fetching, thumbnail caching with `PHCachingImageManager`, and memory management, read [Image Loading and Caching](references/image-loading-caching.md). For format conversion and compression, read [Image Formats and Compression](references/image-formats-compression.md).
- For video playback, custom player UI, and AVPlayer integration, read [AV Playback Reference](references/av-playback.md).

## Common Mistakes

- Requesting full photo library permissions when `PhotosPicker` would suffice without any permissions.
- Hardcoding `.highQualityFormat` on `PHImageRequestOptions` for fast-scrolling grids, causing dropped frames.
- Running `AVCaptureSession.startRunning()` or configuration changes on `@MainActor`.
- Forgetting to handle `.limited` photo library access on iOS 14+.
- Loading full-resolution `UIImage` into memory for multiple items simultaneously without downsampling.

## Review Checklist

- [ ] `PhotosPicker` preferred over custom library enumeration where appropriate
- [ ] `NSPhotoLibraryUsageDescription` provided when using `PHPhotoLibrary`
- [ ] `NSCameraUsageDescription` provided when using `AVCaptureSession`
- [ ] `.limited` photo library authorization handled gracefully
- [ ] `PHCachingImageManager` used with preheating for asset collections
- [ ] `AVCaptureSession` configured and started on a serial background queue
- [ ] Photo picker item loading handles cancellation and errors asynchronously
- [ ] Image assets downsampled to target display size to prevent memory spikes

## References

- [PhotoKit patterns and picker recipes](references/photokit-patterns.md)
- [Camera capture and AVCaptureSession reference](references/camera-capture.md)
- [Image loading, caching, and downsampling](references/image-loading-caching.md)
- [Image formats and compression](references/image-formats-compression.md)
- [AV Playback reference](references/av-playback.md)
- [PhotoKit documentation](https://sosumi.ai/documentation/photokit)
- [PhotosUI documentation](https://sosumi.ai/documentation/photosui)
