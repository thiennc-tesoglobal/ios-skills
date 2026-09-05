---
name: paperkit
description: "Add drawings, shapes, and a consistent markup experience using PaperKit. Use when integrating PaperMarkupViewController for markup editing, adding shape recognition, working with PaperMarkup data models, embedding markup tools in document editors, or building annotation features that need the system-standard markup toolbar. New in iOS 26."
---

# PaperKit

Combine freeform PencilKit drawings with structured markup elements (shapes, text boxes, images, connectors) using `PaperKit` (`PaperMarkupViewController`, `PaperMarkup`). Targets Swift 6.3 / iOS 26+.

> **Beta-sensitive:** PaperKit is new in iOS/iPadOS 26, macOS 26, and visionOS 26. Verify availability guards and SDK versions before production release.

## Contents

- [PaperKit Architecture](#paperkit-architecture)
- [PencilKit vs PaperKit Boundary](#pencilkit-vs-paperkit-boundary)
- [Core Components](#core-components)
- [Persistence and Feature Sets](#persistence-and-feature-sets)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## PaperKit Architecture

PaperKit provides an interactive document canvas hosting both vector PencilKit strokes and structured document annotations.

```
┌────────────────────────────────────────────────────────┐
│            PaperMarkupViewController                   │
│  ┌───────────────────────┐  ┌────────────────────────┐ │
│  │   PKToolPicker        │  │ MarkupEditController   │ │
│  │  (PencilKit Inking)   │  │ (Shapes, Text, Images) │ │
│  └───────────────────────┘  └────────────────────────┘ │
│                                                        │
│  Canvas: PaperMarkup (Strokes + Shapes + Text Objects) │
└────────────────────────────────────────────────────────┘
```

## PencilKit vs PaperKit Boundary

- **`pencilkit`**: Use for pure freehand sketchbooks, drawing-only canvases, raw vector stroke analysis, or when supporting iOS 17 and earlier.
- **`paperkit`**: Use when users need to place shapes, typed text, sticky notes, or signature annotations alongside freehand drawings in document editors.

## Core Components

| Component | Role |
|---|---|
| `PaperMarkupViewController` | Scrollable interactive markup canvas hosting drawings and elements |
| `PaperMarkup` | Serializable document model representing canvas elements and bounds |
| `MarkupEditViewController` | System UI for inserting shapes, text, arrows, and signatures |
| `MarkupToolbarViewController` | Toolbar controller coordinating tools on desktop and iPad |
| `FeatureSet` | Capability configuration declaring supported tools and element types |

## Persistence and Feature Sets

1. **Serialization**: Save and restore `PaperMarkup` using `markup.dataRepresentation()`.
2. **FeatureSet Compatibility**: Initialize view controllers with explicit feature sets (e.g. `FeatureSet.latest` or targeted subsets) to prevent forward-compatibility loading errors.
3. **Thumbnail Rendering**: Generate raster thumbnail previews off the main thread for fast document list loading.

## Route by Task

- For full UIKit setup, delegate lifecycle, and embedding in parent controllers, read [PaperMarkupViewController Setup](references/paperkit-patterns.md#papermarkupviewcontroller-setup).
- For SwiftUI integration with `UIViewControllerRepresentable`, read [SwiftUI PaperKit Integration](references/paperkit-patterns.md#swiftui-integration).
- For custom tool picker coordination and first-responder management, read [Tool Picker Coordination](references/paperkit-patterns.md#tool-picker-coordination).
- For document serialization, thumbnail generation, and backward compatibility, read [Persistence and Thumbnails](references/paperkit-patterns.md#persistence-and-thumbnails).

## Common Mistakes

- Presenting markup insertion controllers without anchoring to a valid bar button or source rect.
- Recreating `PaperMarkupViewController` on every SwiftUI view update rather than using coordinator pattern.
- Performing `PaperMarkup` serialization synchronously on the main thread for large multi-element documents.
- Omitting availability checks (`@available(iOS 26.0, *)`) when deploying to earlier OS versions.
- Failing to synchronize document bounds between `PaperMarkup` and the hosting view layout.

## Review Checklist

- [ ] `PaperMarkupViewController` hosted in a stable UIKit container or SwiftUI Coordinator
- [ ] Availability guarded for iOS 26+
- [ ] Insertion controllers properly anchored to source views or bar button items
- [ ] `PKToolPicker` added as observer to the paper markup controller
- [ ] Document serialization performed asynchronously in background tasks
- [ ] Undo and redo actions integrated with the canvas `UndoManager`

## References

- [PaperKit extended recipes and SwiftUI wrappers](references/paperkit-patterns.md)
- [PaperKit documentation](https://sosumi.ai/documentation/paperkit)
- [PencilKit documentation](https://sosumi.ai/documentation/pencilkit)
