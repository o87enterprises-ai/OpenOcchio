#!/usr/bin/env python3
import requests
import json
import numpy as np
import sys
import re

# -------------------------------
# Configuration
# -------------------------------
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"   # Better semantic calibration
CONFIDENCE_THRESHOLD = 0.65   # default threshold

def get_llama_response(prompt, temperature=0.0):
    """Get response and token logprobs (if available)."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 100,
            "logprobs": True
        }
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=10)
        if resp.status_code != 200:
            return {"response": f"Error: Ollama returned {resp.status_code}", "logprobs": []}
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"response": f"Connection Error: {e}", "logprobs": []}

def confidence_from_logprobs(logprobs_list):
    """Convert per-token logprobs to a confidence score."""
    if not logprobs_list: return 0.5
    probs = []
    for lp in logprobs_list:
        if isinstance(lp, dict):
            val = lp.get('logprob')
            if val is not None: probs.append(np.exp(val))
        elif isinstance(lp, (int, float)):
            probs.append(np.exp(lp))
    if not probs: return 0.5
    return float(np.mean(probs))

def detect_refusal(text):
    """Detect if the AI is refusing to answer or admitting inability."""
    refusal_patterns = [
        r"as an? (?:ai|artificial intelligence|language model)",
        r"i (?:cannot|can't|am unable to) (?:answer|provide|respond|describe)",
        r"i don't have (?:a|the) (?:ability|capacity|correct answer)",
        r"there is no (?:real|correct|objective) answer",
        r"it is (?:not possible|impossible) to (?:know|tell|describe)",
        r"subjective",
        r"opinion-based",
        r"i (?:apologize|am sorry)",
    ]
    for pattern in refusal_patterns:
        if re.search(pattern, text.lower()):
            return True
    return False

def self_consistency_confidence(prompt, num_samples=5):
    """
    Generate multiple responses and compare.
    Includes refusal detection to handle questions with no real answer.
    """
    responses = []
    refusal_count = 0
    for _ in range(num_samples):
        try:
            data = get_llama_response(prompt, temperature=0.7)
            res_text = data['response'].strip()
            responses.append(res_text)
            if detect_refusal(res_text):
                refusal_count += 1
        except Exception as e:
            continue
    
    if not responses:
        return 0.0
    
    # If a majority of responses are refusals, it's a "no real answer" case
    # We treat this as inherently lower confidence in the "correctness" of the answer
    refusal_ratio = refusal_count / len(responses)
    
    if all(r == responses[0] for r in responses) and refusal_ratio == 0:
        return 1.0

    # Hybrid approach: Count-based Cosine Similarity + Jaccard
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    try:
        vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b|[^\w\s]', use_idf=False).fit(responses)
        vectors = vectorizer.transform(responses)
        sim_matrix = cosine_similarity(vectors)
        n = len(responses)
        avg_cos_sim = (sim_matrix.sum() - n) / (n * (n - 1))
        
        def get_unigrams(text):
            return set(re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).split())

        j_sims = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                u1, u2 = get_unigrams(responses[i]), get_unigrams(responses[j])
                j_sims.append(len(u1.intersection(u2)) / len(u1.union(u2)) if u1 or u2 else 1.0)
        avg_j_sim = sum(j_sims) / len(j_sims)

        final_sim = 0.6 * avg_cos_sim + 0.4 * avg_j_sim
        
        # Apply refusal penalty: if they all refuse consistently, the score drops
        # because the user wants to identify "inability to receive a suitable response"
        if refusal_ratio > 0.5:
            final_sim = final_sim * (1.0 - (refusal_ratio * 0.5))
            
        return float(max(0.0, min(1.0, final_sim)))
    except Exception:
        return 0.5

def compute_confidence(prompt, use_logprobs=True):
    if use_logprobs:
        try:
            data = get_llama_response(prompt, temperature=0.0)
            if 'logprobs' in data: 
                logprob_conf = confidence_from_logprobs(data['logprobs'])
                # If the top response is a refusal, pull down the logprob confidence
                if detect_refusal(data['response']):
                    logprob_conf *= 0.5
                return logprob_conf
        except: pass
    return self_consistency_confidence(prompt)

def interpret_confidence(conf):
    """
    Returns (label, color_code, score_text)
    Labels: Confident, Not so confident, Unsure, Kind of insecure, Insecure
    """
    if conf >= 0.8:
        return "Confident", "\033[92m", "Confident" # Green
    elif conf >= 0.6:
        return "Not so confident", "\033[93m", "Not so confident" # Yellowish/Light Green
    elif conf >= 0.4:
        return "Unsure", "\033[33m", "Unsure" # Yellow/Orange
    elif conf >= 0.2:
        return "Kind of insecure", "\033[31m", "Kind of insecure" # Red/Orange
    else:
        return "Insecure", "\033[41m\033[37m", "Insecure" # Bright Red background

def get_visual_indicator(conf):
    label, color, score = interpret_confidence(conf)
    bar_width = 20
    filled_width = int(conf * bar_width)
    empty_width = bar_width - filled_width
    
    # Use different colors for the bar itself based on confidence
    bar = f"{color}█" * filled_width + "\033[0m" + "░" * empty_width
    return f"[{bar}] {conf:.2f} - {color}{score}\033[0m"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wrapper.py 'Your prompt here'")
        sys.exit(1)
    prompt = sys.argv[1]
    conf = compute_confidence(prompt)
    print(get_visual_indicator(conf))
