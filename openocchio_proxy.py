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


def response(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host

    # Only process recognised AI hosts
    if not any(h in host for h in AI_HOSTS):
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
            # Simple keyword / phrase confidence heuristic
            low_confidence_markers = [
                "i'm not sure", "i don't know", "it depends", "could be", "might be",
                "possibly", "maybe", "i think", "i believe", "in my opinion",
                "not certain", "hard to say", "unknown", "speculative",
                "not exactly", "sort of", "kind of", "somewhat", "it's possible"
            ]
            high_confidence_markers = [
                "certainly", "absolutely", "without a doubt", "definitely",
                "it is clear that", "it is well established", "always",
                "never", "undoubtedly", "indisputably",
                "yes,", "indeed", "of course", "it is ", "that is correct", "that's correct",
                "without question", "no question", "by definition", "the fact is",
                "is the", "definitely", "certainly", "absolutely"
            ]

            text_lower = ai_text.lower()
            low_count = sum(1 for phrase in low_confidence_markers if phrase in text_lower)
            high_count = sum(1 for phrase in high_confidence_markers if phrase in text_lower)

            if low_count + high_count == 0:
                conf = 0.5  # neutral
            else:
                # Map the balance to a 0–1 scale
                conf = high_count / (low_count + high_count)
                # Stretch to 0–1 range with some curvature
                conf = 0.2 + 0.6 * conf  # keep it between 0.2 and 0.8 for mixed signals

            log(f"Heuristic score: low markers={low_count}, high markers={high_count}, confidence={conf}")

    if conf is not None:
        try:
            requests.post(OVERLAY_URL, json={"confidence": conf}, timeout=1, proxies={"http": None, "https": None})
            log(f"Sent confidence {conf} to overlay")
        except Exception as e:
            log(f"Failed to update overlay: {e}")