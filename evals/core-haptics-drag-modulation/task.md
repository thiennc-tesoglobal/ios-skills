# Drag-Driven Haptic Texture

## Problem/Feature Description

An iPhone mixing app has a vertical intensity control. While a finger is down, the
control should produce a continuous texture: moving upward increases intensity and
moving right makes it sharper. The interaction must remain usable on unsupported
hardware, stop immediately when the gesture ends or cancels, and recover after an
audio interruption or app backgrounding.

## Output Specification

Create a file named `drag-haptic-design.md` containing:

- the engine and player ownership design;
- concise Swift 6.3 snippets for setup, playback, live updates, cancellation, and reset;
- fallback and power-management behavior;
- a physical-device verification checklist.

Do not create an Xcode project or replace the custom texture with a standard feedback
generator.
