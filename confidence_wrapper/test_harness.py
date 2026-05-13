import json
from wrapper import compute_confidence

# Define a ground-truth dataset
test_cases = [
    ("What is 2+2?", 0.95, "high"),        # high confidence expected
    ("Explain quantum gravity in one sentence.", 0.70, "medium"),
    ("Who was the 15th president of the United States?", 0.85, "high"),
    ("Describe the taste of the color blue.", 0.30, "low"),
    ("Is the following true? 'The moon is made of cheese.'", 0.20, "low"),
]

def run_harness():
    results = []
    print(f"{'Label':5} | {'Conf':7} | {'Prompt'}")
    print("-" * 50)
    for prompt, expected_conf, label in test_cases:
        conf = compute_confidence(prompt)
        results.append({"prompt": prompt[:50], "confidence": conf, "label": label})
        print(f"{label:5} | {conf:.3f} | {prompt[:50]}")

    # Save for analysis
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Simple accuracy: are low prompts <=0.5 and high prompts >=0.7?
    correct = 0
    for r in results:
        if r["label"] == "high" and r["confidence"] >= 0.7:
            correct += 1
        elif r["label"] == "low" and r["confidence"] <= 0.5:
            correct += 1
        elif r["label"] == "medium": # accept medium as is for now
            correct += 1
    
    accuracy_pct = (correct/len(results)) * 100
    print(f"\nSimple accuracy: {correct}/{len(results)} = {accuracy_pct:.0f}%")
    return correct == len(results)

if __name__ == "__main__":
    run_harness()
