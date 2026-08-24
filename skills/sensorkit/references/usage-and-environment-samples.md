# SensorKit Usage and Environment Samples

Read this reference only when the task matches the sections below.

## Keyboard Metrics Deep Dive

`SRKeyboardMetrics` provides extensive typing analytics:

### Basic Metrics

```swift
func processKeyboardMetrics(_ result: SRFetchResult<AnyObject>) {
    guard let metrics = result.sample as? SRKeyboardMetrics else { return }

    // Session info
    let duration = metrics.duration
    let keyboardID = metrics.keyboardIdentifier
    let inputModes = metrics.inputModes  // Active languages
    let sessions = metrics.sessionIdentifiers

    // Quantitative metrics
    let totalWords = metrics.totalWords
    let totalTaps = metrics.totalTaps
    let totalDeletes = metrics.totalDeletes
    let totalEmojis = metrics.totalEmojis
    let totalAutoCorrections = metrics.totalAutoCorrections
    let typingSpeed = metrics.typingSpeed  // Characters per second

    // Keyboard dimensions
    let width = metrics.width   // Measurement<UnitLength>
    let height = metrics.height // Measurement<UnitLength>

    print("Session: \(duration)s, \(totalWords) words at \(typingSpeed) chars/sec")
}
```

### Correction Metrics

```swift
func analyzeCorrections(_ metrics: SRKeyboardMetrics) {
    let corrections = [
        "Auto": metrics.totalAutoCorrections,
        "Space": metrics.totalSpaceCorrections,
        "Retro": metrics.totalRetroCorrections,
        "Transposition": metrics.totalTranspositionCorrections,
        "Insert key": metrics.totalInsertKeyCorrections,
        "Skip touch": metrics.totalSkipTouchCorrections,
        "Near key": metrics.totalNearKeyCorrections,
        "Substitution": metrics.totalSubstitutionCorrections,
        "Hit test": metrics.totalHitTestCorrections
    ]

    for (type, count) in corrections where count > 0 {
        print("\(type) corrections: \(count)")
    }
}
```

### Sentiment Analysis

```swift
func analyzeSentiment(_ metrics: SRKeyboardMetrics) {
    let categories: [SRKeyboardMetrics.SentimentCategory] = [
        .positive, .sad, .anger, .anxiety,
        .confused, .down, .lowEnergy, .health,
        .death, .absolutist
    ]

    for category in categories {
        let wordCount = metrics.wordCount(for: category)
        let emojiCount = metrics.emojiCount(for: category)
        if wordCount > 0 || emojiCount > 0 {
            print("\(category): \(wordCount) words, \(emojiCount) emojis")
        }
    }
}
```

### Timing Distributions

Timing metrics use `SRKeyboardMetrics.ProbabilityMetric`, which contains a
distribution of sample values:

```swift
func analyzeTimings(_ metrics: SRKeyboardMetrics) {
    // Touch down to touch up duration for any key
    let touchDuration = metrics.touchDownUp
    let samples = touchDuration.distributionSampleValues  // [Measurement<UnitDuration>]

    if !samples.isEmpty {
        let avgMs = samples.map { $0.converted(to: .milliseconds).value }
            .reduce(0, +) / Double(samples.count)
        print("Average key press: \(avgMs)ms")
    }

    // QuickType (swipe) typing speed
    let pathSpeed = metrics.pathTypingSpeed  // Words per minute
    print("Swipe speed: \(pathSpeed) WPM")
}
```

## Device Usage Reports

`SRDeviceUsageReport` provides screen time, unlock, and per-app usage data:

