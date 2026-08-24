---
name: pdfkit
description: "Display and manipulate PDF documents using PDFKit. Use when embedding PDFView to show PDF files, creating or modifying PDFDocument instances, adding annotations (highlights, notes, signature widgets), extracting text with PDFSelection, navigating pages, generating thumbnails, filling PDF forms, or wrapping PDFView in SwiftUI."
---

# PDFKit

Display, navigate, search, annotate, and manipulate PDF documents with `PDFView`, `PDFDocument`, `PDFPage`, `PDFAnnotation`, and `PDFSelection`.

## Workflow

1. Load the document safely, handle password/invalid data, and define who owns mutations and saves.
2. Configure `PDFView` display, scaling, navigation, and observation for the actual product surface.
3. Perform search, selection, annotation, form, thumbnail, or page operations with PDF coordinate conversion in mind.
4. Keep SwiftUI representable identity stable and strongly own weak delegates/providers.
5. Save to a deliberate destination and verify reload, rotation, large files, protected files, and annotation persistence.

## Route by Task

- Read [core implementation details](references/core-implementation.md) for loading, viewing, navigation, search, annotations, thumbnails, SwiftUI integration, and page overlays.
- Read [extended PDFKit patterns](references/pdfkit-patterns.md) for forms, watermarks, merging, printing, outlines, custom drawing, and overlay lifecycle recipes.

## Core Decisions

- Never assume `PDFDocument` initialization succeeds or that a protected document is unlocked.
- Convert between view and page coordinates before placing or hit-testing annotations.
- Keep PDF mutations serialized and update UI-facing state on the main actor.
- Avoid representable update loops caused by comparing document objects or rebuilding the view.

## Common Mistakes

### DON'T: Force-unwrap PDFDocument init

`PDFDocument(url:)` and `PDFDocument(data:)` are failable initializers.

```swift
// WRONG
let document = PDFDocument(url: url)!

// CORRECT
guard let document = PDFDocument(url: url) else { return }
```

### DON'T: Forget autoScales on PDFView

Without `autoScales`, the PDF renders at its native resolution.

```swift
// WRONG
pdfView.document = document

// CORRECT
pdfView.autoScales = true
pdfView.document = document
```

### DON'T: Ignore PDF coordinate system in annotations

PDF page coordinates have origin at the bottom-left with Y increasing
upward -- opposite of UIKit.

```swift
// WRONG: UIKit coordinates
let bounds = CGRect(x: 50, y: 50, width: 200, height: 30)

// CORRECT: PDF coordinates (origin bottom-left)
let pageBounds = page.bounds(for: .mediaBox)
let pdfY = pageBounds.height - 50 - 30
let bounds = CGRect(x: 50, y: pdfY, width: 200, height: 30)
```

### DON'T: Modify annotations on a background thread

PDFKit classes are not thread-safe.

```swift
// WRONG
DispatchQueue.global().async { page.addAnnotation(annotation) }

// CORRECT
DispatchQueue.main.async { page.addAnnotation(annotation) }
```

### DON'T: Compare PDFDocument with == in UIViewRepresentable

`PDFDocument` is a reference type. Use identity (`!==`).

```swift
// WRONG: Always replaces document
func updateUIView(_ pdfView: PDFView, context: Context) {
    pdfView.document = document
}

// CORRECT
func updateUIView(_ pdfView: PDFView, context: Context) {
    if pdfView.document !== document {
        pdfView.document = document
    }
}
```

## Review Checklist

- [ ] `PDFDocument` init uses optional binding, not force-unwrap
- [ ] `pdfView.autoScales = true` set for proper initial display
- [ ] Page indices checked against `pageCount` before access
- [ ] `displayMode` and `displayDirection` configured to match design
- [ ] Annotations use PDF coordinate space (origin bottom-left, Y up)
- [ ] All PDFKit mutations happen on the main thread
- [ ] Password-protected PDFs handled with `isLocked` / `unlock(withPassword:)`
- [ ] SwiftUI wrapper uses `!==` identity check in `updateUIView`
- [ ] `PDFViewPageChanged` notification observed for page tracking
- [ ] `PDFThumbnailView.pdfView` linked to the main `PDFView`
- [ ] Large-document search uses async `beginFindString` with delegate
- [ ] Saved documents use `write(to:withOptions:)` when encryption needed

## References

- Extended patterns (forms, watermarks, merging, printing, overlays, outlines, custom drawing): [references/pdfkit-patterns.md](references/pdfkit-patterns.md)
- [PDFKit framework](https://sosumi.ai/documentation/pdfkit)
- [PDFView](https://sosumi.ai/documentation/pdfkit/pdfview)
- [PDFDocument](https://sosumi.ai/documentation/pdfkit/pdfdocument)
- [PDFPage](https://sosumi.ai/documentation/pdfkit/pdfpage), [PDFAnnotation](https://sosumi.ai/documentation/pdfkit/pdfannotation), [PDFSelection](https://sosumi.ai/documentation/pdfkit/pdfselection), [PDFThumbnailView](https://sosumi.ai/documentation/pdfkit/pdfthumbnailview)
- [PDFPageOverlayViewProvider](https://sosumi.ai/documentation/pdfkit/pdfpageoverlayviewprovider)
- [Adding Widgets to a PDF Document](https://sosumi.ai/documentation/pdfkit/adding-widgets-to-a-pdf-document)
- [Adding Custom Graphics to a PDF](https://sosumi.ai/documentation/pdfkit/adding-custom-graphics-to-a-pdf)
- [Core implementation details](references/core-implementation.md) -- setup, API wiring, and focused implementation recipes moved out of the entrypoint.
