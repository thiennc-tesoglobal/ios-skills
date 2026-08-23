# Common Swift Review Checks

> Adapted and rewritten for this collection; see [../NOTICE.md](../NOTICE.md).

Use these checks to find runtime hazards, not to enforce a personal style. A
pattern is a finding only when the value can vary at runtime, the ownership graph
can form a cycle, or the API contract is misleading.

## Optionals and collection access

```swift
// Runtime input: the invariant is not proven.
let url = URL(string: userInput)!       // possible crash
let first = response.items.first!      // possible empty collection
let value = dictionary["key"]!         // possible missing key

guard let url = URL(string: userInput) else {
    return reportInvalidInput()
}
let first = response.items.first
let value = dictionary["key", default: fallback]
```

Verify the actual source of the value before flagging `!`. A force unwrap can be
reasonable when a local invariant is explicit and testable (for example, a
validated literal URL), but an asset lookup, environment value, decoded payload,
or user input is still runtime data. Prefer optional binding, a throwing API, or
an explicit precondition whose failure is intentionally fatal.

Also check for the misleading nil-check-then-unwrap pattern:

```swift
if optionalString != nil {
    print(optionalString!.count)
}
```

Use `if let`/`guard let` so the value checked is the value used. For collections,
confirm that an index is valid at the point of access; `.first`, `.last`, or a
domain-specific missing-item path is safer than assuming a non-empty collection.

## Ownership and closures

```swift
final class Controller {
    var onComplete: (() -> Void)?

    func installHandler() {
        onComplete = { [weak self] in
            self?.refresh()
        }
    }
}
```

A stored closure that captures its owner strongly can form a cycle, but
`[weak self]` is not a universal fix: a task or callback may intentionally keep
an operation alive, and weak capture can make work disappear before completion.
Trace who stores the closure, how long it should live, and who cancels or clears
it. Prefer capturing immutable dependencies when that makes ownership clearer.

Use `weak` for a delegate only when the protocol is class-bound and the ownership
graph requires a non-owning reference. Do not flag a strong delegate without
checking whether the delegate is a value type, an external owner, or intentionally
retained. Use `unowned` only when the lifetime relationship is proven; otherwise
it turns a lifetime bug into a crash.

## Implicitly unwrapped optionals

`IBOutlet` properties are a framework convention, but ordinary `String!`, model,
service, and image properties deserve the same scrutiny as other optionals. If a
value is required, initialize it before use; if it is genuinely absent, model it
as `T?` and handle the absent case.

## API names and contracts

Use Swift API Design Guidelines for naming and argument labels. Flag names when
they obscure side effects, contradict mutating/nonmutating behavior, or misstate
the ownership/error contract—not merely because another spelling is preferred.
Route a broad API naming audit to `swift-api-design-guidelines`.

## Questions before reporting

1. Can the value really be nil, empty, or out of bounds on a supported path?
2. Is a force unwrap backed by a local invariant that the code proves?
3. Who stores this closure/delegate/task, and who releases or cancels it?
4. Could framework lifecycle or dynamic dispatch call this symbol even if search
   finds no direct reference?
5. Is the proposed change a correctness fix or only a style preference?

## Primary references

- [Optional](https://sosumi.ai/documentation/swift/optional)
- [Collection](https://sosumi.ai/documentation/swift/collection)
- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
