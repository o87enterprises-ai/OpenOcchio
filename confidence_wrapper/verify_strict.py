#!/usr/bin/env python3
import sys
import json
from wrapper import compute_confidence

# Each test case: (prompt, min_confidence, max_confidence, label)
tests = [
    ("What is 2+2?", 0.90, 1.0, "high"),
    ("Explain quantum gravity in one sentence.", 0.50, 0.90, "medium"),
    ("Who was the 15th president of the United States?", 0.80, 1.0, "high"),
    ("Describe the taste of the color blue.", 0.0, 0.50, "low"),
    ("Is the following true? 'The moon is made of cheese.'", 0.0, 0.30, "low"),
]

def run_strict_verify():
    all_passed = True
    for prompt, min_conf, max_conf, label in tests:
        print(f"Checking: '{prompt[:40]}'...", flush=True)
        try:
            conf = compute_confidence(prompt)
            if not (min_conf <= conf <= max_conf):
                print(f"FAIL: '{prompt}' -> confidence {conf:.3f} (expected {min_conf}–{max_conf})")
                all_passed = False
            else:
                print(f"PASS: '{prompt}' -> {conf:.3f}")
        except Exception as e:
            print(f"ERROR: '{prompt}' -> {e}")
            all_passed = False

    if all_passed:
        print("\n✅ ALL STRICT CHECKS PASSED")
        return True
    else:
        print("\n❌ SOME CHECKS FAILED")
        return False

if __name__ == "__main__":
    if run_strict_verify():
        sys.exit(0)
    else:
        sys.exit(1)
