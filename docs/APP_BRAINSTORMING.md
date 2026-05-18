# OpenOcchio App: Brainstorming & Architecture

To reach a truly consumer-grade "One-Click" experience for on-device AI confidence metering, we need to transition from a developer toolset to a unified application.

## 1. The Goal: "Truth-on-Tap"
A single downloadable application (`.app` for macOS, `.exe` for Windows) that requires **zero configuration**.

## 2. Technical Architecture Options

### A. The "Universal Interceptor" (Current path evolved)
- **Engine:** Python-based (packaged via PyInstaller or Nuitka).
- **Interception:** A background service that manages a local proxy automatically.
- **UI:** A system tray icon + the "Pinocchio's Nose" overlay.
- **Pros:** Already 80% implemented.
- **Cons:** Users still need to toggle browser proxy settings (unless we use `networksetup` on Mac to automate it).

### B. The "Secure Browser" / "OpenOcchio Browser"
- **Engine:** Electron or Tauri wrapper around a Chromium instance.
- **Interception:** Native to the browser wrapper; no external proxy needed.
- **UI:** Built-in gauge in the browser toolbar or as an overlay.
- **Pros:** Zero setup for the user.
- **Cons:** Users have to switch to a new browser.

### C. The "Accessibility Overlay" (Mobile & Desktop)
- **Engine:** Native (Swift for macOS/iOS, Kotlin for Android).
- **Interception:** Uses OS Accessibility APIs to "read" the screen of AI apps (ChatGPT, Claude apps).
- **UI:** Native OS overlays.
- **Pros:** Works with *native* AI apps, not just browsers.
- **Cons:** Very difficult to implement across different AI app versions; requires heavy system permissions.

## 3. Recommended Consumer Path: The "OpenOcchio System Tray"

1. **Unified Binary:** Bundle the Proxy and the Overlay into a single executable.
2. **Auto-Proxy Management:** The app should use `networksetup` (macOS) to automatically set the system proxy to `localhost:8082` when "Verification Mode" is ON, and revert it when OFF.
3. **CA Certificate Automation:** Automatically install the mitmproxy CA certificate into the system keychain so HTTPS interception works "out of the box."
4. **On-Device AI Integration:** Add support for detecting local inference (Ollama/LM Studio traffic) in the proxy script.

## 4. Next Implementation Steps
- [ ] Create a "Proxy Toggle" script that uses macOS `networksetup` to automate the configuration.
- [ ] Research `pystray` for adding a menu to the Pinocchio Nose overlay.
- [ ] Prototype a Tauri-based desktop app that embeds the Python logic.

---
*Brainstorming Session - May 18, 2026*
