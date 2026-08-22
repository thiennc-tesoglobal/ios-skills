---
name: ios-simulator
description: "Build, install, launch, inspect, and test iOS apps with Simulator and simctl. Use for simulator lifecycle, screenshots, logs, permissions, locations, push payloads, app containers, and repeatable local or CI verification."
---

# iOS Simulator

Use Simulator as a reproducible verification environment while keeping device selection and destructive operations explicit.

## Scope and Safety

This skill owns Simulator discovery, boot/shutdown, app install/launch, screenshots, logs, permissions, locations, push simulation, containers, and CI lifecycle. It does not replace real-device verification for hardware, performance, networking conditions, push delivery, camera, Bluetooth, NFC, or other device-only behavior.

Resolve an explicit simulator UDID before mutating state. Prefer an already booted suitable device. Do not erase or delete all simulators, broad CoreSimulator directories, or unrelated devices as a routine recovery step. If an erase/delete is genuinely needed, verify the exact target and preserve user data unless the task authorizes its removal.

Read [simctl Command Reference](references/simctl-commands.md) for command syntax and less common operations.

## Workflow

1. Inspect the Xcode project/workspace, scheme, supported platform, deployment target, installed runtimes, and available devices.
2. Select one destination by UDID and boot it if needed.
3. Build the intended scheme for that destination with a dedicated derived-data path when isolation helps.
4. Install and launch by bundle identifier; preserve the installed app container unless a clean-state test is required.
5. Capture logs, screenshots, and interaction evidence relevant to the request.
6. Clean up only devices, overrides, permissions, locations, or temporary artifacts created for the task.

## Core Commands

```bash
xcrun simctl list devices available
xcrun simctl bootstatus <UDID> -b
xcodebuild -project App.xcodeproj -scheme App \
  -destination 'platform=iOS Simulator,id=<UDID>' build
xcrun simctl install <UDID> /path/to/App.app
xcrun simctl launch <UDID> com.example.app
xcrun simctl io <UDID> screenshot /tmp/app.png
```

Use parsed command output or an explicit known UDID. Do not hardcode a device name when multiple runtimes can contain the same name.

## State and Diagnostics

- Reinstalling over an app normally preserves its data; uninstalling or erasing does not.
- Use `get_app_container` before inspecting sandboxed files.
- Prefer subsystem/category log predicates over unfiltered log streams.
- Clear status-bar, location, appearance, and permission overrides after tests that change them.
- Push simulation validates payload handling in Simulator, not production APNs delivery.
- Permission grants are useful in CI; permission behavior itself needs dedicated denied/limited/authorized tests.

## Recovery

When launch or boot fails, inspect device state and the exact error first. Try the narrowest recovery: terminate the app, relaunch, shut down the chosen simulator, or recreate only the disposable device created for the task. Treat erase/delete as destructive and target a validated UDID.

Do not present broad cache deletion or `erase all` as a default fix. Stop and report when recovery would remove user-owned simulator data outside the requested scope.

## Verification Matrix

Choose checks proportional to the change:

- build success and clean diagnostics
- cold/warm launch
- persistence across relaunch
- target appearance and Dynamic Type size
- required permission states
- screenshots of important states
- focused logs for crashes or runtime warnings
- real-device follow-up for unsupported hardware behavior

## Review Checklist

- [ ] Project, scheme, runtime, target, and bundle identifier are resolved
- [ ] Commands target an explicit UDID
- [ ] Existing app data is preserved unless clean state is required
- [ ] Screenshots and logs correspond to the tested build
- [ ] Overrides and task-created devices are cleaned up narrowly
- [ ] No broad erase/delete operation targets unrelated simulator data
- [ ] Simulator-only results are not claimed as real-device proof
- [ ] CI-created devices have deterministic teardown

## Reference

- [Complete simctl command reference](references/simctl-commands.md)
