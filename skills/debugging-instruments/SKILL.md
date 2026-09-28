---
name: debugging-instruments
description: "Debug iOS apps and profile performance using LLDB, the interactive Memory Graph Debugger, and Instruments. Use for crashes, retain-cycle inspection, hangs, build failures, and generic CPU, memory, energy, or network profiling. Use ios-memgraph-analysis for .memgraph capture, leaks CLI ownership paths, or persistent heap growth; use ios-ettrace-performance for ETTrace capture and JSON."
---

# Debugging and Instruments

Diagnose crashes, memory leaks, hangs, and performance bottlenecks using LLDB, Xcode Memory Graph Debugger, unified logging/signposts, and Instruments.

> **Scope Boundary:** Route command-line `.memgraph` analysis to `ios-memgraph-analysis` and ETTrace tracing to `ios-ettrace-performance`.

## Contents

- [LLDB Debugging Workflow](#lldb-debugging-workflow)
- [Memory Graph & Retain Cycles](#memory-graph--retain-cycles)
- [Hangs & Signpost Diagnostics](#hangs--signpost-diagnostics)
- [Instruments Profiling](#instruments-profiling)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## LLDB Debugging Workflow

Follow a structured, non-invasive triage loop:

1. Reproduce in Debug configuration; pause at the narrowest relevant line.
2. Inspect values without executing code using `v`, falling back to `po` only for formatted descriptions.
3. Traverse frames and threads to isolate invalid states.
4. Set conditional breakpoints or watchpoints to catch unintended state transitions.

```text
(lldb) br set -f OrderViewModel.swift -l 42   # Break at file and line
(lldb) v orderState                           # Inspect variable without code execution
(lldb) po orderState                          # Print debug description
(lldb) bt all                                 # Print backtrace for all threads
(lldb) frame select 2                         # Switch execution frame
(lldb) br modify 1 -c "orderId == 404"        # Set condition on breakpoint
(lldb) w set v self.totalAmount               # Watchpoint on memory mutation
```

## Memory Graph & Retain Cycles

Enable **Malloc Stack Logging** (Edit Scheme > Run > Diagnostics) to record allocation backtraces.

1. Navigate to the suspect view, perform user actions, and pop/dismiss the view.
2. Click **Debug Memory Graph** in the Xcode debug bar.
3. Look for purple exclamation mark warnings indicating leaked memory or retain cycles.
4. Select the instance node to inspect the strong reference graph.

Common fix: break closure cycles using `[weak self]` or assign delegates weakly (`weak var delegate: SomeDelegate?`).

## Hangs & Signpost Diagnostics

Diagnose main thread stalls and measure execution intervals using unified logging and `OSSignposter`:

```swift
import os

let logger = Logger(subsystem: "com.example.app", category: "DataSync")
let signposter = OSSignposter(logger: logger)

func loadRecords() async throws {
    let signpostID = signposter.makeSignpostID()
    let state = signposter.beginInterval("LoadRecords", id: signpostID)
    defer { signposter.endInterval("LoadRecords", state) }

    // Intensive operation
}
```

View intervals and subsystem events in Instruments under the **os_signpost** instrument.

## Instruments Profiling

Always profile in **Release configuration** outside the debugger (Product > Profile):

- **Time Profiler**: Identifies hot execution paths and CPU usage. Expand invert-call-tree and hide-system-libraries to focus on app code.
- **Allocations & Leaks**: Tracks heap growth, memory allocations, and leaked memory over time.
- **Core ML**: Measures model execution latency, neural engine offload, and memory consumption.
- **Energy Log / Network**: Audits battery impact and network transfer efficiency.

## Common Mistakes

- **Using `po` for simple inspection**: `po` evaluates expressions via the Swift runtime and can cause unexpected side effects or deadlocks. Use `v` to read values safely.
- **Profiling in Debug configuration**: Debug builds disable compiler optimizations and produce distorted performance timings.
- **Profiling with debugger attached**: LLDB hooks introduce significant execution overhead. Use Instruments standalone.
- **Ignoring purple warnings in Memory Graph**: Purple warnings flag definite object leaks; resolve them before optimizing memory elsewhere.
- **Blocking the main thread with synchronous work**: Synchronous file I/O or network calls on `@MainActor` trigger main-thread hangs.

## Review Checklist

- [ ] LLDB inspection favors `v` over `po` to avoid side effects
- [ ] Malloc Stack Logging enabled when capturing memory graphs
- [ ] Strong reference cycles broken with `[weak self]` or `weak` delegates
- [ ] Profiling performed in Release build without debugger attachment
- [ ] Signposts implemented around performance-critical workflows
- [ ] Time Profiler call trees inspected with system libraries hidden

## References

- LLDB command reference: [references/lldb-patterns.md](references/lldb-patterns.md)
- Instruments template guide: [references/instruments-guide.md](references/instruments-guide.md)
- [Logging (unified logging system)](https://sosumi.ai/documentation/os/logging)
- [Logger](https://sosumi.ai/documentation/os/logger)
- [OSSignposter](https://sosumi.ai/documentation/os/ossignposter)
- [Generating log messages from your code](https://sosumi.ai/documentation/os/generating-log-messages-from-your-code)
- [Recording performance data (signposts)](https://sosumi.ai/documentation/os/recording-performance-data)
- [Diagnosing memory, thread, and crash issues early](https://sosumi.ai/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)
- [Data races](https://sosumi.ai/documentation/xcode/data-races)
- [Reducing your app's memory use](https://sosumi.ai/documentation/xcode/reducing-your-app-s-memory-use)
- [Improving your app's performance](https://sosumi.ai/documentation/xcode/improving-your-app-s-performance)
- [Improving app responsiveness](https://sosumi.ai/documentation/xcode/improving-app-responsiveness)
- [Analyzing your app's battery use](https://sosumi.ai/documentation/xcode/analyzing-your-app-s-battery-use)
- [Analyzing the performance of your shipping app](https://sosumi.ai/documentation/xcode/analyzing-the-performance-of-your-shipping-app)
