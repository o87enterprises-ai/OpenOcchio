# OpenOcchio: The AI Integrity Wrapper

A practical Python wrapper for any LLM running via Ollama to provide real-time confidence scores (0-1) and visual indicators. Like the legendary puppet who inspired its name, OpenOcchio watches for "growing noses" in AI responses.

## Features
- **Hybrid Confidence Metric:** Combines Count-based Cosine Similarity and Jaccard Unigram overlap to measure self-consistency across multiple samples.
- **Refusal Detection:** Automatically penalizes confidence when the AI admits inability to answer (ideal for subjective or nonsensical prompts).
- **Visual Indicator UI:** Color-coded ASCII progress bars and status labels (Confident, Unsure, Insecure).
- **Lightweight:** Optimized for local use on systems with limited RAM (e.g., 8GB).

---

## Quickstart Guide

### 1. Prerequisites
- **Ollama:** Install from [ollama.com](https://ollama.com).
- **Python 3.10+**
- **Model:** Pull a supported model (default is `qwen2.5:3b`, but `gemma3:1b` or `llama3.2:3b` also work).
  ```bash
  ollama pull qwen2.5:3b
  ```

### 2. Installation
Navigate to the project folder and activate the environment:
```bash
cd confidence_wrapper
source venv/bin/activate
# Install dependencies if not already present
pip install requests numpy scikit-learn
```

### 3. Usage

#### Interactive Chat
Run the visual chat interface to see real-time confidence bars:
```bash
python3 chat.py
```

#### Single Prompt
Run the wrapper directly for a quick score:
```bash
python3 wrapper.py "What is 2+2?"
```

---

## Confidence Levels
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