```swift
func processDeviceUsage(_ result: SRFetchResult<AnyObject>) {
    guard let report = result.sample as? SRDeviceUsageReport else { return }

    // Summary metrics
    let reportDuration = report.duration
    let screenWakes = report.totalScreenWakes
    let unlocks = report.totalUnlocks
    let unlockDuration = report.totalUnlockDuration

    print("Wakes: \(screenWakes), Unlocks: \(unlocks), Duration: \(unlockDuration)s")

    // Per-category app usage
    for (category, apps) in report.applicationUsageByCategory {
        print("Category: \(category.rawValue)")
        for app in apps {
            let bundleID = app.bundleIdentifier ?? "unknown"
            let usageTime = app.usageTime
            print("  \(bundleID): \(usageTime)s")

            // Text input sessions within this app
            for session in app.textInputSessions {
                let inputDuration = session.duration
                let inputType = session.sessionType
                switch inputType {
                case .keyboard:
                    print("    Keyboard input: \(inputDuration)s")
                case .dictation:
                    print("    Dictation input: \(inputDuration)s")
                case .pencil:
                    print("    Pencil input: \(inputDuration)s")
                case .thirdPartyKeyboard:
                    print("    Third-party keyboard: \(inputDuration)s")
                @unknown default:
                    break
                }
            }
        }
    }

    // Notification interactions
    for (category, notifications) in report.notificationUsageByCategory {
        for notification in notifications {
            let event = notification.event
            switch event {
            case .received:
                print("Notification received: \(notification.bundleIdentifier ?? "unknown")")
            case .appLaunch:
                print("Notification opened app")
            case .clear, .hide, .silence:
                print("Notification dismissed")
            default:
                break
            }
        }
    }
}
```

## Phone and Messages Usage

### Phone Usage

```swift
func processPhoneUsage(_ result: SRFetchResult<AnyObject>) {
    guard let report = result.sample as? SRPhoneUsageReport else { return }

    let duration = report.duration
    let incoming = report.totalIncomingCalls
    let outgoing = report.totalOutgoingCalls
    let callDuration = report.totalPhoneCallDuration
    let contacts = report.totalUniqueContacts

    print("Calls: \(incoming) in / \(outgoing) out, Duration: \(callDuration)s")
    print("Unique contacts: \(contacts)")
}
```

### Messages Usage

```swift
func processMessagesUsage(_ result: SRFetchResult<AnyObject>) {
    guard let report = result.sample as? SRMessagesUsageReport else { return }

    let duration = report.duration
    let incoming = report.totalIncomingMessages
    let outgoing = report.totalOutgoingMessages
    let contacts = report.totalUniqueContacts

    print("Messages: \(incoming) in / \(outgoing) out over \(duration)s")
    print("Unique contacts: \(contacts)")
}
```

## Visit Tracking

`SRVisit` provides categorized location visit data with distance from home:

```swift
func processVisit(_ result: SRFetchResult<AnyObject>) {
    guard let visit = result.sample as? SRVisit else { return }

    let visitID = visit.identifier
    let arrival = visit.arrivalDateInterval
    let departure = visit.departureDateInterval
    let distance = visit.distanceFromHome  // CLLocationDistance in meters

    switch visit.locationCategory {
    case .home:
        print("At home")
    case .work:
        print("At work, \(distance)m from home")
    case .school:
        print("At school")
    case .gym:
        print("At gym")
    case .unknown:
        print("Unknown location, \(distance)m from home")
    @unknown default:
        break
    }

    print("Visit \(visitID): arrived \(arrival), departed \(departure)")
}
```

## Media Events

`SRMediaEvent` tracks interactions with images and videos in messaging apps:

```swift
func processMediaEvent(_ result: SRFetchResult<AnyObject>) {
    guard let event = result.sample as? SRMediaEvent else { return }

    let mediaID = event.mediaIdentifier

    switch event.eventType {
    case .onScreen:
        print("Media \(mediaID) appeared on screen")
    case .offScreen:
        print("Media \(mediaID) went off screen")
    @unknown default:
        break
    }
}
```

## Wrist Detection

`SRWristDetection` reports Apple Watch wrist state and configuration:

```swift
func processWristDetection(_ result: SRFetchResult<AnyObject>) {
    guard let wrist = result.sample as? SRWristDetection else { return }

    let isOnWrist = wrist.onWrist
    let onDate = wrist.onWristDate
    let offDate = wrist.offWristDate

    // Watch configuration
    switch wrist.wristLocation {
    case .left:
        print("Watch on left wrist")
    case .right:
        print("Watch on right wrist")
    @unknown default:
        break
    }

    switch wrist.crownOrientation {
    case .left:
        print("Crown on left")
    case .right:
        print("Crown on right")
    @unknown default:
        break
    }

    print("On wrist: \(isOnWrist)")
}
```
