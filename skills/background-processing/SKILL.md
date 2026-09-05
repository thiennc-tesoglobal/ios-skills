---
name: background-processing
description: "Schedules and executes iOS background work with BGTaskScheduler and background URLSession. Use for app refresh, processing, continued-processing tasks, expiration and completion handling, background downloads, background pushes, registration, Info.plist configuration, or launch simulation."
---

# Background Processing

Register, schedule, and execute background tasks on iOS using BackgroundTasks (`BGTaskScheduler`), background `URLSession`, and background push notifications. Targets Swift 6.3 / iOS 26+.

## Contents

- [Capabilities and Configuration](#capabilities-and-configuration)
- [Task Selection Matrix](#task-selection-matrix)
- [Core Lifecycle Rules](#core-lifecycle-rules)
- [Route by Task](#route-by-task)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Capabilities and Configuration

Every task identifier must be declared in `Info.plist` under `BGTaskSchedulerPermittedIdentifiers`, or `submit(_:)` throws `BGTaskScheduler.Error.Code.notPermitted`.

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.example.app.refresh</string>
    <string>com.example.app.db-cleanup</string>
    <string>com.example.app.export.*</string>
</array>
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>       <!-- Required for BGAppRefreshTask -->
    <string>processing</string>  <!-- Required for BGProcessingTask -->
    <string>remote-notification</string> <!-- Required for silent push -->
</array>
```

In Xcode: Target > Signing & Capabilities > Background Modes > enable **Background fetch**, **Background processing**, or **Remote notifications**.

## Task Selection Matrix

| Task Type | Max Duration | Trigger | Requires Power/Network | Use Case |
|---|---|---|---|---|
| `BGAppRefreshTask` | ~30 seconds | System opportunistic | Configurable hint | Light feed/state updates |
| `BGProcessingTask` | Several minutes | Device idle | External power / network optional | Database cleanup, maintenance, ML indexing |
| `BGContinuedProcessingTask` | User bounded | Foreground user action | Live Activity progress | Exporting large media, offline bundle generation |
| `URLSession.background` | Managed out-of-process | Network completion | Cellular/WiFi policy | Large file downloads and uploads |
| Silent Remote Push | ~30 seconds | APNs trigger (`content-available: 1`) | Network required | Server-driven data invalidation hint |

## Core Lifecycle Rules

1. **Register before launch finishes**: Register all handlers in `application(_:didFinishLaunchingWithOptions:)` (UIKit) or `App.init()` (SwiftUI). Submitting an unregistered identifier throws runtime exceptions.
2. **Re-schedule inside handler**: Immediately schedule the next iteration at the beginning of the execution handler so scheduling survives app crashes or task timeouts.
3. **Always set `expirationHandler`**: The system can revoke background execution time at any moment. The expiration handler must cancel active tasks and call `setTaskCompleted(success: false)`.
4. **Call `setTaskCompleted(success:)` exactly once**: Failing to call completion causes the system to penalize future execution allocations.
5. **Treat `earliestBeginDate` as a lower bound**: iOS determines actual launch time based on battery status, power state, and user interaction patterns.

## Route by Task

- For full registration code, canonical handlers, and checkpointing, read [Canonical Registration and Handlers](references/background-task-patterns.md#canonical-bgtaskscheduler-registration).
- For simulating task launches with LLDB (`_simulateLaunchForTaskWithIdentifier:`), read [Debugging Background Tasks](references/background-task-patterns.md#debugging-background-tasks).
- For background downloads, uploads, and handling app relaunch in `handleEventsForBackgroundURLSession`, read [Background URLSession Extended Patterns](references/background-task-patterns.md#background-urlsession--extended-patterns).
- For background push throttling and payload constraints, read [Background Push Extended Patterns](references/background-task-patterns.md#background-push--extended-patterns).
- For continued processing tasks conforming to `ProgressReporting`, read [BGContinuedProcessingTask Patterns](references/background-task-patterns.md#bgcontinuedprocessingtask--extended-patterns).

## Common Mistakes

- Submitting a task identifier that is not declared in `BGTaskSchedulerPermittedIdentifiers` (throws `.notPermitted`).
- Forgetting to call `task.setTaskCompleted(success:)` on all execution and failure paths.
- Omitting `task.expirationHandler`, leading to watchdog termination when background time expires.
- Scheduling app refresh at aggressive minute-scale intervals instead of respecting system heuristics.
- Using async/await convenience APIs or completion closures on background `URLSession` (requires delegate).

## Review Checklist

- [ ] Task identifiers declared in `BGTaskSchedulerPermittedIdentifiers`
- [ ] Required `UIBackgroundModes` enabled (`fetch`, `processing`, `remote-notification`)
- [ ] Handlers registered during app launch before launch completes
- [ ] `expirationHandler` cancels active tasks and reports failure
- [ ] `setTaskCompleted(success:)` called exactly once on all code paths
- [ ] Subsequent tasks re-scheduled within the handler
- [ ] Background `URLSession` uses delegate and preserves background completion handler
- [ ] Downloaded files moved in `urlSession(_:downloadTask:didFinishDownloadingTo:)` before return
- [ ] Silent pushes include `content-available: 1`, `apns-push-type: background`, and priority 5

## References

- [Background task patterns and debugging recipes](references/background-task-patterns.md)
- [BGTaskScheduler](https://sosumi.ai/documentation/backgroundtasks/bgtaskscheduler)
- [BGAppRefreshTask](https://sosumi.ai/documentation/backgroundtasks/bgapprefreshtask)
- [BGProcessingTask](https://sosumi.ai/documentation/backgroundtasks/bgprocessingtask)
- [BGContinuedProcessingTask](https://sosumi.ai/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [Performing long-running tasks on iOS and iPadOS](https://sosumi.ai/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
