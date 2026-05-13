# <img src="confidence_pro/assets/logo.png" width="40" vertical-align="middle"> OpenOcchio

**Developed by OpenEdin, a subsidiary of o87Dev Software Engineering.**

**OpenOcchio** (the "Open Eye") is a suite of AI Integrity tools designed to bring transparency to AI responses. By calculating real-time confidence scores and detecting "growing noses" (refusals or inconsistencies), OpenOcchio helps users distinguish between factual AI outputs and hallucinations.

## Project Structure

- **[OpenOcchio Pro (Desktop/Web/Mobile)](./confidence_pro/README.md):** A PWA and Python overlay for consumer-grade confidence monitoring.
- **[OpenOcchio Wrapper (Python CLI)](./confidence_wrapper/README.md):** A practical Python wrapper for LLMs running via Ollama.

## Quickstart

### Desktop Overlay
```bash
cd confidence_pro
pip install -r requirements.txt
python3 system_overlay.py
```

### CLI Chat
```bash
cd confidence_wrapper
python3 chat.py
```

## Security & Integrity
- **Local First:** All calculations stay on your machine.
- **Hardened:** API calls include timeouts and robust error handling.
- **Sanitized:** No sensitive credentials or secrets are stored in this repository.

---
© 2026 OpenEdin / o87Dev Software Engineering
