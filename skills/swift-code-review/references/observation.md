# Swift Observation and SwiftUI State

> Adapted and rewritten for this collection; see [../NOTICE.md](../NOTICE.md).

Review ownership and invalidation separately. `@State`, `@Bindable`, and
`@Environment` are not interchangeable wrappers, and a model being observable
does not make every nested reference observable.

## Ownership with `@State`

For an `@Observable` reference type, `@State` is appropriate when the view owns
the model identity and its lifetime:

```swift
@Observable final class EditorModel {
    var title = ""
}

struct EditorView: View {
    @State private var model = EditorModel()

    var body: some View { Text(model.title) }
}
```

Do not claim that SwiftUI recreates the stored model on every body evaluation.
The view value and the state storage have different lifetimes. Instead, inspect
whether the initializer has expensive side effects, whether a parent should own
the identity, and whether a new input is being ignored because `@State` keeps
the first value.

## Child ownership and bindings

A child that receives an existing model should not put it in `@State` merely to
make it available; that changes ownership and can preserve the first instance.
Use a plain property for read-only access, or `@Bindable` when controls need a
two-way binding:

```swift
struct EditView: View {
    @Bindable var model: EditorModel

    var body: some View {
        TextField("Title", text: $model.title)
    }
}
```

For an environment-provided observable, read it with `@Environment` and create
a local bindable projection inside `body`:

```swift
struct SettingsView: View {
    @Environment(AppSettings.self) private var settings

    var body: some View {
        @Bindable var settings = settings
        Toggle("Dark Mode", isOn: $settings.darkMode)
    }
}
```

## Observation boundaries

Mark a property `@ObservationIgnored` only when it should not participate in
view invalidation (for example, a logger, repository, or cache that is accessed
outside rendered state). Verify that ignored changes cannot affect what the view
renders. A property wrapper does not automatically make its wrapped value
observable.

If a model stores a reference whose mutable properties are read by a view, that
nested reference should participate in Observation or explicitly publish changes
through the owning model. Do not flag a nested type merely because it is not
annotated: first check which properties the view reads and how mutations are
propagated.

`withObservationTracking` invokes `onChange` when a tracked property is about to
change and the tracking registration is one-shot. Re-register tracking for
continued observation and schedule work on the actor that owns the model; do not
assume a global `DispatchQueue.main` hop is the correct fix.

## Migration review

| Combine-era pattern | Observation-era direction |
|---|---|
| `ObservableObject` / `@Published` | `@Observable` and stored properties |
| `@StateObject` | `@State` when the view owns the observable identity |
| `@ObservedObject` | Plain property for reads, `@Bindable` for bindings |
| `@EnvironmentObject` | `@Environment(Type.self)` for an injected observable |

Do not recommend migration just because a project uses Combine. Check deployment
targets, existing publisher contracts, and whether the change is in scope.

## Questions before reporting

1. Who owns the observable identity and what happens when the input instance
   changes?
2. Is `@State` preserving state intentionally, or hiding a parent-owned model?
3. Does a control need `@Bindable`, or is a read-only property enough?
4. Are ignored and nested properties truly outside the rendered observation graph?
5. Is observation re-registered and isolated on the model’s actor?

## Primary references

- [Observation framework](https://sosumi.ai/documentation/observation)
- [Observable macro](https://sosumi.ai/documentation/observation/observable%28%29)
- [ObservationIgnored macro](https://sosumi.ai/documentation/observation/observationignored%28%29)
- [withObservationTracking](https://sosumi.ai/documentation/observation/withobservationtracking%28_:onchange:%29)
- [SwiftUI State](https://sosumi.ai/documentation/swiftui/state)
- [SwiftUI Bindable](https://sosumi.ai/documentation/swiftui/bindable)
