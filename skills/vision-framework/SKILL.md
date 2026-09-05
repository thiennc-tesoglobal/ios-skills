---
name: vision-framework
description: "Builds or reviews iOS computer-vision features with Vision and VisionKit, including OCR, barcode and document scanning, face/object detection, segmentation, tracking, and Core ML inference. Use for Vision requests, live DataScanner flows, or Vision/Core ML integration."
---

# Vision Framework

Detect text, faces, barcodes, objects, contours, and poses in images and live video using Apple's on-device computer vision frameworks (`Vision` and `VisionKit`). Targets Swift 6.3 / iOS 26+.

## Contents

- [Two API Generations](#two-api-generations)
- [Modern Request Architecture](#modern-request-architecture)
- [Normalized Coordinates vs Pixel Space](#normalized-coordinates-vs-pixel-space)
- [Core ML Integration](#core-ml-integration)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Two API Generations

| Dimension | Modern Vision (iOS 18+) | Legacy Vision (pre-iOS 18) |
|---|---|---|
| Request Types | Swift structs (`RecognizeTextRequest`, `DetectBarcodesRequest`) | ObjC classes (`VNRecognizeTextRequest`, `VNDetectBarcodesRequest`) |
| Execution | `try await request.perform(on: image)` | `VNImageRequestHandler(cgImage:).perform([request])` |
| Results | Strongly typed observation arrays | `request.results as? [VNBarcodeObservation]` |
| Concurrency | Native async/await | Completion handlers or synchronous blocking calls |

Prefer modern Swift-native request structs for new code. Maintain legacy handlers only when supporting deployment targets below iOS 18.

## Modern Request Architecture

All modern requests conform to `ImageProcessingRequest`:
```swift
import Vision

var request = RecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = [Locale.Language(identifier: "en-US")]

let observations = try await request.perform(on: cgImage)
for observation in observations {
    print("Found text: \(observation.topCandidates(1).first?.string ?? "")")
}
```

## Normalized Coordinates vs Pixel Space

Vision observations express bounding boxes in normalized coordinates `(0.0...1.0)` with origin at the **bottom-left** corner (Cartesian), while UIKit/SwiftUI places origin at the **top-left**.

To convert to UIKit/SwiftUI coordinates:
```swift
let rect = VNImageRectForNormalizedRect(observation.boundingBox, Int(viewWidth), Int(viewHeight))
// Flip Y-axis: y = viewHeight - rect.origin.y - rect.size.height
```

## Core ML Integration

Run custom Core ML vision models using `CoreMLModelContainer`:
1. Compile model (`.mlpackage` or `.mlmodelc`).
2. Wrap with `CoreMLModelContainer(model: compiledModel)`.
3. Create image request: `var request = ImageFeaturePrintRequest()` or custom Core ML classification request.

## Route by Task

- For OCR text recognition, barcode scanning, face detection, person segmentation, and object tracking, read [Vision Requests and Detectors](references/vision-requests.md).
- For live camera scanner UI, document scanning, and optical barcode flows with `DataScannerViewController`, read [VisionKit Scanner](references/visionkit-scanner.md).

## Common Mistakes

- Forgetting to invert the Y-axis when projecting normalized Vision bounding boxes onto UIKit/SwiftUI views.
- Running heavy Vision requests (`.accurate` text recognition) synchronously on the main thread.
- Passing `UIImage` directly without extracting `cgImage` or preserving image orientation metadata.
- Using `DataScannerViewController` without checking `DataScannerViewController.isSupported` and `isAvailable`.
- Retaining stateful tracking requests (`TrackObjectRequest`) across unrelated image sequences.

## Review Checklist

- [ ] Modern request types (`RecognizeTextRequest`) preferred on iOS 18+ targets
- [ ] Image orientation properly passed to `perform(on:orientation:)`
- [ ] Vision bounding box coordinates converted and Y-flipped for SwiftUI rendering
- [ ] Camera scanner checks `DataScannerViewController.isSupported` before presentation
- [ ] Heavy processing executed on background tasks off `@MainActor`
- [ ] Bounding boxes clamped to image bounds before cropping

## References

- [Vision requests, legacy VNRequest patterns, and Core ML integration](references/vision-requests.md)
- [VisionKit DataScannerViewController and document scanner](references/visionkit-scanner.md)
- [Vision documentation](https://sosumi.ai/documentation/vision)
- [VisionKit documentation](https://sosumi.ai/documentation/visionkit)
- [RecognizeTextRequest](https://sosumi.ai/documentation/vision/recognizetextrequest)
