---
name: weatherkit
description: "Fetch WeatherKit current, minute, hourly, and daily forecasts; weather alerts; iOS 18+ changes, historical comparisons, summaries, and statistics; and required Apple Weather attribution. Use when integrating weather data, showing forecasts or alerts, caching WeatherKit responses, displaying attribution, or reviewing WeatherKit query limits in iOS apps."
---

# WeatherKit

Fetch current conditions, hourly and daily forecasts, weather alerts, and historical statistics using `WeatherService`. Displays mandatory Apple Weather attribution.

## Contents

- [Setup & Permissions](#setup--permissions)
- [Fetching Weather Data](#fetching-weather-data)
- [Selective Queries](#selective-queries)
- [Context & Historical Queries (iOS 18+)](#context--historical-queries-ios-18)
- [Attribution Requirements](#attribution-requirements)
- [Caching & Rate Limits](#caching--rate-limits)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Setup & Permissions

1. Enable the **WeatherKit** capability in Xcode.
2. Enable WeatherKit for your App ID in the Apple Developer portal.
3. Add `NSLocationWhenInUseUsageDescription` to Info.plist if requesting coordinates via CoreLocation.
4. Use `WeatherService.shared` across the app.

## Fetching Weather Data

Fetch complete weather datasets for a target `CLLocation`:

```swift
import WeatherKit
import CoreLocation

let weather = try await WeatherService.shared.weather(for: location)

// Current conditions
let current = weather.currentWeather
print("Temperature: \(current.temperature.formatted())")
print("Condition: \(current.condition.description), SF Symbol: \(current.symbolName)")

// Hourly and Daily forecasts
for hour in weather.hourlyForecast.prefix(12) {
    print("\(hour.date.formatted(date: .omitted, time: .shortened)): \(hour.temperature.formatted())")
}
```

Format `Measurement<UnitTemperature>` values with `.formatted()` to honor user locale conventions.

## Selective Queries

Reduce bandwidth and processing by requesting only necessary datasets:

```swift
let (current, hourly) = try await WeatherService.shared.weather(
    for: location,
    including: .current, .hourly
)
```

Available query types include `.current`, `.hourly`, `.daily`, `.minute`, and `.alerts`.

## Context & Historical Queries (iOS 18+)

Access climate context, historical comparisons, and weather summaries:

```swift
// Query weather changes (e.g. temperature shift since yesterday)
let changes = try await WeatherService.shared.weather(for: location, including: .changes)

// Historical comparison
let historical = try await WeatherService.shared.weather(for: location, including: .historicalComparisons)
```

## Attribution Requirements

Apple requires visible attribution whenever WeatherKit data is displayed:

```swift
let attribution = try await WeatherService.shared.attribution
// Display attribution.combinedMark (light/dark Apple Weather logo)
// Provide tappable link to attribution.legalPageURL
```

In SwiftUI, display attribution using `Link` and the official logo asset.

## Caching & Rate Limits

- Respect `metadata.expirationDate` returned with forecasts; avoid refetching unexpired data.
- Batch requests by coordinates and debounce location updates to stay within API tier allowances.

## Common Mistakes

- **Omitting mandatory Apple Weather attribution**: App Store review rejects apps displaying WeatherKit data without legal attribution and logo.
- **Ignoring forecast expiration dates**: Calling `weather(for:)` on every view appearance causes rate-limiting errors. Respect `metadata.expirationDate`.
- **Hardcoding temperature unit conversion**: Manually calculating Fahrenheit/Celsius ignores system locale. Use `temperature.formatted()`.
- **Requesting all datasets when only current weather is needed**: Increases network latency. Use selective `including:` queries.
- **Missing Apple Developer WeatherKit entitlement**: WeatherKit calls fail if the capability is not enabled in the developer portal.

## Review Checklist

- [ ] WeatherKit capability enabled in Xcode and Developer Portal
- [ ] Required Apple Weather attribution logo and legal link displayed
- [ ] Temperatures formatted via `Measurement.formatted()`
- [ ] Selective queries (`including:`) used to minimize network payload
- [ ] Forecasts cached and refreshed according to `metadata.expirationDate`

## References

- Extended patterns (SwiftUI dashboard, charts integration, historical statistics): [references/weatherkit-patterns.md](references/weatherkit-patterns.md)
- [WeatherKit framework](https://sosumi.ai/documentation/weatherkit)
- [WeatherService](https://sosumi.ai/documentation/weatherkit/weatherservice)
- [WeatherAttribution](https://sosumi.ai/documentation/weatherkit/weatherattribution)
- [WeatherQuery](https://sosumi.ai/documentation/weatherkit/weatherquery)
- [WeatherQuery.daily(startDate:endDate:)](https://sosumi.ai/documentation/weatherkit/weatherquery/daily(startdate:enddate:))
- [WeatherQuery.hourly(startDate:endDate:)](https://sosumi.ai/documentation/weatherkit/weatherquery/hourly(startdate:enddate:))
- [CurrentWeather](https://sosumi.ai/documentation/weatherkit/currentweather)
- [CurrentWeather.temperature](https://sosumi.ai/documentation/weatherkit/currentweather/temperature)
- [Measurement.formatted()](https://sosumi.ai/documentation/foundation/measurement/formatted())
- [Forecast](https://sosumi.ai/documentation/weatherkit/forecast)
- [HourWeather](https://sosumi.ai/documentation/weatherkit/hourweather)
- [DayWeather](https://sosumi.ai/documentation/weatherkit/dayweather)
- [WeatherAlert](https://sosumi.ai/documentation/weatherkit/weatheralert)
- [WeatherAvailability](https://sosumi.ai/documentation/weatherkit/weatheravailability)
- [WeatherMetadata.expirationDate](https://sosumi.ai/documentation/weatherkit/weathermetadata/expirationdate)
- [WeatherQuery.changes](https://sosumi.ai/documentation/weatherkit/weatherquery/changes)
- [WeatherQuery.historicalComparisons](https://sosumi.ai/documentation/weatherkit/weatherquery/historicalcomparisons)
- [WeatherKit updates](https://sosumi.ai/documentation/updates/weatherkit)
- [Bring context to today's weather](https://sosumi.ai/videos/play/wwdc2024/10067)
- [WeatherService.weather(for:)](https://sosumi.ai/documentation/weatherkit/weatherservice/weather(for:))
