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

def calculate_confidence(text: str) -> float:
    text_lower = text.lower()
    words = text_lower.split()

    # Length bonus for very short factual answers
    if len(words) <= 10 and any(word in text_lower for word in ["yes","no","is","are","equals","="]):
        length_bonus = 0.3
    else:
        length_bonus = 0.0

    low_weight = {
        "i'm not sure":0.8, "i don't know":0.9, "it depends":0.6, "maybe":0.5,
        "might be":0.5, "possibly":0.4, "i think":0.3, "in my opinion":0.4,
        "not certain":0.7, "hard to say":0.8, "unknown":0.9,
        "not exactly":0.5, "sort of":0.4, "kind of":0.4, "somewhat":0.3, "it's possible":0.4
    }
    high_weight = {
        "certainly":0.9, "absolutely":1.0, "without a doubt":1.0, "definitely":0.9,
        "it is clear":0.8, "always":0.7, "never":0.7, "undoubtedly":1.0,
        "yes, it is":0.9, "that is correct":0.9, "the fact is":0.8,
        "yes,":0.8, "indeed":0.8, "of course":0.9, "it is ":0.5, "that's correct":0.9,
        "without question":1.0, "no question":0.9, "by definition":0.9, "is the":0.4
    }

    low_score = sum(w for phrase,w in low_weight.items() if phrase in text_lower)
    high_score = sum(w for phrase,w in high_weight.items() if phrase in text_lower)

    total = low_score + high_score + 0.001
    raw_conf = high_score / total
    conf = min(0.95, raw_conf + length_bonus)
    return max(0.05, conf)

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

    # 1. Try direct token logprobs (OpenAI style)
    try:
        content = resp_data["choices"][0].get("logprobs", {}).get("content", [])
        if content:
            probs = [math.exp(t.get("logprob", -100)) for t in content if t.get("logprob") is not None]
            if probs:
                conf = sum(probs) / len(probs)
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
            conf = calculate_confidence(ai_text)
            log(f"Heuristic score: confidence={conf}")

    if conf is not None:
        try:
            requests.post(OVERLAY_URL, json={"confidence": conf}, timeout=1, proxies={"http": None, "https": None})
            log(f"Sent confidence {conf} to overlay")
        except Exception as e:
            log(f"Failed to update overlay: {e}")