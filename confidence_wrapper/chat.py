#!/usr/bin/env python3
from wrapper import compute_confidence, get_visual_indicator, get_llama_response

def start_chat():
    print("\n--- OpenOcchio Chat ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit"]:
                break
            
            print("AI is thinking...", end="\r")
            # Get model response
            data = get_llama_response(user_input, temperature=0.0)
            answer = data['response']
            
            # Compute confidence
            conf = compute_confidence(user_input)
            
            print(f"🤖 AI: {answer}")
            print(f"📊 {get_visual_indicator(conf)}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_chat()
