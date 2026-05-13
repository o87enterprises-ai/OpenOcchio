# <img src="assets/logo.png" width="40" vertical-align="middle"> OpenOcchio

**The AI Integrity Gauge — Bringing Transparency to Every Response.**

OpenOcchio (the "Open Eye") is a consumer-grade AI Confidence Indicator designed for browsers, desktop apps, and mobile devices. Like the legendary puppet who inspired its name, OpenOcchio watches for "growing noses" in AI responses by calculating real-time confidence scores.

## Features
- **Browser-in-Browser:** Run any AI chat inside the OpenOcchio PWA wrapper.
- **Global Desktop Overlay:** A floating, always-on-top gauge that monitors your clipboard for native macOS/Windows/Linux apps.
- **Mobile PWA:** Install on iOS/Android as a standalone app to bypass App Store restrictions.
- **Zero-Config Verification:** Simply "Copy" text to see its confidence score instantly.

---

## Installation & Setup

### Desktop (macOS, Windows, Linux)
1. **Requirements:** Python 3.10+ and [Ollama](https://ollama.com).
2. **Install Dependencies:**
   ```bash
   pip install PySide6 pyperclip requests numpy scikit-learn
   ```
3. **Run the Overlay:**
   ```bash
   python3 system_overlay.py
   ```

### Web & Mobile (iOS, Android)
1. **GitHub Pages Deployment:**
   - Push the `confidence_pro/` folder to a GitHub repository.
   - Go to **Settings > Pages** and enable deployment from the `main` branch.
2. **Install as App:**
   - Open your GitHub Pages URL in Safari (iOS) or Chrome (Android).
   - Tap "Add to Home Screen" to install the PWA.

---

## Security & Privacy
- **Local First:** All confidence calculations for local models (Ollama) stay on your machine.
- **Repo Sanitation:** Ensure you do not commit `.env` files or API keys. The provided `.gitignore` handles standard exclusions.
- **Open Source:** This project is designed for distribution via open-source marketplaces like GitHub, F-Droid, or AltStore.

---

## Multi-Platform Support
| Platform | Implementation | Recommendation |
| :--- | :--- | :--- |
| **macOS/Win/Linux** | `system_overlay.py` | Use for native App Store apps. |
| **iOS/Android** | PWA (index.html) | Add to Home Screen for app-like use. |
| **Web Browser** | PWA (index.html) | Best for laptop/desktop browsing. |
The indicator uses a green-to-red gradient with the following scores:
- **0.80 - 1.00:** 🟢 **Confident**
- **0.60 - 0.79:** 🟡 **Not so confident**
- **0.40 - 0.59:** 🟠 **Unsure**
- **0.20 - 0.39:** 🔴 **Kind of insecure**
- **0.00 - 0.19:** 🚨 **Insecure**

## Project Structure
- `wrapper.py`: Core logic for confidence computation and UI labels.
- `chat.py`: Interactive terminal chat application.
- `verify_strict.py`: Automated testing suite for accuracy validation.
- `test_harness.py`: Basic benchmark script.
