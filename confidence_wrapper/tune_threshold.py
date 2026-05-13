import json
from wrapper import compute_confidence
import numpy as np
from sklearn.metrics import confusion_matrix

# Build a larger dataset (you can annotate 20–30 prompts manually)
prompts = [
    ("What is the boiling point of water at sea level?", 1, "high"),
    ("Explain the plot of the movie 'Inception'.", 1, "high"),
    ("Write a haiku about a rusty hinge.", 0, "low"),
    ("Predict the exact price of Bitcoin on Jan 1, 2027.", 0, "low"),
    ("Summarize the theory of relativity in two sentences.", 1, "high"),
    ("How many angels can dance on the head of a pin?", 0, "low"),
]

def tune():
    y_true = []
    y_scores = []
    print("Collecting confidence scores for tuning...")
    for prompt, _, truth_label in prompts:
        conf = compute_confidence(prompt)
        y_scores.append(conf)
        y_true.append(1 if truth_label == "high" else 0)
        print(f"Prompt: {prompt[:30]}... | Score: {conf:.3f} | Truth: {truth_label}")

    # Try thresholds from 0.1 to 0.9
    best_acc = 0
    best_thresh = 0.5
    for thresh in np.arange(0.1, 0.95, 0.05):
        pred = [1 if s >= thresh else 0 for s in y_scores]
        acc = sum(p == t for p, t in zip(pred, y_true)) / len(y_true)
        if acc > best_acc:
            best_acc = acc
            best_thresh = thresh

    print(f"\nOptimal confidence threshold = {best_thresh:.2f} (accuracy {best_acc:.0%})")
    return best_thresh

if __name__ == "__main__":
    tune()
