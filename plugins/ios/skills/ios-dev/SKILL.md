---
name: ios-dev
description: MUST use this skill for any native iOS/Swift app work on a Mac with Xcode 27 or later - building, testing, debugging, simulator or device verification, TestFlight, and App Store release. Triggers on "iOS 앱", "Xcode", "시뮬레이터", "실기기", "TestFlight", "앱스토어 배포", "asc". Routes build/test/debug through the Xcode MCP bridge, verification through Device Hub (SimSlim) and iPhone Mirroring, and release through the asc CLI.
---

# iOS Development (Xcode 27)

One path: Xcode owns build, test, debug, and device sessions; the agent talks to it through the Xcode MCP bridge. Release goes to the App Store through `asc`.

## Priorities

1. **App Store** (TestFlight → review) via `asc` is the release path.
2. Sideloading (SideStore, AltStore) and cross-platform stacks (Expo, React Native, Flutter) are fallback candidates. Propose one only when the user asks or the App Store path is impossible, and say why.

Never open `Simulator.app`; Device Hub replaced it. Never `killall`; stop only processes you started.

## 0. Connect to Xcode (once per project)

Requirements: Xcode 27+, macOS 26.6+, Apple Silicon. In Xcode: Settings > Intelligence > Model Context Protocol > **Xcode Tools** on.

```bash
xcrun --find mcpbridge                                   # bridge exists
claude mcp add -s project xcode -- xcrun mcpbridge       # Claude Code: writes .mcp.json in the repo
codex mcp add xcode -- xcrun mcpbridge                   # Codex
xcrun mcp-server status                                  # headless server state
```

- Project scope on purpose: the bridge attaches to (or starts) Xcode, so registering it user-wide spawns Xcode in every unrelated session.
- Headless (no Xcode window): `sudo xcrun mcp-server enable` once, then `xcrun mcp-server open <workspace>`. The user runs the `sudo` step. Never pass `--unsafe-always-allow-all-agents`.
- Xcode shows a permission dialog per session unless the headless server has granted the agent. If the bridge is missing or denied, say so and stop; do not silently fall back to `xcodebuild`.
- Launch with Xcode's own configuration (Apple skills injected): `xcrun mcpbridge run-agent claude` / `... codex`.
- Apple's skills (`device-interaction`, `swiftui-specialist`, `modernize-tests`, ...): `xcrun agent skills export --output-dir <dir> --replace-existing`.

## 1. Build · test · debug — through Xcode

Use the Xcode MCP tools: build, run tests (XCTest and Swift Testing), read issues and diagnostics, control the debugger run state and read its console, list and switch schemes and destinations, inspect build settings, entitlements, and Info.plist keys. Render SwiftUI previews with the preview tools instead of launching the app for a layout check.

- Fix the compiler diagnostics the bridge returns; do not re-run a build to "see if it passes".
- Xcode's built-in agent (Coding Intelligence) is where the user runs test sweeps, bug hunts, and reads crash/hang/energy insights. When the user hands work to it, stop and do not duplicate the run.
- `xcodebuild` only when the user asks for a scripted or CI path, or the bridge is unavailable and you have said so.

## 2. Simulator verification — Device Hub + SimSlim

Device Hub (Xcode > Open Developer Tool > Device Hub) is the single window for simulators and physical devices.

```bash
simslim list                       # slim status per simulator
simslim on                         # after a runtime change or simulator reset
simslim verify                     # drift against the project's profile JSON
simslim measure                    # actual memory effect
```

- Keep a profile JSON in the project; `--except` keeps Push, StoreKit, and Universal Links alive when a test needs them.
- `simslim disk-clean` deletes permanently: never without the user's approval, and `simslim clone` important simulators first.
- Verify UI through the Xcode device tools: start a workspace session → install and run → synthesize events and capture screenshots and the UI hierarchy (tap `hitPoint` coordinates) → end the session. Keep one session per task; open sessions are expensive.
- After a UI-affecting change, verify on the simulator before reporting done. Report overlapping, cropped, or unreadable UI as a bug even when the user did not ask.

## 3. Physical device — only with the user's approval

Ask before installing or running anything on a device. State the device, the build configuration, and what you will check.

- Pairing: Device Hub sidebar `+` → "Pair Nearby Device…" (iOS 27+, same Wi-Fi) or by cable. Developer Mode must be on.
- The user keeps **iPhone Mirroring** (macOS app, separate from Device Hub) open to watch the device. The agent reads: the Xcode debugger console through the bridge, or `xcrun devicectl device process launch --console --device <udid> <bundle-id>` for stdout without the debugger. Screenshots and the UI hierarchy come from the Xcode device tools with the session bound to the device id.
- Device-only features (Push, camera, background, StoreKit sandbox) are the reason to be on a device; everything else stays on the simulator.

## 4. App Store release — asc

```bash
brew install asc                   # rorkai/App-Store-Connect-CLI, MIT
asc auth status                    # the user runs `asc auth login --name ... --key-id ... --issuer-id ... --private-key <AuthKey.p8>` once
asc doctor
asc status --app <APP_ID>
asc xcode archive --workspace <App>.xcworkspace --scheme <App> --archive-path .asc/artifacts/<App>.xcarchive --output json
asc xcode export  --archive-path .asc/artifacts/<App>.xcarchive --ipa-path .asc/artifacts/<App>.ipa --output json
asc publish testflight --app <APP_ID> --ipa .asc/artifacts/<App>.ipa --group <GROUP_ID>
asc publish appstore   --app <APP_ID> --ipa .asc/artifacts/<App>.ipa --version <X.Y.Z> --submit --confirm
asc search "<what you want to do>" --output json      # find the exact command
```

- API keys live in the keychain via `asc auth login`. Never print, log, or commit a key, key id, or issuer id; never type them yourself - the user runs the login.
- `--submit --confirm` is irreversible: state app, version, build, and release notes, then wait for the user's yes.
- Definitive API errors (409, 422) fail the step as-is. No retries that hide them.
- Every published build gets a git tag and a user-facing changelog.

## Checklist

Xcode MCP bridge connected in project scope · build and tests through the bridge · Device Hub only, `simslim verify` clean · device run approved by the user, iPhone Mirroring open, console read · `asc auth status` valid without exposing keys · submit confirmed by the user · tag and changelog done.
