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
    mode: str = "generate"          # "generate" (Ask AI) or "verify" (Analyze Text)
    model: str = "llama3-8b-8192"   # can be any Groq model
    temperature: float = 0.0
    max_tokens: int = 256

@app.post("/confidence")
def get_confidence(input: PromptInput):
    if not client:
        return {"error": "GROQ_API_KEY environment variable not set", "status": 500}
    
    if input.mode == "verify":
        # JUDGE MODE: Analyze existing text for confidence markers
        judge_prompt = (
            f"Analyze the following AI response for CONFIDENCE markers. "
            f"Rate how sure the AI sounds on a scale of 0 to 100. "
            f"Consider hedging (e.g., 'maybe', 'I think') as low confidence. "
            f"Respond ONLY with the number.\n\n"
            f"AI Response to Analyze: \"{input.prompt}\"\n\n"
            f"Confidence Score:"
        )
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": judge_prompt}],
            model=input.model,
            temperature=0.0,
            max_tokens=10,
        )
        try:
            score_text = chat_completion.choices[0].message.content.strip()
            # Extract number
            match = re.search(r'\d+', score_text)
            score = float(match.group()) / 100.0 if match else 0.5
            return {"confidence": round(score, 4), "model": input.model, "method": "judge-analysis"}
        except:
            return {"confidence": 0.5, "model": input.model, "method": "judge-error"}

    # GENERATION MODE: Ask AI and get logprobs
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
