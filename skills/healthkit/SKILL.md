---
name: healthkit
description: "Builds HealthKit authorization, sample reads/writes, statistics, background delivery, and workout sessions. Use for Apple Health metrics, charts, HKQuantitySample storage, HKLiveWorkoutBuilder, unit handling, workout recording, or health-data delivery and privacy behavior."
---

# HealthKit

Access, query, and store health and fitness metrics in Apple Health using `HealthKit`. Covers authorization, quantity samples, statistics collection queries, background delivery, and workout sessions. Targets Swift 6.3 / iOS 26+.

## Contents

- [Capabilities and Privacy](#capabilities-and-privacy)
- [Availability and HKHealthStore](#availability-and-hkhealthstore)
- [Query Selection Matrix](#query-selection-matrix)
- [Writing Samples and Units](#writing-samples-and-units)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Capabilities and Privacy

Enable **HealthKit** in Signing & Capabilities. If your app observes updates in the background, enable the **Background Delivery** checkbox.

Declare usage descriptions in `Info.plist`:
- `NSHealthShareUsageDescription`: Required for reading health data.
- `NSHealthUpdateUsageDescription`: Required for writing health data.
- `NSHealthClinicalHealthRecordsShareUsageDescription`: Required if accessing clinical records.

> [!IMPORTANT]
> Request only the exact types needed for the immediate feature. App Review strictly rejects apps requesting unneeded health permissions.

## Availability and HKHealthStore

Always guard initialization with `HKHealthStore.isHealthDataAvailable()`. HealthKit is supported on iPhone, Apple Watch, iPad (iPadOS 17+), and Vision Pro, but unavailable on iPadOS 16 or earlier and managed devices with restrictions.

```swift
guard HKHealthStore.isHealthDataAvailable() else { return }
let healthStore = HKHealthStore() // Single thread-safe shared store
```

## Query Selection Matrix

| Query Type | Best Used For | Execution |
|---|---|---|
| `HKSampleQueryDescriptor` | Raw individual samples with sorting and limits | One-shot async |
| `HKStatisticsQueryDescriptor` | Single aggregate metric (sum, average, min/max) over a date range | One-shot async |
| `HKStatisticsCollectionQueryDescriptor` | Time-series aggregations (daily step charts, hourly heart rate) | One-shot or continuous |
| `HKAnchoredObjectQueryDescriptor` | Incremental synchronization with anchor tokens | One-shot or streaming |
| `HKObserverQuery` | Background delivery triggers when health data changes | Background notification |

## Writing Samples and Units

Always specify compatible `HKUnit`s matching the quantity type. For cumulative metrics (steps, active energy), set start and end dates encompassing the measurement interval; for discrete metrics (heart rate), use identical start and end dates.

## Route by Task

- For statistics collection queries and SwiftUI health chart configurations, read [Statistics and Charts](references/healthkit-patterns.md#statistics-collection-queries).
- For background observation and setting up `enableBackgroundDelivery`, read [Background Delivery](references/healthkit-patterns.md#background-delivery).
- For recording live workouts with `HKWorkoutSession` and `HKLiveWorkoutBuilder`, read [Live Workout Sessions](references/healthkit-patterns.md#workout-sessions).
- For complete HKUnit string formats, conversion, and compound units, read [HKUnit Reference](references/healthkit-patterns.md#hkunit-reference).

## Common Mistakes

- Calling HealthKit APIs without checking `HKHealthStore.isHealthDataAvailable()`.
- Missing `NSHealthShareUsageDescription` or `NSHealthUpdateUsageDescription`, causing immediate crash on launch.
- Creating multiple `HKHealthStore` instances instead of sharing a single instance across the app.
- Assuming read authorization can be inspected (Apple intentionally masks read authorization status for privacy).
- Using incompatible units (e.g. attempting to store step count with `.meter()` instead of `.count()`).

## Review Checklist

- [ ] `HKHealthStore.isHealthDataAvailable()` checked before accessing store
- [ ] Info.plist contains both share and update descriptions
- [ ] HealthKit capability enabled in target signing
- [ ] Read and write authorization requested in separate explicit sets
- [ ] Unit matches target `HKQuantityType` dimension
- [ ] Background delivery enabled with `enableBackgroundDelivery(for:frequency:)`
- [ ] Queries use predicate intervals to prevent scanning full lifetime history
- [ ] UI gracefully handles devices where HealthKit is unavailable (e.g. iPadOS 16)

## References

- [HealthKit extended query patterns and workout builders](references/healthkit-patterns.md)
- [HealthKit documentation](https://sosumi.ai/documentation/healthkit)
- [HKHealthStore](https://sosumi.ai/documentation/healthkit/hkhealthstore)
- [HKQuantityType](https://sosumi.ai/documentation/healthkit/hkquantitytype)
- [HKWorkoutSession](https://sosumi.ai/documentation/healthkit/hkworkoutsession)
