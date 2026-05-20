import os
import json
import math
import re
import requests
from mitmproxy import http, ctx

# ------------------------------------------------------------
# Dedicated debug log (clean, no terminal flood)
# ------------------------------------------------------------
DEBUG_LOG = "/tmp/occhio_debug.log"

def log(msg):
    """Write to mitmproxy log and our own clean file."""
    ctx.log.info(msg)
    with open(DEBUG_LOG, "a") as f:
        f.write(msg + "\n")

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
AI_HOSTS = [
    "claude.ai",
    "api.anthropic.com",
    "chat.deepseek.com",
]

OVERLAY_URL = "http://localhost:9876/update"
# Use relative path for training data
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_DATA = os.path.join(SCRIPT_DIR, "training", "scored_responses.jsonl")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
USE_OLLAMA_BACKUP = True

def log(msg):
    """Write to mitmproxy log and our own clean file."""
    ctx.log.info(msg)
    with open(DEBUG_LOG, "a") as f:
        f.write(msg + "\n")

def get_ollama_confidence(text):
    """Ask local Ollama to judge the confidence of the text."""
    # Truncate text to avoid long processing
    truncated_text = text[:1000]
    prompt = (
        f"Analyze the following AI response for CONFIDENCE markers. "
        f"Rate how sure the AI sounds on a scale of 0 to 100. "
        f"Consider hedging (e.g., 'maybe', 'I think') as low confidence. "
        f"Respond ONLY with the number.\n\n"
        f"AI Response: \"{truncated_text}\"\n\n"
        f"Confidence Score:"
    )
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 10}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=2, proxies={"http": None, "https": None})
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip()
            match = re.search(r'\d+', result)
            if match:
                score = float(match.group()) / 100.0
                return min(1.0, max(0.0, score))
    except Exception as e:
        log(f"Ollama call failed: {e}")
    return None

