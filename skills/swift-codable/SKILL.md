---
name: swift-codable
description: "Master serialization and deserialization in Swift with Codable. Use when implementing custom CodingKeys, date/data decoding strategies, polymorphic/mixed collections, lossy array decoding, property wrappers for default values, or bridging Codable with SwiftData/CoreData persistence."
---

# Swift Codable

Encode and decode Swift types with `Codable` (`Encodable` & `Decodable`). Covers custom keys, date/data strategies, polymorphic decoding, default values, and persistence compatibility. Targets Swift 6.3 / iOS 26+.

## Contents

- [Basic Conformance & CodingKeys](#basic-conformance--codingkeys)
- [Decoder Strategies](#decoder-strategies)
- [Custom Encoding & Decoding](#custom-encoding--decoding)
- [Polymorphic & Lossy Decoding](#polymorphic--lossy-decoding)
- [SwiftData & Persistence Boundaries](#swiftdata--persistence-boundaries)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Basic Conformance & CodingKeys

Map serialized JSON field names to Swift property names using `CodingKey`:

```swift
struct UserProfile: Codable {
    let id: UUID
    var displayName: String
    var emailAddress: String

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case emailAddress = "email"
    }
}
```

## Decoder Strategies

Configure decoder strategies rather than writing manual decoding logic:

```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
decoder.dateDecodingStrategy = .iso8601
decoder.dataDecodingStrategy = .base64

let profiles = try decoder.decode([UserProfile].self, from: jsonData)
```

> **Note:** `.convertFromSnakeCase` does not handle acronyms well (e.g. `server_id` becomes `serverId`, but `server_url` becomes `serverUrl` not `serverURL`). Use explicit `CodingKeys` for non-standard mappings.

## Custom Encoding & Decoding

When custom transformations are needed, implement `init(from:)` and `encode(to:)`:

```swift
struct BoundedScore: Codable {
    let score: Int

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let raw = try container.decode(Int.self)
        self.score = min(max(raw, 0), 100)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(score)
    }
}
```

## Polymorphic & Lossy Decoding

- **Lossy Arrays**: Decode valid elements while skipping corrupted items using an unkeyed container try/catch loop.
- **Polymorphic Types**: Decode a discriminator key (e.g. `"type"`) from a parent container, then decode the corresponding concrete type.

See [references/codable-advanced-patterns.md](references/codable-advanced-patterns.md) for complete implementations.

## SwiftData & Persistence Boundaries

SwiftData `@Model` classes can store complex structures that conform to `Codable`. When persisting `Codable` structs:
- Keep data types stable across app updates.
- Provide default values for newly added properties to prevent schema migration crashes.

## Common Mistakes

- **Omitting properties in custom init(from:)**: A custom decoder initializer must initialize all stored properties or compilation fails.
- **Using convertFromSnakeCase with explicit CodingKeys**: The key decoding strategy converts keys before matching `CodingKeys`, leading to double-conversion mismatches.
- **Failing entire collections on one bad item**: In resilient feeds, decode elements lossily rather than throwing on the entire array.
- **Decoding floating point dates without explicit strategies**: Default date decoding expects seconds since 2001; specify `.iso8601` or `.millisecondsSince1970`.
- **Ignoring DecodingError diagnostics**: Inspect `DecodingError.keyNotFound`, `.typeMismatch`, and `.valueNotFound` details for exact debugging.

## Review Checklist

- [ ] Automatic synthesis preferred over manual `init(from:)` where possible
- [ ] Appropriate `dateDecodingStrategy` and `keyDecodingStrategy` configured on decoder
- [ ] Acronyms in snake_case checked for conversion issues
- [ ] Resilient network arrays handle individual element decoding errors
- [ ] Codable models intended for SwiftData maintain stable schema types

## References

- [Advanced Codable patterns](references/codable-advanced-patterns.md) -- mixed arrays, lossy decoding, wrappers, defaults, configuration, and persistence boundaries
- [Codable](https://sosumi.ai/documentation/swift/codable/) -- protocol combining Encodable and Decodable
- [JSONDecoder](https://sosumi.ai/documentation/foundation/jsondecoder/) -- decodes JSON data into Codable types
- [JSONEncoder](https://sosumi.ai/documentation/foundation/jsonencoder/) -- encodes Codable types as JSON data
- [CodingKey](https://sosumi.ai/documentation/swift/codingkey/) -- protocol for encoding/decoding keys
- [JSONDecoder.KeyDecodingStrategy.convertFromSnakeCase](https://sosumi.ai/documentation/foundation/jsondecoder/keydecodingstrategy-swift.enum/convertfromsnakecase) -- snake-case conversion behavior and limitations
- [Encoding and Decoding Custom Types](https://sosumi.ai/documentation/foundation/encoding-and-decoding-custom-types/) -- Apple guide on custom Codable conformance
- [Using JSON with Custom Types](https://sosumi.ai/documentation/foundation/using-json-with-custom-types) -- Apple sample code for JSON patterns
- [Preserving your app's model data across launches](https://sosumi.ai/documentation/swiftdata/preserving-your-apps-model-data-across-launches) -- SwiftData model property compatibility
