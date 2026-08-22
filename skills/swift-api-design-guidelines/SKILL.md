---
name: swift-api-design-guidelines
description: "Apply Swift API Design Guidelines to names, argument labels, mutating/nonmutating pairs, protocols, and documentation comments. Use when designing or reviewing Swift APIs for clarity at the call site; file and project organization belongs to the relevant architecture/UI skill."
---

# Swift API Design Guidelines

Design APIs that read clearly at the call site and communicate semantic roles rather than implementation details.

## Scope and Compatibility

This skill owns Swift declaration names, argument labels, mutating/nonmutating pairs, protocol naming, casing, overload clarity, and documentation comments. Route language/type-system mechanics to `swift-language`, concurrency semantics to `swift-concurrency`, lint configuration to `swiftlint`, and project/file naming to the relevant architecture or UI skill.

Preserve source compatibility when it is part of the request. Before renaming public API, inspect access level, protocol requirements, generated interfaces, call sites, and whether a deprecation/forwarding period is needed. Verify version-specific language behavior in primary Swift sources.

## Call-Site Test

Read every proposed call as a sentence. Keep words that clarify the role of an argument; remove words that merely repeat its type or the declaration context.

Use the first applicable rule:

| Situation | Label strategy |
|---|---|
| Value-preserving conversion initializer | Omit first label |
| Indistinguishable peer values such as `min(x, y)` | Omit peer labels |
| First argument completes the base-name phrase | Omit or fold words into the base name |
| Argument begins a prepositional phrase | Use that preposition as the label |
| General case | Use a role-based label |

Read [Argument Labels and Parameters](references/argument-labels-and-parameters.md) for grammatical/prepositional edge cases, conversions, peers, defaults, and multi-argument abstractions.

## Side Effects and Pairs

- Use imperative verbs for mutating operations: `sort()`, `append(_:)`.
- Name nonmutating results with a noun/adjective or grammatical participle: `sorted()`, `appending(_:)`.
- For noun operations, use the noun for the returned value and `form` plus noun for mutation: `union(_:)` / `formUnion(_:)`.
- Use `make` for factories when creation is the semantic action.
- Name Boolean properties and methods as assertions: `isEmpty`, `contains(_:)`.

Read [Side Effects and Mutating Pairs](references/side-effects-and-mutating-pairs.md) when `-ed` versus `-ing`, `form`, Boolean, or factory grammar is unclear.

## Names and Protocols

- Name variables and parameters by role, not type.
- Prefer terms established by the domain and use one word for one concept.
- Avoid abbreviations unless they are conventional and unambiguous.
- Name protocols describing a thing as nouns; name capability protocols with an appropriate `-able`, `-ible`, or `-ing` form.
- Prefer methods/properties when there is a natural `self`; use free functions for symmetric peers, unconstrained generic operations, or established notation.
- Avoid overloads distinguishable only by return type.

Read [Naming and Clarity](references/naming-and-clarity.md) for role names, terminology, weak-type compensation, and fluent usage.

## Documentation

Public API should have concise documentation that states purpose, parameters, return value, thrown errors, side effects, and relevant complexity. Function summaries describe what the operation does; type/property summaries describe what the declaration is.

Document non-constant complexity when callers could reasonably assume O(1). Use symbol links and parameter markup supported by DocC. Do not restate the declaration in prose.

Read [Conventions and Special Rules](references/conventions-and-special-rules.md) for casing, complexity, tuples, closure labels, overloads, and documentation edge cases.

## Review Checklist

- [ ] The call reads naturally with values substituted
- [ ] Labels describe semantic roles and do not repeat type information
- [ ] Side-effect and mutating/nonmutating names are grammatical
- [ ] Boolean APIs read as assertions
- [ ] Names use consistent domain terminology
- [ ] Protocol names communicate thing versus capability semantics
- [ ] Defaults simplify one API instead of creating redundant method families
- [ ] Overloads remain unambiguous without relying on return type
- [ ] Public documentation explains behavior, errors, side effects, and non-O(1) complexity where relevant
- [ ] Public renames include an appropriate compatibility strategy

## References

- [Naming clarity and terminology](references/naming-and-clarity.md)
- [Argument labels and parameters](references/argument-labels-and-parameters.md)
- [Side effects and mutating pairs](references/side-effects-and-mutating-pairs.md)
- [Casing, documentation, overloads, tuples, and closures](references/conventions-and-special-rules.md)
