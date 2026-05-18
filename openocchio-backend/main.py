import os
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# Allow frontend to call from any origin (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    # We'll allow it to start but endpoint will fail, 
    # so user can set it in HF Space settings later.
    client = None
else:
    client = Groq(api_key=api_key)

class PromptInput(BaseModel):
    prompt: str
    model: str = "llama3-8b-8192"   # can be any Groq model
    temperature: float = 0.0
    max_tokens: int = 256

def confidence_from_logprobs(logprobs_list):
    """Convert token logprobs to a confidence score 0-1."""
    if not logprobs_list:
        return 0.5
    # logprobs are negative; exp to probability
    probs = [math.exp(lp) for lp in logprobs_list if lp is not None]
    if not probs:
        return 0.5
    avg = sum(probs) / len(probs)
    return min(1.0, max(0.0, avg))

@app.post("/confidence")
def get_confidence(input: PromptInput):
    if not client:
        return {"error": "GROQ_API_KEY environment variable not set", "status": 500}
        
    # Call Groq with logprobs enabled
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": input.prompt}],
        model=input.model,
        temperature=input.temperature,
        max_tokens=input.max_tokens,
        logprobs=True,          # request token logprobs
        top_logprobs=1,
    )
    # Extract logprobs from response (Groq returns logprob objects)
    token_logprobs = []
    # The response object contains logprobs for each token in choices[0].logprobs.content
    if chat_completion.choices[0].logprobs and chat_completion.choices[0].logprobs.content:
        for token_info in chat_completion.choices[0].logprobs.content:
            if token_info.logprob is not None:
                token_logprobs.append(token_info.logprob)
    else:
        # Fallback: no logprobs (unlikely with Groq)
        return {"confidence": 0.5, "model": input.model, "method": "fallback"}

    score = confidence_from_logprobs(token_logprobs)
    return {"confidence": round(score, 4), "model": input.model, "method": "logprobs"}

# Health check
@app.get("/")
def root():
    return {"status": "ok", "service": "OpenOcchio Confidence API"}
