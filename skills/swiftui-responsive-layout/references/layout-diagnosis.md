# Layout Diagnosis and Verification

Use this reference when a view clips, overlaps, moves off-screen, or changes unexpectedly during rotation, resizing, text growth, or keyboard presentation.

## Diagnose the Contract

Record the exact failing context before changing code:

- device or Simulator and current window dimensions
- full screen, Split View, Slide Over, Stage Manager, sheet, popover, tab, or navigation container
- portrait or landscape and whether the failure appears during transition
- Dynamic Type size, locale, layout direction, Display Zoom, and keyboard state
- content values that create the longest or emptiest layout

Then inspect from the nearest stable container toward the failing child. For each boundary ask:

1. What size does the parent propose?
2. What ideal or fixed size does the child require?
3. Which sibling wins when space is compressed?
4. Does an overlay reserve space or only paint above content?
5. Has a safe area been ignored or replaced?
6. Does measured geometry update state that changes the measurement itself?

## Symptom Map

| Symptom | Likely causes | First checks |
|---|---|---|
| Text or buttons clip horizontally | fixed width, one-line label, competing `HStack` children | text limits, child frames, layout priority, axis adaptation |
| Bottom rows hide behind a bar | overlay, tab/navigation chrome, ignored safe area | `safeAreaInset`, scroll content inset, actual container |
| Form fields hide behind keyboard | fixed vertical layout, disabled keyboard safe area, non-scrollable form | keyboard state, scroll container, focused field path |
| iPad layout fails only in multitasking | device-model branch, assumed regular width, fixed column count | live window width, size class changes, adaptive grid minimum |
| Layout flickers near a breakpoint | geometry feedback, rounding noise, mutually changing branches | measurement boundary, transformed value, hysteresis or fit-based alternative |
| State resets when resizing | duplicated conditional trees or unstable identity | `AnyLayout`, stable IDs, branch ownership |
| One locale overflows | width tuned to source language, rigid buttons, forced single line | longest translations, wrapping, RTL, content-driven variants |
| Preview works but app overlaps | missing navigation/tab/sheet container or different safe area | reproduce in the actual hierarchy and Simulator |

## Fix Review

Prefer removing a false constraint over adding compensation elsewhere. A local offset can align one configuration while making the layout more fragile in every other configuration.

Reject a proposed fix if it:

- branches on device model or static screen bounds
- shrinks essential text to preserve a fixed composition
- clips overflow without preserving access to content
- duplicates an entire stateful subtree for a cosmetic arrangement change
- publishes raw geometry through a feature-wide model
- disables safe-area behavior for unrelated descendants
- changes navigation or feature architecture without evidence that layout requires it

## Verification Matrix

Test the smallest matrix that covers the feature's supported contexts, including the original failure:

| Dimension | Required representatives |
|---|---|
| Width | narrow iPhone, wide iPhone, narrow iPad multitasking, regular iPad window |
| Height and orientation | portrait, landscape, and live rotation where supported |
| Text | default plus at least one accessibility Dynamic Type size |
| Content | longest localized labels, multiline values, empty/error states |
| Direction | left-to-right and right-to-left when localization is supported |
| System UI | actual tab/navigation/sheet container, safe areas, software keyboard |
| Transition | resize or rotate while focus, selection, scroll position, or entered text is active |

Use deterministic previews for fast iteration, then verify the affected flow in Simulator. A successful compile does not prove that content remains visible or interactive. Capture screenshots or other runtime evidence for the failing and corrected configurations when the task requires delivery proof.

Route build, launch, orientation, appearance, and screenshot mechanics to `ios-simulator`. Route formal accessibility behavior and assistive-technology testing to `ios-accessibility`.
