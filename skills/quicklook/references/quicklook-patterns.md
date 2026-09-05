# QuickLook Patterns and Recipes

Advanced workflows for SwiftUI `UIViewControllerRepresentable` bridges, custom zoom transition delegates, and progressive thumbnail pipelines.

## SwiftUI Multi-File QLPreviewController

Wrap `QLPreviewController` in a `UIViewControllerRepresentable` to preview multi-file carousels in SwiftUI:

```swift
import SwiftUI
import QuickLook

struct QuickLookSheet: UIViewControllerRepresentable {
    let urls: [URL]
    @Binding var currentIndex: Int

    func makeUIViewController(context: Context) -> UINavigationController {
        let controller = QLPreviewController()
        controller.dataSource = context.coordinator
        controller.delegate = context.coordinator
        controller.currentPreviewItemIndex = currentIndex

        let navigation = UINavigationController(rootViewController: controller)
        return navigation
    }

    func updateUIViewController(_ uiViewController: UINavigationController, context: Context) {
        if let preview = uiViewController.topViewController as? QLPreviewController {
            if preview.currentPreviewItemIndex != currentIndex {
                preview.currentPreviewItemIndex = currentIndex
            }
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    final class Coordinator: NSObject, QLPreviewControllerDataSource, QLPreviewControllerDelegate {
        let parent: QuickLookSheet

        init(parent: QuickLookSheet) {
            self.parent = parent
        }

        func numberOfPreviewItems(in controller: QLPreviewController) -> Int {
            parent.urls.count
        }

        func previewController(_ controller: QLPreviewController, previewItemAt index: Int) -> any QLPreviewItem {
            parent.urls[index] as NSURL
        }

        func previewController(_ controller: QLPreviewController, didUpdateCurrentPreviewItemAt index: Int) {
            parent.currentIndex = index
        }
    }
}
```

## Progressive Thumbnail Generation

Use `generateRepresentations` with an update handler to display a low-quality icon or thumbnail immediately while decoding high-quality representations in the background:

```swift
import QuickLookThumbnailing
import UIKit

@MainActor
final class ProgressiveThumbnailLoader {
    func loadProgressiveThumbnail(
        for fileURL: URL,
        targetSize: CGSize,
        scale: CGFloat,
        onUpdate: @escaping (UIImage, QLThumbnailRepresentation.RepresentationType) -> Void
    ) {
        let request = QLThumbnailGenerator.Request(
            fileAt: fileURL,
            size: targetSize,
            scale: scale,
            representationTypes: .all
        )

        QLThumbnailGenerator.shared.generateRepresentations(for: request) { thumbnail, type, error in
            guard let image = thumbnail?.uiImage else { return }
            Task { @MainActor in
                onUpdate(image, type)
            }
        }
    }
}
```

## Zoom Transition Delegate

Implement `QLPreviewControllerDelegate` to animate previews smoothly from the originating thumbnail view:

```swift
import UIKit
import QuickLook

final class TransitionCoordinator: NSObject, QLPreviewControllerDelegate {
    var sourceViewProvider: ((Int) -> UIView?)?

    func previewController(
        _ controller: QLPreviewController,
        transitionViewFor item: any QLPreviewItem
    ) -> UIView? {
        guard let index = (controller.dataSource as? DocumentPreviewCoordinator)?.previewItems.firstIndex(where: {
            ($0 as NSURL) == (item as? NSURL)
        }) else {
            return nil
        }
        return sourceViewProvider?(index)
    }
}
```

## Validating File Types Before Preview

Ensure files can be opened by QuickLook using `UniformTypeIdentifiers`:

```swift
import UniformTypeIdentifiers

final class QuickLookValidator {
    static func canQuickLook(fileURL: URL) -> Bool {
        guard let resourceValues = try? fileURL.resourceValues(forKeys: [.contentTypeKey]),
              let contentType = resourceValues.contentType else {
            return false
        }

        // QuickLook natively supports images, PDFs, text, audiovisual, and USDZ 3D models
        let supportedTypes: [UTType] = [
            .pdf,
            .image,
            .audiovisualContent,
            .plainText,
            .usdz
        ]

        return supportedTypes.contains { contentType.conforms(to: $0) }
    }
}
```
