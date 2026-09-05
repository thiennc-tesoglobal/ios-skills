# PDF Generation, Forms, and Printing

Use this reference when generating PDFs with UIGraphicsPDFRenderer, filling AcroForms, watermarking pages, merging documents, and printing via UIPrintInteractionController.

## Contents

- [Form Filling](#form-filling)
- [Creating PDFs Programmatically](#creating-pdfs-programmatically)
- [Watermarks](#watermarks)
- [Merging Documents](#merging-documents)
- [Printing](#printing)

---

## Form Filling

PDF forms use widget annotations. Each widget has a `fieldName`, a
`widgetFieldType`, and a `widgetStringValue`.

### Reading Form Fields

```swift
func extractFormFields(from document: PDFDocument) -> [(name: String, value: String)] {
    var fields: [(String, String)] = []
    for pageIndex in 0..<document.pageCount {
        guard let page = document.page(at: pageIndex) else { continue }
        for annotation in page.annotations {
            guard annotation.widgetFieldType == .text,
                  let name = annotation.fieldName else { continue }
            fields.append((name, annotation.widgetStringValue ?? ""))
        }
    }
    return fields
}
```

### Filling Text Fields

```swift
func fillTextField(in document: PDFDocument, fieldName: String, value: String) {
    for pageIndex in 0..<document.pageCount {
        guard let page = document.page(at: pageIndex) else { continue }
        for annotation in page.annotations {
            if annotation.widgetFieldType == .text,
               annotation.fieldName == fieldName {
                annotation.widgetStringValue = value
                return
            }
        }
    }
}
```

### Filling Checkbox Fields

```swift
func setCheckbox(in document: PDFDocument, fieldName: String, checked: Bool) {
    for pageIndex in 0..<document.pageCount {
        guard let page = document.page(at: pageIndex) else { continue }
        for annotation in page.annotations {
            if annotation.widgetFieldType == .button,
               annotation.widgetControlType == .checkBoxControl,
               annotation.fieldName == fieldName {
                annotation.buttonWidgetState = checked ? .onState : .offState
                return
            }
        }
    }
}
```

### Creating Widget Annotations

```swift
// Text field widget
func createTextField(
    bounds: CGRect,
    fieldName: String,
    placeholder: String = ""
) -> PDFAnnotation {
    let widget = PDFAnnotation(bounds: bounds, forType: .widget, withProperties: nil)
    widget.widgetFieldType = .text
    widget.fieldName = fieldName
    widget.widgetStringValue = placeholder
    widget.font = UIFont.systemFont(ofSize: 12)
    widget.backgroundColor = UIColor.systemGray6
    return widget
}

// Checkbox widget
func createCheckbox(bounds: CGRect, fieldName: String) -> PDFAnnotation {
    let widget = PDFAnnotation(bounds: bounds, forType: .widget, withProperties: nil)
    widget.widgetFieldType = .button
    widget.widgetControlType = .checkBoxControl
    widget.fieldName = fieldName
    widget.buttonWidgetState = .offState
    return widget
}

// Radio button widget
func createRadioButton(
    bounds: CGRect,
    groupName: String,
    stateString: String
) -> PDFAnnotation {
    let widget = PDFAnnotation(bounds: bounds, forType: .widget, withProperties: nil)
    widget.widgetFieldType = .button
    widget.widgetControlType = .radioButtonControl
    widget.fieldName = groupName
    widget.buttonWidgetStateString = stateString
    return widget
}

// Choice widget (dropdown)
func createDropdown(
    bounds: CGRect,
    fieldName: String,
    options: [String]
) -> PDFAnnotation {
    let widget = PDFAnnotation(bounds: bounds, forType: .widget, withProperties: nil)
    widget.widgetFieldType = .choice
    widget.fieldName = fieldName
    widget.choices = options
    widget.isListChoice = false  // false = dropdown, true = list box
    return widget
}
```

### Building a Simple Form

```swift
func buildForm() -> PDFDocument {
    let document = PDFDocument()
    let page = PDFPage()
    let pageBounds = CGRect(x: 0, y: 0, width: 612, height: 792) // Letter size
    page.setBounds(pageBounds, for: .mediaBox)

    // Name field
    let nameField = createTextField(
        bounds: CGRect(x: 100, y: 700, width: 200, height: 24),
        fieldName: "name",
        placeholder: ""
    )
    page.addAnnotation(nameField)

    // Agree checkbox
    let checkbox = createCheckbox(
        bounds: CGRect(x: 100, y: 660, width: 20, height: 20),
        fieldName: "agree"
    )
    page.addAnnotation(checkbox)

    document.insert(page, at: 0)
    return document
}
```

## Creating PDFs Programmatically

### From Images

```swift
func createPDFFromImages(_ images: [UIImage]) -> PDFDocument {
    let document = PDFDocument()
    for (index, image) in images.enumerated() {
        if let page = PDFPage(image: image) {
            document.insert(page, at: index)
        }
    }
    return document
}
```

### From Images with Options

```swift
func createPDFFromImage(
    _ image: UIImage,
    mediaBox: CGRect? = nil,
    compressionQuality: CGFloat = 0.8
) -> PDFPage? {
    var options: [PDFPage.ImageInitializationOption: Any] = [
        .compressionQuality: compressionQuality
    ]
    if let box = mediaBox {
        options[.mediaBox] = NSValue(cgRect: box)
    }
    return PDFPage(image: image, options: options)
}
```

### Using Core Graphics

For full control over PDF layout, use `UIGraphicsPDFRenderer`.

```swift
func createPDFWithCoreGraphics() -> Data {
    let pageRect = CGRect(x: 0, y: 0, width: 612, height: 792)
    let renderer = UIGraphicsPDFRenderer(bounds: pageRect)

    return renderer.pdfData { context in
        context.beginPage()

        // Draw title
        let title = "Document Title"
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.boldSystemFont(ofSize: 24),
            .foregroundColor: UIColor.black
        ]
        title.draw(at: CGPoint(x: 50, y: 50), withAttributes: titleAttributes)

        // Draw body text
        let body = "This is the body text of the PDF document."
        let bodyAttributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 12),
            .foregroundColor: UIColor.darkGray
        ]
        let bodyRect = CGRect(x: 50, y: 100, width: 512, height: 600)
        body.draw(in: bodyRect, withAttributes: bodyAttributes)

        // Draw a line
        context.cgContext.setStrokeColor(UIColor.gray.cgColor)
        context.cgContext.setLineWidth(1)
        context.cgContext.move(to: CGPoint(x: 50, y: 90))
        context.cgContext.addLine(to: CGPoint(x: 562, y: 90))
        context.cgContext.strokePath()
    }
}
```

### Loading Core Graphics PDF into PDFDocument

```swift
let pdfData = createPDFWithCoreGraphics()
let document = PDFDocument(data: pdfData)
```

## Watermarks

Add watermarks by subclassing `PDFPage` and overriding `draw(with:to:)`.

### Text Watermark

```swift
class WatermarkedPage: PDFPage {
    var watermarkText: String = "CONFIDENTIAL"

    override func draw(with box: PDFDisplayBox, to context: CGContext) {
        super.draw(with: box, to: context)

        UIGraphicsPushContext(context)
        context.saveGState()

        let pageBounds = bounds(for: box)
        let center = CGPoint(x: pageBounds.midX, y: pageBounds.midY)

        // Rotate around center
        context.translateBy(x: center.x, y: center.y)
        context.rotate(by: -.pi / 4)  // -45 degrees
        context.translateBy(x: -center.x, y: -center.y)

        let attributes: [NSAttributedString.Key: Any] = [
            .font: UIFont.boldSystemFont(ofSize: 72),
            .foregroundColor: UIColor.red.withAlphaComponent(0.15)
        ]

        let textSize = watermarkText.size(withAttributes: attributes)
        let textOrigin = CGPoint(
            x: center.x - textSize.width / 2,
            y: center.y - textSize.height / 2
        )
        watermarkText.draw(at: textOrigin, withAttributes: attributes)

        context.restoreGState()
        UIGraphicsPopContext()
    }
}
```

### Applying Watermarks via Document Delegate

```swift
class WatermarkDelegate: NSObject, PDFDocumentDelegate {
    func classForPage() -> AnyClass {
        WatermarkedPage.self
    }
}

// Usage
let delegate = WatermarkDelegate()
document.delegate = delegate
pdfView.document = document
```

### Image Watermark

```swift
class ImageWatermarkedPage: PDFPage {
    var watermarkImage: UIImage?

    override func draw(with box: PDFDisplayBox, to context: CGContext) {
        super.draw(with: box, to: context)

        guard let image = watermarkImage?.cgImage else { return }

        let pageBounds = bounds(for: box)
        let imageSize = CGSize(width: 200, height: 200)
        let imageRect = CGRect(
            x: pageBounds.midX - imageSize.width / 2,
            y: pageBounds.midY - imageSize.height / 2,
            width: imageSize.width,
            height: imageSize.height
        )

        context.saveGState()
        context.setAlpha(0.1)
        context.draw(image, in: imageRect)
        context.restoreGState()
    }
}
```

## Merging Documents

### Append All Pages

```swift
func mergeDocuments(_ documents: [PDFDocument]) -> PDFDocument {
    let merged = PDFDocument()
    var insertIndex = 0
    for document in documents {
        for pageIndex in 0..<document.pageCount {
            guard let page = document.page(at: pageIndex) else { continue }
            merged.insert(page, at: insertIndex)
            insertIndex += 1
        }
    }
    return merged
}
```

### Extract Page Range

```swift
func extractPages(
    from document: PDFDocument,
    range: ClosedRange<Int>
) -> PDFDocument {
    let extracted = PDFDocument()
    var insertIndex = 0
    for pageIndex in range {
        guard pageIndex >= 0,
              pageIndex < document.pageCount,
              let page = document.page(at: pageIndex) else { continue }
        extracted.insert(page, at: insertIndex)
        insertIndex += 1
    }
    return extracted
}
```

### Split Document

```swift
func splitDocument(_ document: PDFDocument, pagesPerChunk: Int) -> [PDFDocument] {
    var chunks: [PDFDocument] = []
    var chunkDoc = PDFDocument()
    var chunkIndex = 0

    for pageIndex in 0..<document.pageCount {
        guard let page = document.page(at: pageIndex) else { continue }
        chunkDoc.insert(page, at: chunkIndex)
        chunkIndex += 1

        if chunkIndex >= pagesPerChunk {
            chunks.append(chunkDoc)
            chunkDoc = PDFDocument()
            chunkIndex = 0
        }
    }

    if chunkDoc.pageCount > 0 {
        chunks.append(chunkDoc)
    }

    return chunks
}
```

## Printing

### Using UIPrintInteractionController

```swift
func printPDF(document: PDFDocument, from viewController: UIViewController) {
    guard let data = document.dataRepresentation() else { return }

    let printController = UIPrintInteractionController.shared
    let printInfo = UIPrintInfo(dictionary: nil)
    printInfo.outputType = .general
    printInfo.jobName = "PDF Document"

    printController.printInfo = printInfo
    printController.printingItem = data
    printController.present(animated: true)
}
```

### Print a Specific Page Range

```swift
func printPageRange(
    document: PDFDocument,
    range: ClosedRange<Int>,
    from viewController: UIViewController
) {
    let subset = extractPages(from: document, range: range)
    guard let data = subset.dataRepresentation() else { return }

    let printController = UIPrintInteractionController.shared
    let printInfo = UIPrintInfo(dictionary: nil)
    printInfo.outputType = .general
    printController.printInfo = printInfo
    printController.printingItem = data
    printController.present(animated: true)
}
```

