# SwiftUI PDF and Message Wrappers

Read this reference only when the task matches the sections below.

## 8. PDFView Wrapper (PDFKit)

Display PDF documents in SwiftUI using `PDFView` from PDFKit. Supports loading from URL, Data, or file path, with configurable display mode and auto-scaling.

```swift
import SwiftUI
import PDFKit

struct PDFViewer: UIViewRepresentable {
    let document: PDFDocument?
    var displayMode: PDFDisplayMode = .singlePageContinuous
    var autoScales: Bool = true
    var displayDirection: PDFDisplayDirection = .vertical
    var pageShadowsEnabled: Bool = true

    func makeUIView(context: Context) -> PDFView {
        let pdfView = PDFView()
        pdfView.displayMode = displayMode
        pdfView.displayDirection = displayDirection
        pdfView.autoScales = autoScales
        pdfView.pageShadowsEnabled = pageShadowsEnabled
        pdfView.document = document
        return pdfView
    }

    func updateUIView(_ uiView: PDFView, context: Context) {
        // Update document if it changed (reference comparison)
        if uiView.document !== document {
            uiView.document = document
        }

        if uiView.displayMode != displayMode {
            uiView.displayMode = displayMode
        }

        if uiView.autoScales != autoScales {
            uiView.autoScales = autoScales
        }
    }
}
```

### Convenience Initializers

```swift
extension PDFViewer {
    /// Load a PDF from a URL (local file or remote).
    init(url: URL, displayMode: PDFDisplayMode = .singlePageContinuous) {
        self.document = PDFDocument(url: url)
        self.displayMode = displayMode
    }

    /// Load a PDF from raw data.
    init(data: Data, displayMode: PDFDisplayMode = .singlePageContinuous) {
        self.document = PDFDocument(data: data)
        self.displayMode = displayMode
    }
}
```

### Usage

```swift
struct DocumentView: View {
    let pdfURL: URL

    var body: some View {
        PDFViewer(url: pdfURL)
            .ignoresSafeArea(edges: .bottom)
            .navigationTitle("Document")
            .navigationBarTitleDisplayMode(.inline)
    }
}
```

### With Async Loading

```swift
struct RemotePDFView: View {
    let url: URL
    @State private var document: PDFDocument?
    @State private var isLoading = true
    @State private var errorMessage: String?

    var body: some View {
        Group {
            if let document {
                PDFViewer(document: document)
            } else if isLoading {
                ProgressView("Loading PDF...")
            } else if let errorMessage {
                ContentUnavailableView(
                    "Could Not Load PDF",
                    systemImage: "doc.text.fill",
                    description: Text(errorMessage)
                )
            }
        }
        .task {
            do {
                let (data, _) = try await URLSession.shared.data(from: url)
                document = PDFDocument(data: data)
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
```

### PDFView with Page Navigation

```swift
struct NavigablePDFView: UIViewRepresentable {
    let document: PDFDocument?
    @Binding var currentPageIndex: Int

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> PDFView {
        let pdfView = PDFView()
        pdfView.displayMode = .singlePageContinuous
        pdfView.autoScales = true
        pdfView.document = document

        NotificationCenter.default.addObserver(
            context.coordinator,
            selector: #selector(Coordinator.pageChanged(_:)),
            name: .PDFViewPageChanged,
            object: pdfView
        )

        return pdfView
    }

    func updateUIView(_ uiView: PDFView, context: Context) {
        if uiView.document !== document {
            uiView.document = document
        }

        // Navigate to page if binding changed externally
        if let doc = uiView.document,
           let page = doc.page(at: currentPageIndex),
           uiView.currentPage != page {
            uiView.go(to: page)
        }
    }

    static func dismantleUIView(_ uiView: PDFView, coordinator: Coordinator) {
        NotificationCenter.default.removeObserver(coordinator)
    }

    final class Coordinator: NSObject {
        var parent: NavigablePDFView

        init(_ parent: NavigablePDFView) { self.parent = parent }

        @objc func pageChanged(_ notification: Notification) {
            guard let pdfView = notification.object as? PDFView,
                  let currentPage = pdfView.currentPage,
                  let document = pdfView.document else { return }
            let index = document.index(for: currentPage)
            if parent.currentPageIndex != index {
                parent.currentPageIndex = index
            }
        }
    }
}
```

### Gotchas

