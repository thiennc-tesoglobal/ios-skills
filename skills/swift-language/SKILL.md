---
name: swift-language
description: "Apply modern Swift language patterns to non-SwiftUI, non-concurrency code, including expressions, typed throws, generics, protocols, result builders, property wrappers, opaque and existential types, regexes, and collections. Route concurrency, Codable, formatting, and API naming to their specialist skills."
---

# Swift Language Patterns

Apply modern Swift 6.3 syntax and idioms without altering behavior or evaluation order. Route concurrency to `swift-concurrency`, deep serialization to `swift-codable`, formatting to `swift-formatstyle`, naming to `swift-api-design-guidelines`, and SwiftUI state to `swiftui-patterns`.

## Contents

- [Expressions & Control Flow](#expressions--control-flow)
- [Typed Throws (Swift 6+)](#typed-throws-swift-6)
- [Opaque vs Existential Types](#opaque-vs-existential-types)
- [Result Builders & Property Wrappers](#result-builders--property-wrappers)
- [Modern Collections & Regex](#modern-collections--regex)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Expressions & Control Flow

Use value-producing `if` and `switch` expressions for direct assignment, initialization, and single-expression returns:

```swift
// Direct variable initialization from expression
let statusColor = switch order.status {
case .pending: Color.orange
case .completed: Color.green
case .failed: Color.red
}

let badge = if isFeatured { "star.fill" } else { "circle" }
```

Every branch must produce identical value types without multi-statement bodies.

## Typed Throws (Swift 6+)

Specify concrete error types when callers benefit from exhaustive compile-time error handling:

```swift
enum PaymentError: Error {
    case cardExpired, insufficientFunds
}

func processPayment() throws(PaymentError) {
    guard hasFunds else { throw .insufficientFunds }
}

// Caller error handling is exhaustive without casting
do {
    try processPayment()
} catch {
    switch error {
    case .cardExpired: promptNewCard()
    case .insufficientFunds: promptDeposit()
    }
}
```

Use `throws(Never)` for non-throwing conformance in generic protocols. For mixed or open error sources, retain untyped `throws`.

## Opaque vs Existential Types

- **`some Protocol` (Opaque)**: Preferred for return and parameter types. Preserves underlying static type information, enables compiler optimizations, and avoids existential container allocation overhead.
- **`any Protocol` (Existential)**: Use only when dynamic heterogeneous collections or runtime polymorphism is explicitly required (e.g. `[any Plugin]`).

```swift
// Parameter pack / opaque parameter
func render(item: some Displayable) { ... }

// Heterogeneous collection requires existential boxing
let plugins: [any Plugin] = [AudioPlugin(), VisualPlugin()]
```

## Result Builders & Property Wrappers

- **`@resultBuilder`**: Construct declarative DSLs by implementing `buildBlock`, `buildOptional`, and `buildEither`.
- **`@propertyWrapper`**: Encapsulate reusable property storage or validation via `wrappedValue` and projected `projectedValue` (`$`).

```swift
@propertyWrapper
struct Clamped<T: Comparable> {
    var value: T
    let range: ClosedRange<T>

    var wrappedValue: T {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
}
```

## Modern Collections & Regex

- Use regex literals `#/pattern/#` with typed capture groups and `RegexBuilder`.
- Leverage Swift collection operations: `contains(where:)`, `allSatisfy`, `min(by:)`, and non-mutating transformations.

## Common Mistakes

- **Defaulting to `any` instead of `some`**: Using `any Protocol` incurs existential boxing costs and suppresses type relationship inference. Prefer `some Protocol`.
- **Overusing typed throws for general errors**: Forcing `throws(MyError)` on functions that wrap URLSession or system APIs requires fragile error translation. Use untyped `throws` for mixed errors.
- **Multi-statement branches in expressions**: `if`/`switch` expressions only evaluate single-expression branches. Multi-line logic requires traditional statements.
- **Forgetting parentheses in function calls**: Wrap expression arguments in parentheses when passing to functions to avoid parsing ambiguity.
- **Modifying evaluation order during refactoring**: When modernizing with expressions, ensure parameter evaluation order remains strictly preserved.

## Review Checklist

- [ ] Value-producing `if`/`switch` used for concise variable initialization
- [ ] `throws(SpecificError)` used only where callers genuinely need exhaustive handling
- [ ] `some Protocol` chosen over `any Protocol` unless heterogeneous storage is required
- [ ] Regex patterns use modern regex literals or `RegexBuilder`
- [ ] Property wrappers maintain thread safety and avoid re-entrant side effects

## References

- Extended patterns and Codable examples: [references/swift-patterns-extended.md](references/swift-patterns-extended.md)
- Attributes and C interop: [references/swift-attributes-interop.md](references/swift-attributes-interop.md)
