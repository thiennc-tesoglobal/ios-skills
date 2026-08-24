# SwiftUI Picker, Mail, Share, and Search Wrappers

Read this reference only when the task matches the sections below.

## 4. PHPickerViewController Wrapper

Multi-select photo picker that loads selected images asynchronously.

```swift
import SwiftUI
import PhotosUI

struct PhotoPicker: UIViewControllerRepresentable {
    @Binding var selectedImages: [UIImage]
    var selectionLimit: Int = 0  // 0 = unlimited
    @Environment(\.dismiss) private var dismiss

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var config = PHPickerConfiguration(photoLibrary: .shared())
        config.filter = .images
        config.selectionLimit = selectionLimit
        config.preferredAssetRepresentationMode = .current

        let picker = PHPickerViewController(configuration: config)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {
        // Nothing to update -- configuration is immutable after creation
    }

    final class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: PhotoPicker

        init(_ parent: PhotoPicker) { self.parent = parent }

        func picker(
            _ picker: PHPickerViewController,
            didFinishPicking results: [PHPickerResult]
        ) {
            parent.dismiss()

            guard !results.isEmpty else { return }

            Task { @MainActor in
                var images: [UIImage] = []
                for result in results {
                    if let image = await loadImage(from: result.itemProvider) {
                        images.append(image)
                    }
                }
                parent.selectedImages = images
            }
        }

        private func loadImage(from provider: NSItemProvider) async -> UIImage? {
            await withCheckedContinuation { continuation in
                if provider.canLoadObject(ofClass: UIImage.self) {
                    provider.loadObject(ofClass: UIImage.self) { image, _ in
                        continuation.resume(returning: image as? UIImage)
                    }
                } else {
                    continuation.resume(returning: nil)
                }
            }
        }
    }
}
```

### Usage

```swift
struct ImagePickerDemo: View {
    @State private var images: [UIImage] = []
    @State private var showPicker = false

    var body: some View {
        VStack {
            ScrollView(.horizontal) {
                HStack {
                    ForEach(images.indices, id: \.self) { i in
                        Image(uiImage: images[i])
                            .resizable()
                            .scaledToFill()
                            .frame(width: 100, height: 100)
                            .clipShape(.rect(cornerRadius: 8))
                    }
                }
            }
            Button("Pick Photos") { showPicker = true }
        }
        .sheet(isPresented: $showPicker) {
            PhotoPicker(selectedImages: $images, selectionLimit: 5)
        }
    }
}
```

### Gotchas

- **Always dismiss in the delegate.** `picker(_:didFinishPicking:)` is called for both selection and cancellation (with empty results). Dismiss in both cases.
- **Async image loading.** `NSItemProvider.loadObject` is completion-based. Wrap in `withCheckedContinuation` for async/await usage. Load images after dismissal to avoid blocking the picker UI.
- **iOS 17 alternative.** `PhotosUI.PhotosPicker` is a native SwiftUI view. Prefer it unless you need custom picker UI or advanced filtering.

---

## 5. MFMailComposeViewController Wrapper

Present the system email composer with pre-filled fields and handle the result.

```swift
import SwiftUI
import MessageUI

struct MailComposer: UIViewControllerRepresentable {
    let subject: String
    let recipients: [String]
    let body: String
    var isHTML: Bool = false
    var onResult: ((MFMailComposeResult) -> Void)?
    @Environment(\.dismiss) private var dismiss

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let controller = MFMailComposeViewController()
        controller.mailComposeDelegate = context.coordinator
        controller.setSubject(subject)
        controller.setToRecipients(recipients)
        controller.setMessageBody(body, isHTML: isHTML)
        return controller
    }

    func updateUIViewController(_ uiViewController: MFMailComposeViewController, context: Context) {
        // Cannot update mail compose after presentation
    }

    final class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let parent: MailComposer

        init(_ parent: MailComposer) { self.parent = parent }

        func mailComposeController(
            _ controller: MFMailComposeViewController,
            didFinishWith result: MFMailComposeResult,
            error: Error?
        ) {
            parent.onResult?(result)
            parent.dismiss()
        }
    }
}
```

### Usage

```swift
struct FeedbackView: View {
    @State private var showMail = false

    var body: some View {
        Button("Send Feedback") {
            guard MFMailComposeViewController.canSendMail() else { return }
            showMail = true
        }
        .sheet(isPresented: $showMail) {
            MailComposer(
                subject: "App Feedback",
                recipients: ["support@example.com"],
                body: "I have feedback about..."
            ) { result in
                print("Mail result: \(result.rawValue)")
            }
        }
    }
}
```

