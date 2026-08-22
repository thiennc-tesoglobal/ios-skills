---
name: swiftdata
description: "Implement or review SwiftData models, containers, queries, relationships, migrations, CloudKit configuration, and background persistence work. Use for SwiftData-backed storage; route legacy Core Data-only work to core-data."
---

# SwiftData

Design persistence so model identity, relationships, query cost, migration, and context ownership remain explicit.

## Scope and Compatibility

This skill owns `@Model`, `ModelContainer`, `ModelContext`, `@Query`, predicates, fetch descriptors, schema migration, `@ModelActor`, and SwiftData/CloudKit constraints. Route pure Core Data work to `core-data`, UI state wiring to `swiftui-patterns`, and general actor diagnostics to `swift-concurrency`.

Inspect deployment target, Xcode/Swift toolchain, enabled capabilities, and the existing schema before recommending APIs. Preserve the current store and migration path unless the user explicitly authorizes a reset. Verify availability and CloudKit constraints against SDK headers and primary Apple documentation.

## Workflow

1. Inventory models, unique identity, relationships, delete rules, constraints, indexes, and current store configuration.
2. Identify context ownership and every write path.
3. Choose query and mutation APIs based on data size, UI liveness, and isolation.
4. If the schema changes, define a migration and test it with a copy of representative data.
5. Build and verify create, fetch, update, delete, relaunch persistence, failure handling, and any sync behavior in scope.

## Models and Relationships

- Keep durable domain values persistable and give identity stable semantics.
- Model both sides of important relationships and choose delete rules deliberately.
- Avoid adding uniqueness, indexes, or nonoptional properties to an existing store without a migration plan.
- Keep computed/transient presentation data out of the persisted schema unless persistence has product value.
- Use transformable or external storage only after considering queryability, migration, CloudKit, and file-lifecycle costs.

Read [SwiftData Advanced](references/swiftdata-advanced.md) for relationships, schema versions, migrations, CloudKit, and advanced container configuration. Read [Indexing](references/indexing.md) before adding indexes or compound uniqueness.

## Containers and Contexts

Install one deliberate root container for an app/scene unless isolation or testing requires another. Inject it into SwiftUI and use in-memory or temporary configurations for previews and tests.

`ModelContext` is not a general-purpose cross-actor value. Keep UI writes on the UI-owned context. Use `@ModelActor` or another context created for background persistence work, and pass stable identifiers or `PersistentIdentifier` values across isolation boundaries rather than live model objects.

Save behavior must be explicit enough for the feature: decide whether a user action saves immediately, a transaction batches changes, or autosave is sufficient. Do not silently swallow persistence errors in production paths where data loss matters.

## Queries

Use `@Query` when a SwiftUI view owns a live query whose predicate and sort shape are suitable for property-wrapper construction. Use `FetchDescriptor` for imperative, reusable, paginated, or actor-owned fetches.

Push filtering and sorting into the store when practical. In-memory filtering is acceptable for a proven small dataset or UI-only transformation, not as a default workaround for predicate limitations.

Read [Queries](references/swiftdata-queries.md) for `@Query`, `FetchDescriptor`, sorting, pagination, and dynamic query patterns. Read [Predicate Pitfalls](references/predicate-pitfalls.md) before debugging optional relationships, captured values, enums, or unsupported expressions.

## Migration and Coexistence

Treat schema evolution as a product-data change. Test lightweight and custom stages from the actual previous schema, including failure and rollback/recovery expectations. Never delete the user's store merely to make a migration pass unless the user has explicitly accepted data loss.

Read [Core Data Coexistence](references/core-data-coexistence.md) when both frameworks share a product or when planning an incremental migration.

## Review Checklist

- [ ] Stable identity, relationships, inverses, and delete rules are intentional
- [ ] Container and context ownership are explicit
- [ ] No live model object crosses actors unsafely
- [ ] Query work is performed by the store when practical
- [ ] Save and error behavior matches product expectations
- [ ] Schema changes include a tested migration path
- [ ] CloudKit-compatible schema/configuration is verified when sync is enabled
- [ ] Previews and tests use isolated stores
- [ ] CRUD and relaunch persistence are verified
- [ ] Destructive store resets require explicit authorization

## References

- [Advanced models, relationships, migrations, and CloudKit](references/swiftdata-advanced.md)
- [Queries and fetch descriptors](references/swiftdata-queries.md)
- [Predicate pitfalls](references/predicate-pitfalls.md)
- [Indexing and uniqueness](references/indexing.md)
- [Core Data coexistence and migration](references/core-data-coexistence.md)