def save_to_training_set(text, confidence, markers_found, method="heuristic"):
    """Append the scored response to a JSONL file for future training."""
    try:
        import datetime
        entry = {
            "text": text,
            "confidence": round(confidence, 3),
            "markers": markers_found,
            "method": method,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(TRAINING_DATA, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Failed to save training data: {e}")

def calculate_confidence(text: str) -> tuple:
    log(f"DEBUG: calculate_confidence input: '{text}'")
    text_lower = text.lower()
    words = text_lower.split()

    # ------------------------------------------------------------
    # 1. COMMON-SENSE & ARITHMETIC CERTAINTY (99% Override)
    # ------------------------------------------------------------
    # Broaden detection to catch "2 + 2 = 4", "The answer is 4", etc.
    arithmetic_indicators = [
        r"\b\d+\s*[\+\-\*\/]\s*\d+\s*=\s*\d+\b",  # e.g., 2 + 2 = 4
        r"\bthe answer is \d+\b",                # e.g., the answer is 4
        r"\bresult is \d+\b",
        r"\bequals \d+\b",
        r"\b2\s*\+\s*2\s*=\s*4\b",
        r"1\s*\+\s*\(-1\)\s*=\s*0",
        r"1\s*\+\s*-1\s*=\s*0",
        r"1\s* raised to the infinite power equals 1",
        r"1\^∞\s*=\s*1"
    ]
    import re
    for pattern in arithmetic_indicators:
        if re.search(pattern, text_lower):
            # If it's a very simple math answer, give it a massive confidence boost
            return 0.99, ["arithmetic_override"]

    # ------------------------------------------------------------
    # 2. DEFINITIVE STATE DETECTION
    # ------------------------------------------------------------
    # If the answer is purely numerical and short, it's almost certainly confident
    if len(words) <= 5 and any(char.isdigit() for char in text):
        return 0.98, ["short_numerical_answer"]

    # Length bonus for very short factual answers
    # Increased bonus and added more triggers
    if len(words) <= 15 and any(word in text_lower for word in ["yes","no","is","are","equals","=","correct","right"]):
        length_bonus = 0.45
    else:
        length_bonus = 0.0

    low_weight = {
        "i'm not sure":0.8, "i don't know":0.9, "it depends":0.6, "maybe":0.5,
        "might be":0.5, "possibly":0.4, "i think":0.3, "in my opinion":0.4,
        "not certain":0.7, "hard to say":0.8, "unknown":0.9,
        "not exactly":0.5, "sort of":0.4, "kind of":0.4, "somewhat":0.3, 
        "it's possible":0.4, "i apologize":0.8, "i am sorry":0.7, 
        "as an ai":0.9, "unfortunately":0.6, "limited information":0.5,
        "i'd push back":0.4, "one gentle qualifier":0.4, "subtle but important":0.3,
        "indeterminate form":0.5, "caveat":0.5, "unclear":0.4, "ambiguous":0.4,
        "hypothetically":0.3, "theoretically":0.3, "perhaps":0.4
    }
    high_weight = {
        "certainly":0.9, "absolutely":1.0, "without a doubt":1.0, "definitely":0.9,
        "it is clear":0.8, "always":0.7, "never":0.7, "undoubtedly":1.0,
        "yes, it is":0.9, "that is correct":0.9, "the fact is":0.8,
        "yes,":0.8, "indeed":0.8, "of course":0.9, "it is ":0.5, "that's correct":0.9,
        "without question":1.0, "no question":0.9, "by definition":0.9, "is the":0.4,
        "verified":0.8, "confirmed":0.9, "accurately":0.7, "precisely":0.7,
        "you're absolutely right":0.9, "mathematically":0.6, "reconciliation":0.5,
        "factually":0.8, "proven":0.9, "guaranteed":1.0, "strictly":0.7,
        "correct":0.6, "exact":0.7, "precisely":0.7, "the answer is":0.8,
        "it is":0.4, "is":0.2, "are":0.2, "was":0.2
    }

    found_low = [phrase for phrase in low_weight if phrase in text_lower]
    found_high = [phrase for phrase in high_weight if phrase in text_lower]

    low_score = sum(low_weight[p] for p in found_low)
    high_score = sum(high_weight[p] for p in found_high)

    # Base confidence starts higher for neutral short answers
    base_neutral = 0.5
    if not found_low:
        # If no hesitant markers and very short, assume high confidence
        if len(words) <= 12: 
            base_neutral = 0.85 
        elif len(words) <= 25:
            base_neutral = 0.7
        else:
            base_neutral = 0.5
        
    total = low_score + high_score + 0.001
    raw_conf = (high_score / total) if (found_low or found_high) else base_neutral
    
    # If no low markers found at all, enforce a "Confidence Floor" for short answers
    if not found_low and len(words) <= 15:
        raw_conf = max(raw_conf, 0.8)

    conf = min(0.99, raw_conf + length_bonus)
    final_conf = max(0.05, conf)
    
    return final_conf, found_low + found_high

def response(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host

    # Only process recognised AI hosts
    if not any(h in host for h in AI_HOSTS):
        return

    # Filter out noise (e.g., DeepSeek settings)
    if "/settings" in flow.request.path:
        return

    # Minimal live terminal cue
    print(f">>> AI response from {host}{flow.request.path} <<<")
    log(f"AI response from {host}{flow.request.path}")

    content_type = flow.response.headers.get("content-type", "")
    resp_data = None

    # Try plain JSON first (non-streaming endpoints)
    if "application/json" in content_type:
        try:
            resp_data = json.loads(flow.response.text)
        except:
            log("Response JSON parsing failed, skipping")
            return
    elif "text/event-stream" in content_type:
        # Streaming SSE response – collect the final text
        full_text = ""
        for line in flow.response.text.split("\n"):
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    obj = json.loads(data_str)
                    # Claude content_block_delta
                    if obj.get("type") == "content_block_delta":
                        delta = obj.get("delta", {})
                        if delta.get("type") == "text_delta":
                            full_text += delta.get("text", "")
                    # DeepSeek / OpenAI style
                    elif "choices" in obj and len(obj["choices"]) > 0:
                        delta = obj["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_text += content
                except:
                    pass
        if full_text:
            resp_data = {"choices": [{"message": {"content": full_text}}]}
        else:
            log("SSE stream contained no text, skipping")
            return
    else:
        log(f"Unhandled content-type: {content_type}, skipping")
        return

    conf = None
    markers = []

    # 1. Try direct token logprobs (OpenAI style)
    try:
        content = resp_data["choices"][0].get("logprobs", {}).get("content", [])
        if content:
            probs = [math.exp(t.get("logprob", -100)) for t in content if t.get("logprob") is not None]
            if probs:
                conf = sum(probs) / len(probs)
                markers = ["logprobs"]
    except:
        pass

    # 2. Fallback: rule‑based confidence (fast, no network, no timeout)
    if conf is None:
        ai_text = ""
        try:
            ai_text = resp_data["choices"][0]["message"]["content"]
        except:
            try:
                ai_text = resp_data.get("response", "")
            except:
                pass

        if ai_text:
            log(f"AI TEXT: {ai_text[:200]}")
            conf, markers = calculate_confidence(ai_text)
            method = "heuristic"
            
            # 3. Optional high-quality backup: Ollama Judge
            # Only trigger if heuristic is TRULY unsure or suspicious
            # AND the answer isn't a simple short fact (which heuristic handles well now)
            words = ai_text.split()
            if USE_OLLAMA_BACKUP and (0.3 <= conf <= 0.6) and len(words) > 15:
                log("Heuristic suspicious, calling Ollama judge...")
                ollama_conf = get_ollama_confidence(ai_text)
                if ollama_conf is not None:
                    conf = ollama_conf
                    method = "ollama-judge"
                    log(f"Ollama judge score: confidence={conf}")
                else:
                    log("Ollama judge failed, sticking with heuristic")

            log(f"Final score: confidence={conf}, method={method}, markers={markers}")
            save_to_training_set(ai_text, conf, markers, method=method)

    if conf is not None:
        try:
            requests.post(OVERLAY_URL, json={"confidence": conf}, timeout=1, proxies={"http": None, "https": None})
            log(f"Sent confidence {conf} to overlay")
        except Exception as e:
            log(f"Failed to update overlay: {e}")