### Gotchas

- **Check `canSendMail()` before presenting.** If it returns `false`, do not display `MFMailComposeViewController`; show fallback UI or disable the mail action.
- **Cannot update after presentation.** `updateUIViewController` is intentionally empty -- the mail compose API does not support changing fields after the controller is shown.
- **The delegate protocol name is `MFMailComposeViewControllerDelegate`**, not `MFMailComposeDelegate`.

---

## 6. UIActivityViewController Wrapper (Share Sheet)

Present the system share sheet. This is a `UIViewControllerRepresentable` because `UIActivityViewController` is a controller, not a view.

```swift
import SwiftUI

struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    var activities: [UIActivity]? = nil
    var excludedTypes: [UIActivity.ActivityType]? = nil

    func makeUIViewController(context: Context) -> UIActivityViewController {
        let controller = UIActivityViewController(
            activityItems: items,
            applicationActivities: activities
        )
        controller.excludedActivityTypes = excludedTypes
        return controller
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {
        // Cannot update after presentation
    }
}
```

### Usage

```swift
struct ContentView: View {
    @State private var showShare = false

    var body: some View {
        Button("Share") { showShare = true }
            .sheet(isPresented: $showShare) {
                ShareSheet(items: ["Check out this app!", URL(string: "https://example.com")!])
                    .presentationDetents([.medium])
            }
    }
}
```

### Gotchas

- **Present via `.sheet`.** Do not try to use `UIActivityViewController` as an inline view -- it is a modal controller.
- **iPad requires `popoverPresentationController`.** When using on iPad outside of `.sheet`, set the source view/rect on the popover controller. SwiftUI's `.sheet` handles this automatically.
- **iOS 16+ alternative.** `ShareLink` is a native SwiftUI view for Transferable items. Prefer it for simple sharing.

---

## 7. UISearchBar Wrapper

Wrap `UISearchBar` with delegate-based callbacks, debounce support, and cancel button handling.

```swift
import SwiftUI
import Combine

struct SearchBar: UIViewRepresentable {
    @Binding var text: String
    var placeholder: String = "Search"
    var onSearch: ((String) -> Void)?
    var onCancel: (() -> Void)?

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> UISearchBar {
        let searchBar = UISearchBar()
        searchBar.delegate = context.coordinator
        searchBar.placeholder = placeholder
        searchBar.searchBarStyle = .minimal
        searchBar.autocapitalizationType = .none
        return searchBar
    }

    func updateUIView(_ uiView: UISearchBar, context: Context) {
        if uiView.text != text {
            uiView.text = text
        }
    }

    final class Coordinator: NSObject, UISearchBarDelegate {
        var parent: SearchBar
        private var debounceTask: Task<Void, Never>?

        init(_ parent: SearchBar) { self.parent = parent }

        func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
            parent.text = searchText
            searchBar.showsCancelButton = !searchText.isEmpty

            // Debounce search
            debounceTask?.cancel()
            debounceTask = Task { @MainActor in
                try? await Task.sleep(for: .milliseconds(300))
                guard !Task.isCancelled else { return }
                parent.onSearch?(searchText)
            }
        }

        func searchBarSearchButtonClicked(_ searchBar: UISearchBar) {
            debounceTask?.cancel()
            parent.onSearch?(parent.text)
            searchBar.resignFirstResponder()
        }

        func searchBarCancelButtonClicked(_ searchBar: UISearchBar) {
            parent.text = ""
            parent.onCancel?()
            searchBar.resignFirstResponder()
            searchBar.showsCancelButton = false
        }
    }
}
```

### Usage

```swift
struct SearchableList: View {
    @State private var query = ""
    @State private var results: [String] = []

    var body: some View {
        VStack(spacing: 0) {
            SearchBar(text: $query, placeholder: "Search items") { text in
                results = performSearch(text)
            }
            List(results, id: \.self) { Text($0) }
        }
    }
}
```

### Gotchas

- **Native `.searchable` modifier.** Prefer SwiftUI's `.searchable(text:)` modifier for standard search patterns. Use this wrapper only when you need precise control over search bar appearance or delegate timing.
- **Debounce with `Task.sleep`.** Cancel the previous task before starting a new one to debounce. `Combine` is not needed.
- **Cancel button state.** Toggle `showsCancelButton` in the delegate, not in `updateUIView`, to avoid layout jumps.

---
