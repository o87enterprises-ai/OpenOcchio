<p align="center">
  <img src="confidence_pro/assets/logo.png" width="600">
</p>

# OpenOcchio

**Developed by OpenEdin, a subsidiary of o87Dev Software Engineering.**

**OpenOcchio** is a real-time AI Integrity tool that acts as a "truth-meter" for LLM responses. By intercepting traffic from major AI providers (Claude, ChatGPT, DeepSeek), it calculates a confidence score and visualizes it through a dynamic **Pinocchio's Nose** interface.

---

## ✨ Key Features
- **Pinocchio's Nose UI:** A playful, intuitive gauge where "lies" (low confidence) make the nose grow longer and turn red.
- **Real-time Interception:** Monitors traffic from `claude.ai`, `chat.deepseek.com`, and more using a transparent proxy.
- **Enhanced Heuristics:** Weighted keyword analysis combined with factual-answer bonuses to detect hallucinations.
- **Multi-Platform:** Desktop overlay for macOS/Linux and a Mobile-ready PWA for iOS/Android.

---

## 💻 Desktop Installation & Usage (Recommended)

The desktop version provides the full experience: real-time traffic interception and the floating Pinocchio gauge.

### 1. Prerequisites
- **Python 3.10+**
- **mitmproxy** (`pip install mitmproxy`)
- **PySide6** (`pip install PySide6`)

### 2. Launch Sequence
OpenOcchio requires two components running in parallel:

**Step A: Start the Pinocchio Overlay**
```bash
python3 confidence_pro/system_overlay.py
```

**Step B: Start the Traffic Interceptor**
```bash
mitmweb --listen-port 8082 -s openocchio_proxy.py
```

**Step C: Configure Browser**
Set your browser (Firefox is easiest) to use a **Manual Proxy Configuration**:
- **HTTP/HTTPS Proxy:** `localhost`
- **Port:** `8082`

Now, whenever you chat with Claude or DeepSeek, the Pinocchio gauge will react instantly to the AI's responses!

---

## 📱 Mobile & Web (PWA)

OpenOcchio can also be deployed as a standalone mobile app using Hugging Face Spaces and GitHub Pages.

### 1. Backend Setup
Deploy the `openocchio-backend/` directory as a **Docker Space** on Hugging Face. Add your `GROQ_API_KEY` to the Space secrets.

### 2. Frontend Setup
1. Update `confidence_pro/script.js` with your Hugging Face Space URL.
2. Host the `confidence_pro/` folder on GitHub Pages.
3. On your phone, "Add to Home Screen" to install the PWA.

---

## 📊 Understanding Pinocchio's Nose

The gauge directly visualizes the AI's certainty:
- **Short & Green (0.8 - 1.0):** **Confident.** The AI is assertive and uses certain language.
- **Medium & Yellow (0.6 - 0.79):** **Steady.** Factual but perhaps slightly hedged.
- **Long & Orange (0.4 - 0.59):** **Unsure.** Pinocchio's nose is growing! The AI is using uncertain phrases.
- **Very Long & Red (0.0 - 0.39):** **Insecure.** High risk of hallucination or refusal.

---
© 2026 OpenEdin / o87Dev Software Engineering
