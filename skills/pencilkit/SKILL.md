---
name: pencilkit
description: "Implement drawing, handwriting, and sketching with PencilKit and PaperKit. Use when integrating PKCanvasView, configuring PKToolPicker, handling drawing gestures and Apple Pencil features, inspecting or rendering strokes, managing drawing data, or building drawing interfaces."
---

# PencilKit

Integrate drawing, sketching, and annotation into iOS and iPadOS apps using `PencilKit` (`PKCanvasView`, `PKToolPicker`, `PKDrawing`) and `PaperKit`. Targets Swift 6.3 / iOS 26+.

## Contents

- [Core PencilKit Architecture](#core-pencilkit-architecture)
- [SwiftUI Integration Pattern](#swiftui-integration-pattern)
- [Drawing Persistence and Data](#drawing-persistence-and-data)
- [Input Policy and Gestures](#input-policy-and-gestures)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Core PencilKit Architecture

| Component | Responsibility |
|---|---|
| `PKCanvasView` | Scrollable drawing canvas that receives touch and pencil inputs; inherits from `UIScrollView` |
| `PKToolPicker` | Floating system tool palette offering pens, pencils, markers, erasers, rulers, and custom tools |
| `PKDrawing` | Immutable data model containing vector strokes (`PKStroke`), stroke points, and bounds |
| `PKTool` | Active drawing instrument (`PKInkingTool`, `PKEraserTool`, `PKLassoTool`) |
| `PKCanvasViewDelegate` | Notifies when drawing changes or user starts/ends drawing |

## SwiftUI Integration Pattern

Bridge `PKCanvasView` into SwiftUI using `UIViewRepresentable`:

```swift
import SwiftUI
import PencilKit

struct CanvasViewRepresentable: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var tool: PKTool = PKInkingTool(.pen, color: .black, width: 5)
    var isRulerActive: Bool = false

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.drawingPolicy = .anyInput
        canvas.tool = tool
        canvas.isRulerActive = isRulerActive
        canvas.delegate = context.coordinator
        return canvas
    }

    func updateUIView(_ uiView: PKCanvasView, context: Context) {
        if uiView.drawing != drawing {
            uiView.drawing = drawing
        }
        uiView.tool = tool
        uiView.isRulerActive = isRulerActive
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, PKCanvasViewDelegate {
        var parent: CanvasViewRepresentable
        init(_ parent: CanvasViewRepresentable) { self.parent = parent }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            Task { @MainActor in parent.drawing = canvasView.drawing }
        }
    }
}
```

## Drawing Persistence and Data

- **Serialization**: Serialize drawings using `drawing.dataRepresentation()`. Restore via `PKDrawing(data:)`.
- **Image Generation**: Render drawings to raster images with `drawing.image(from: canvasView.bounds, scale: canvasView.traitCollection.displayScale)`.
- **Stroke Inspection**: Iterate through `drawing.strokes` to inspect points, pressure, force, and azimuth.

## Input Policy and Gestures

Configure `canvasView.drawingPolicy`:
- `.default`: Follows system preference (Apple Pencil only if configured in Settings).
- `.anyInput`: Allows finger drawing alongside Apple Pencil.
- `.pencilOnly`: Restricts drawing strictly to Apple Pencil; finger touches scroll the canvas.

Coordinating `PKToolPicker`: Attach the picker with `toolPicker.setVisible(true, forFirstResponder: canvasView)` and `toolPicker.addObserver(canvasView)`. Ensure the canvas becomes first responder.

## Route by Task

- For tracking tool picker changes, visibility, and frame obstruction, read [Tool Picker Observer Pattern](references/pencilkit-patterns.md#tool-picker-observer-pattern).
- For custom items in `PKToolPicker` (iOS 18+), read [Custom Tool Picker Items](references/pencilkit-patterns.md#custom-tool-picker-items).
- For stroke construction, comparison, and shape recognition, read [Constructing Strokes Programmatically](references/pencilkit-patterns.md#constructing-strokes-programmatically).
- For thumbnail generation and background image rendering, read [Thumbnail Generation](references/pencilkit-patterns.md#thumbnail-generation).
- For undo/redo coordination with `UndoManager`, read [Undo/Redo Support](references/pencilkit-patterns.md#undoredo-support).

## Common Mistakes

- Forgetting to call `canvasView.becomeFirstResponder()` before showing `PKToolPicker`.
- Updating SwiftUI `@Binding var drawing` continuously during drawing gestures, causing hitching and feedback loops.
- Overriding finger scrolling gestures without setting `drawingPolicy = .pencilOnly`.
- Generating high-resolution raster images synchronously on the main thread from complex drawings.
- Assuming `PKToolPicker` floats automatically in SwiftUI without anchoring to a window or first responder.

## Review Checklist

- [ ] `PKCanvasView` embedded in SwiftUI with a clean Coordinator
- [ ] `drawingPolicy` explicitly set (`.anyInput`, `.pencilOnly`, or `.default`)
- [ ] `PKToolPicker` tied to canvas first responder and visible state
- [ ] Drawing data serialized with `dataRepresentation()` and restored with error handling
- [ ] Raster image rendering performed asynchronously or off the main thread for large canvases
- [ ] Undo and redo actions integrated with the canvas's `undoManager`
- [ ] Dynamic Type and safe area insets respected when `PKToolPicker` obscures canvas regions

## References

- [PencilKit extended patterns and stroke inspection](references/pencilkit-patterns.md)
- [PencilKit documentation](https://sosumi.ai/documentation/pencilkit)
- [PKCanvasView](https://sosumi.ai/documentation/pencilkit/pkcanvasview)
- [PKToolPicker](https://sosumi.ai/documentation/pencilkit/pktoolpicker)
- [PKDrawing](https://sosumi.ai/documentation/pencilkit/pkdrawing-swift.struct)
