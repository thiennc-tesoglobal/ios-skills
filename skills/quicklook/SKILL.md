---
name: quicklook
description: "Preview documents, images, audio, and 3D USDZ files with QLPreviewController and SwiftUI .quickLookPreview, and generate asynchronous thumbnails using QLThumbnailGenerator in iOS apps."
---

# QuickLook

Preview documents, media, and 3D models with `QLPreviewController` and generate fast, cached file thumbnails with `QLThumbnailGenerator` in iOS and iPadOS.

## Contents

- [SwiftUI QuickLook Previews](#swiftui-quicklook-previews)
- [UIKit QLPreviewController](#uikit-qlpreviewcontroller)
- [Thumbnail Generation with QLThumbnailGenerator](#thumbnail-generation-with-qlthumbnailgenerator)
- [Custom QLPreviewItem Conformance](#custom-qlpreviewitem-conformance)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

---

## SwiftUI QuickLook Previews

The `.quickLookPreview` modifier presents system file previews directly from SwiftUI when binding to an optional local `URL`.

```swift
import SwiftUI
import QuickLook

struct DocumentRowView: View {
    let fileURL: URL
    @State private var previewURL: URL?

    var body: some View {
        HStack {
            Image(systemName: "doc.fill")
            Text(fileURL.lastPathComponent)
            Spacer()
            Button("Preview") {
                previewURL = fileURL
            }
        }
        .quickLookPreview($previewURL)
    }
}
```

---

## UIKit QLPreviewController

For multi-item carousels, custom navigation transitions, or fine-grained preview control, use `QLPreviewController`.

```swift
import UIKit
import QuickLook

@MainActor
final class DocumentPreviewCoordinator: NSObject, QLPreviewControllerDataSource, QLPreviewControllerDelegate {
    private var previewItems: [URL] = []

    func presentPreview(from presenter: UIViewController, files: [URL], startIndex: Int = 0) {
        self.previewItems = files

        let previewController = QLPreviewController()
        previewController.dataSource = self
        previewController.delegate = self
        previewController.currentPreviewItemIndex = startIndex

        presenter.present(previewController, animated: true)
    }

    // MARK: - QLPreviewControllerDataSource

    func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
        previewItems.count
    }

    func previewController(_ controller: QLPreviewController, previewItemAt index: Int) -> any QLPreviewItem {
        previewItems[index] as NSURL
    }
}
```

---

## Thumbnail Generation with QLThumbnailGenerator

Generate asynchronous, system-cached thumbnails for documents, images, and videos with `QLThumbnailGenerator.Request`.

```swift
import QuickLookThumbnailing
import UIKit

actor ThumbnailLoader {
    static let shared = ThumbnailLoader()
    private let cache = NSCache<NSURL, UIImage>()

    func loadThumbnail(for fileURL: URL, size: CGSize, scale: CGFloat = 2.0) async throws -> UIImage {
        if let cached = cache.object(forKey: fileURL as NSURL) {
            return cached
        }

        let request = QLThumbnailGenerator.Request(
            fileAt: fileURL,
            size: size,
            scale: scale,
            representationTypes: .all
        )

        let representation = try await QLThumbnailGenerator.shared.generateBestRepresentation(for: request)
        let image = representation.uiImage

        cache.setObject(image, forKey: fileURL as NSURL)
        return image
    }
}
```

---

## Custom QLPreviewItem Conformance

Provide custom titles or encrypted/in-memory file references wrapped in local sandbox files:

```swift
import QuickLook

final class PreviewableDocument: NSObject, QLPreviewItem {
    let previewItemURL: URL?
    let previewItemTitle: String?

    init(url: URL, title: String? = nil) {
        self.previewItemURL = url
        self.previewItemTitle = title ?? url.lastPathComponent
        super.init()
    }
}
```

---

## Common Mistakes

- **Passing remote web URLs:** QuickLook does not stream remote HTTP URLs. Files must be downloaded to a local file URL in the temporary or cache directory before previewing.
- **Ignoring scale in thumbnail generation:** Passing default scale `1.0` produces blurry thumbnails on Retina displays; always pass environment `@Environment(\.displayScale)` or `traitCollection.displayScale`.
- **Blocking main actor with thumbnail loading:** Calling synchronous thumbnail APIs freezes the UI; use async `generateBestRepresentation(for:)` or callbacks.
- **Retaining temporary preview files indefinitely:** Files copied to temp directories for QuickLook preview should be cleaned up after dismiss.
- **Missing QLPreviewItem URL validity:** Passing a file URL pointing to a non-existent file or dangling symlink displays an empty error preview.

---

## Review Checklist

- [ ] Are target files downloaded locally before passing to QuickLook?
- [ ] Is `.quickLookPreview($url)` used for standard SwiftUI single-file previewing?
- [ ] Does `QLPreviewControllerDataSource` return valid `QLPreviewItem` conforming objects?
- [ ] Does `QLThumbnailGenerator.Request` pass appropriate size, screen scale, and representation types?
- [ ] Are generated thumbnails cached in `NSCache` to prevent redundant disk decodes?
- [ ] Are temporary files cleaned up when preview presentation is completed?

---

## References

- [QuickLook Patterns](references/quicklook-patterns.md) — SwiftUI custom preview sheets, zoom transitions, and thumbnail caching.
- [QuickLook Documentation](https://sosumi.ai/documentation/quicklook) — Official Apple QuickLook API reference.
- [QuickLookThumbnailing Documentation](https://sosumi.ai/documentation/quicklookthumbnailing) — Asynchronous thumbnail generator reference.
- [QLPreviewController Guide](https://sosumi.ai/documentation/quicklook/qlpreviewcontroller) — UIKit preview controller and delegate methods.