- **`PDFView` inherits from `UIView`.** Use `UIViewRepresentable`, not `UIViewControllerRepresentable`.
- **Document is a reference type.** Use `!==` for identity comparison in `updateUIView` to avoid unnecessary reloads.
- **Page change notifications.** Use `NotificationCenter` with `.PDFViewPageChanged` -- `PDFView` does not use a delegate pattern for page changes.
- **Remove observers in `dismantleUIView`.** Failing to remove `NotificationCenter` observers causes crashes after the view is removed.
- **`autoScales`** fits the PDF to the view width. Disable it if you want the user to start at a specific zoom level.
- **Thread safety.** `PDFDocument` loading can be expensive. Load asynchronously and assign on the main thread.

> **Docs:** [PDFView](https://sosumi.ai/documentation/pdfkit/pdfview) | [PDFKit](https://sosumi.ai/documentation/pdfkit)

---

## 9. MFMessageComposeViewController Wrapper

Present the system SMS/MMS composer with pre-filled recipients, body, and optional attachments. Companion to Recipe 6 (MFMailComposeViewController).

```swift
import SwiftUI
import MessageUI

struct MessageComposer: UIViewControllerRepresentable {
    let recipients: [String]
    let body: String
    var attachments: [MessageAttachment] = []
    var onResult: ((MessageComposeResult) -> Void)?
    @Environment(\.dismiss) private var dismiss

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIViewController(context: Context) -> MFMessageComposeViewController {
        let controller = MFMessageComposeViewController()
        controller.messageComposeDelegate = context.coordinator
        controller.recipients = recipients
        controller.body = body

        for attachment in attachments {
            controller.addAttachmentData(
                attachment.data,
                typeIdentifier: attachment.typeIdentifier,
                filename: attachment.filename
            )
        }

        return controller
    }

    func updateUIViewController(
        _ uiViewController: MFMessageComposeViewController,
        context: Context
    ) {
        // Cannot update message compose after presentation
    }

    final class Coordinator: NSObject, MFMessageComposeViewControllerDelegate {
        let parent: MessageComposer

        init(_ parent: MessageComposer) { self.parent = parent }

        func messageComposeViewController(
            _ controller: MFMessageComposeViewController,
            didFinishWith result: MessageComposeResult
        ) {
            parent.onResult?(result)
            parent.dismiss()
        }
    }
}

struct MessageAttachment {
    let data: Data
    let typeIdentifier: String // UTI, e.g., "public.jpeg"
    let filename: String
}
```

### Usage

```swift
struct InviteView: View {
    @State private var showMessage = false

    var body: some View {
        Button("Send Invite via SMS") {
            guard MFMessageComposeViewController.canSendText() else { return }
            showMessage = true
        }
        .sheet(isPresented: $showMessage) {
            MessageComposer(
                recipients: ["+1234567890"],
                body: "Join me on this app!"
            ) { result in
                switch result {
                case .sent:
                    print("Message sent")
                case .cancelled:
                    print("User cancelled")
                case .failed:
                    print("Message failed")
                @unknown default:
                    break
                }
            }
        }
    }
}
```

### With Image Attachment

```swift
struct SharePhotoView: View {
    @State private var showMessage = false
    let image: UIImage

    var body: some View {
        Button("Send Photo") {
            guard MFMessageComposeViewController.canSendText(),
                  MFMessageComposeViewController.canSendAttachments() else {
                return
            }
            showMessage = true
        }
        .sheet(isPresented: $showMessage) {
            MessageComposer(
                recipients: [],
                body: "Check out this photo!",
                attachments: [
                    MessageAttachment(
                        data: image.jpegData(compressionQuality: 0.8) ?? Data(),
                        typeIdentifier: "public.jpeg",
                        filename: "photo.jpg"
                    )
                ]
            )
        }
    }
}
```

### Gotchas

- **Check `canSendText()` before presenting.** If it returns `false`, do not display `MFMessageComposeViewController`; show fallback UI or disable the message action.
- **Check `canSendAttachments()` before adding attachments.** Not all devices or carriers support MMS attachments.
- **The delegate protocol is `MFMessageComposeViewControllerDelegate`**, not `MFMessageComposeDelegate`. It has a single required method.
- **Cannot update after presentation.** Like `MFMailComposeViewController`, the message composer API does not support changing fields after the controller is shown.
- **iMessage vs. SMS.** The controller automatically uses iMessage when available. You cannot force one protocol over the other.
- **Simulator limitation.** `canSendText()` returns `false` on the simulator. Test on a physical device.

> **Docs:** [MFMessageComposeViewController](https://sosumi.ai/documentation/messageui/mfmessagecomposeviewcontroller) | [MFMessageComposeViewControllerDelegate](https://sosumi.ai/documentation/messageui/mfmessagecomposeviewcontrollerdelegate)
