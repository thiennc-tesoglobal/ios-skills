---
name: energykit
description: "Query grid electricity forecasts and submit load events using EnergyKit to help users optimize home electricity usage. Use when building smart home apps, EV charger controls, HVAC scheduling, or energy management dashboards that guide users to use power during cleaner or cheaper grid periods."
---

# EnergyKit

Query electricity cleanliness and cost forecasts and report device load telemetry using EnergyKit to help users shift power consumption to cleaner or cheaper grid periods. Targets Swift 6.3 / iOS 26+.

> **Beta-sensitive:** Core EnergyKit APIs require iOS/iPadOS 26.0+. iOS/iPadOS 27+ APIs (`ElectricalLoadDevice`, Home app LoadEvents integration) are beta-sensitive.

## Contents

- [Capabilities and Entitlements](#capabilities-and-entitlements)
- [Core Architecture](#core-architecture)
- [Action and Rating Semantics](#action-and-rating-semantics)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Capabilities and Entitlements

All EnergyKit use requires the `com.apple.developer.energykit` entitlement. Enable the **EnergyKit** capability on your app target.

| Target Platform | Required Capabilities | Key APIs |
|---|---|---|
| iOS/iPadOS 26.x | EnergyKit | `ElectricityGuidance.Service`, `deviceID:` parameter |
| iOS/iPadOS 27+ | EnergyKit (+ EnergyKit LoadEvents for Home app) | `ElectricalLoadDevice`, `ElectricityInsightService` |

Handle `EnergyKitError.permissionDenied` when authorization is missing and `EnergyKitError.unsupportedRegion` outside supported grid territories (contiguous US).

## Core Architecture

1. **Electricity Guidance**: Time-weighted forecast stream telling apps when electricity is cleaner and less expensive.
   - Use `.shift` for schedulable workloads (EV charging, battery storage).
   - Use `.reduce` for curtailment workloads (HVAC thermostat setbacks).
2. **Load Events**: Telemetry submitted by managed devices confirming actual consumption timing. Submissions must match the venue where guidance was received.
3. **Energy Venues**: Physical locations (`EnergyVenue`) registered in the user's Apple Home environment.

## Action and Rating Semantics

- Guidance ratings range from `0.0` (dirtiest/costliest) to `1.0` (cleanest/cheapest).
- The guidance stream emits continuous intervals. Always observe updates because grid forecasts change dynamically with weather and demand spikes.
- Submit load events promptly after consumption completes so historical insights reflect accurate savings.

## Route by Task

- For guidance query streams, SwiftUI chart bindings, and venue discovery, read [Observing Electricity Guidance](references/energykit-patterns.md#observing-electricity-guidance).
- For submitting EV charger (`ElectricVehicleLoadEvent`) and HVAC (`ElectricHVACLoadEvent`) telemetry, read [Submitting Load Events](references/energykit-patterns.md#submitting-load-events).
- For historical consumption records, cost breakdowns, and tariff analysis with `ElectricityInsightService`, read [Electricity Insights](references/energykit-patterns.md#electricity-insights).
- For Home app integration on iOS 27+ and device metadata, read [Home App Integration](references/energykit-patterns.md#home-app-integration).

## Common Mistakes

- Missing `com.apple.developer.energykit` entitlement, causing silent failures or `.permissionDenied`.
- Assuming global coverage without handling `EnergyKitError.unsupportedRegion`.
- Submitting load events with mismatched device or venue identifiers.
- Failing to observe guidance updates dynamically, leaving stale charging schedules in place.
- Using iOS 27 `ElectricalLoadDevice` without availability checks on iOS 26 deployment targets.

## Review Checklist

- [ ] `com.apple.developer.energykit` entitlement enabled on app target
- [ ] Regional availability handled gracefully (`EnergyKitError.unsupportedRegion`)
- [ ] Query action matches device behavior (`.shift` for EV/batteries, `.reduce` for HVAC)
- [ ] Load events submitted promptly with accurate start/end timestamps and watt-hours
- [ ] Guidance values normalized and mapped to user-facing cleaner/cheaper indicators
- [ ] iOS 27+ LoadEvents capability gated behind appropriate availability checks

## References

- [EnergyKit implementation recipes and load event telemetry](references/energykit-patterns.md)
- [EnergyKit documentation](https://sosumi.ai/documentation/energykit)
- [ElectricityGuidance](https://sosumi.ai/documentation/energykit/electricityguidance)
- [EnergyVenue](https://sosumi.ai/documentation/energykit/energyvenue)
