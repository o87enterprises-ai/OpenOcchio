<p align="center">
  <img src="confidence_pro/assets/logo.png" width="600">
</p>

# OpenOcchio

**Developed by OpenEdin, a subsidiary of o87Dev Software Engineering.**

**OpenOcchio** is a comprehensive suite of AI Integrity tools designed to bring transparency and verification to AI-generated content. By calculating real-time confidence scores and detecting inconsistencies (like "growing noses" in responses), OpenOcchio empowers users to distinguish between factual outputs and hallucinations.

This repository provides two primary interfaces:
1.  **OpenOcchio Pro:** A cross-platform UI (Desktop Overlay & PWA) for real-time monitoring.
2.  **OpenOcchio Wrapper:** A lightweight Python CLI for developers and power users.

---

## 🚀 Quickstart: Core Requirements (All Platforms)

To use OpenOcchio locally, you must have an LLM runner installed. We recommend **Ollama**:
1.  **Download Ollama:** [ollama.com](https://ollama.com)
2.  **Pull a Model:**
    ```bash
    ollama pull qwen2.5:3b
    ```
    *OpenOcchio is optimized for `qwen2.5:3b`, but supports any model via configuration.*

---

## 💻 Desktop Installation (macOS, Windows, Linux)

The Desktop version provides a "System Overlay" — a floating, always-on-top gauge that monitors your clipboard.

### 1. Prerequisites
- **Python 3.10+**
- **Git**

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/o87enterprises-ai/OpenOcchio.git
cd OpenOcchio/confidence_pro

# Install dependencies
pip install -r requirements.txt
```

### 3. Launching the Overlay
```bash
python3 system_overlay.py
```
*   **macOS Note:** You may need to grant "Accessibility" or "Screen Recording" permissions depending on your security settings to allow the clipboard monitor to function seamlessly.
*   **Linux Note:** Ensure `xclip` or `wl-clipboard` is installed for clipboard support.

---

## 📱 Mobile & Web Installation (iOS, Android, Browser)

OpenOcchio Pro is built as a **Progressive Web App (PWA)**, allowing it to run as a standalone app on mobile devices without an App Store.

### 1. Hosting Locally
To run the PWA locally on your network:
```bash
cd confidence_pro
python3 -m http.server 8000
```

### 2. Android Installation
1.  Open Chrome on your Android device.
2.  Navigate to your machine's IP address (e.g., `http://192.168.1.5:8000`).
3.  Tap the **three dots (⋮)** and select **"Install app"** or **"Add to Home Screen"**.
4.  OpenOcchio will now appear in your app drawer.

### 3. iOS Installation (iPhone/iPad)
1.  Open **Safari** on your iOS device.
2.  Navigate to your machine's IP address (e.g., `http://192.168.1.5:8000`).
3.  Tap the **Share button** (square with up arrow).
4.  Scroll down and tap **"Add to Home Screen"**.
5.  Launch OpenOcchio from your home screen for a full-screen, app-like experience.

---

## 🛠 Developer CLI (OpenOcchio Wrapper)

For terminal-based interaction and automated testing.

### Setup & Usage
```bash
cd confidence_wrapper
# Optional: Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python3 chat.py
```

---

## 🛡 Security & Hardening

OpenOcchio is designed for **Privacy-First** operations:
-   **100% Local:** No data ever leaves your machine. Your prompts and AI responses stay between you and your local Ollama instance.
-   **Robust API Handling:** All internal calls are hardened with timeouts and error-handling to prevent system hangs.
-   **Zero Secrets:** The repository is sanitized and contains no API keys or sensitive credentials.

---

## 📊 Understanding the Scores

OpenOcchio uses a color-coded integrity scale:
-   **0.80 - 1.00:** 🟢 **Confident** (High consistency, reliable response)
-   **0.60 - 0.79:** 🟡 **Steady** (Minor variations, verify if critical)
-   **0.40 - 0.59:** 🟠 **Unsure** (Significant variance, likely a hallucination)
-   **0.20 - 0.39:** 🔴 **Insecure** (Low integrity, high risk of error)
-   **0.00 - 0.19:** 🚨 **Insecure** (Failure to provide a consistent answer)

---
© 2026 OpenEdin / o87Dev Software Engineering
