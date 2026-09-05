# QuickLook Preview and Thumbnail Generation Service

You are building a file browser and document manager for an iOS and iPadOS app. The app handles diverse local file formats (PDFs, images, videos, 3D USDZ files) and needs rich previewing and high-performance thumbnail rendering.

Implement the document preview and thumbnail pipeline conforming to these requirements:
1. Provide a SwiftUI file detail view integrating the `.quickLookPreview` modifier.
2. Build an asynchronous `ThumbnailService` using `QLThumbnailGenerator` that requests appropriate point size and screen display scale, returning `UIImage` results and caching them with `NSCache`.
3. Support multi-file document collections using `QLPreviewController` and `QLPreviewControllerDataSource`, with custom `QLPreviewItem` titles.
4. Correctly address the limitation that QuickLook requires local file URLs (handling temporary downloads and post-dismiss cleanup when dealing with remote resources).
