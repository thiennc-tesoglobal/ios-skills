# Project Structure and File Naming

Use this reference when creating a feature, reorganizing an existing SwiftUI project, or reviewing filenames and source boundaries. Preserve the project's established organization when it is coherent; structure changes are not permission to rewrite behavior.

## Choose Structure by Project Size

For a small prototype, a flat source folder can be clearer than premature hierarchy. Introduce feature folders when screens, models, or supporting views become difficult to find or several features evolve independently.

For a medium or growing app, prefer feature-first organization with small shared layers:

```text
App/
  ProductApp.swift
DesignSystem/
  AppTheme.swift
Models/
  TodoItem.swift
Features/
  Dashboard/
    TodoDashboardView.swift
    DashboardHeaderView.swift
    TodoListSection.swift
  Editor/
    TodoEditorView.swift
    TodoCategoryPicker.swift
Services/
  TodoRepository.swift
```

Do not add empty `ViewModels`, `Repositories`, `UseCases`, or `Coordinators` folders merely to resemble an architecture. Add a layer when it owns real behavior or establishes a useful dependency boundary.

## Naming

- Name the app entry point after the product: `FlowApp`, not `todoApp` or `AppMainView`.
- Name screens by domain and role: `TodoDashboardView`, `TodoEditorView`.
- Name reusable pieces by what they present or do: `ProgressSummaryView`, `TodoItemRow`.
- Match the filename to its primary type.
- Use the product prefix for brand/design-system concepts and the domain prefix for feature concepts; do not prefix every type mechanically.
- Avoid generic production names such as `ContentView`, `MainView`, `Helper`, `Manager`, or `Utils` when a concrete role is known.

Swift API naming belongs to `swift-api-design-guidelines`; this reference covers file and project discoverability.

## File Boundaries

A dedicated file is usually justified when a type:

- owns state, focus, gestures, a task, or lifecycle behavior
- has meaningful branching or substantial layout
- is independently previewable or testable
- is shared across multiple parents
- has a clear responsibility that would otherwise be hidden in a large file

Keep tiny private types and one-off stateless fragments with their parent when separating them would make navigation harder. Line count is a signal, not a rule.

One primary production type per file is a useful default, not an absolute requirement. Closely related private support types may remain together. Split domain enums or styles when they have independent ownership, substantial behavior, or reuse.

## Composition Root

A screen root should make the hierarchy and data flow obvious. It may own queries, route state, orchestration, and feature-level actions, while child views own presentation and local interaction details.

Avoid these pseudo-boundaries:

- a 500-line screen divided only by `// MARK:`
- screen-sized computed `some View` properties
- extensions that hide state and side effects without narrowing dependencies
- a single `Theme.swift` that accumulates unrelated services, models, formatting, and UI
- one file per three-line private fragment

## Refactor Contract

Before moving code, pin:

- layout and navigation
- state ownership and bindings
- model identity
- accessibility labels, actions, and focus order
- animation and side-effect timing
- persistence behavior

Move one meaningful boundary at a time, build after risky or compiler-visible changes, and compare the same preview or simulator state. Do not combine structural cleanup with visual redesign unless the user requested both.

## Xcode Integration

Respect the project's group and file-synchronization model. When source folders are filesystem-synchronized, add files under the synchronized root. For explicit PBX groups, ensure new files are added to the correct target and build phase. A file existing on disk is not proof that Xcode compiles it.
