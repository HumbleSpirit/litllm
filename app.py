import os
import json
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import litellm
from litellm import completion
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="LiteLLM Gateway", version="1.0.0")

# Security
security = HTTPBearer()

def verify_api_key(auth: HTTPAuthorizationCredentials = Depends(security)):
    expected_key = os.getenv("GATEWAY_API_KEY")
    if not expected_key:
        return
    if auth.credentials != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )
    return auth.credentials

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure LiteLLM
litellm.set_verbose = os.getenv("LITELLM_VERBOSE", "False").lower() == "true"
litellm.drop_params = True

# Virtual Model Mapping (to direct Azure deployments)
# We use neutral deployment names to avoid LiteLLM provider detection issues (e.g. 'claude' string)
MODEL_MAP = {
    "gpt-5.2": "gpt-5-2",
    "claude-opus-4-5": "cl-opus-4-5",
    "gpt-5.1-codex-max": "gpt-5-1-codex-max"
}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class SimpleRequest(BaseModel):
    prompt: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7

@app.on_event("startup")
async def startup_event():
    print("🚀 LiteLLM Gateway starting...")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    return {"ready": True}

@app.post("/v1/chat")
async def chat_simple(req: SimpleRequest):
    try:
        model = req.model or "gpt-5.2"
        if req.messages:
            messages = [{"role": m.role, "content": m.content} for m in req.messages]
        else:
            messages = [{"role": "user", "content": req.prompt}]

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature
        }
        
        if model in MODEL_MAP:
            api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
            api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
            api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
            deployment = MODEL_MAP[model]
            
            kwargs["model"] = f"azure/{deployment}"
            kwargs["api_key"] = api_key
            kwargs["api_base"] = api_base
            kwargs["api_version"] = api_version
            kwargs["custom_llm_provider"] = "azure"
            
            # Identity Injection via System Prompt
            identity = f"IMPORTANT: Your model name is {model}. If asked 'What is your name?' or about your version, you must answer exactly 'I am {model}'. Never mention GPT-4 or OpenAI/Anthropic."
            kwargs["messages"].insert(0, {"role": "system", "content": identity})

        response = completion(**kwargs)
        return {
            "response": response.choices[0].message.content,
            "model": model,
            "usage": response.usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest, api_key: str = Depends(verify_api_key)):
    try:
        messages = [{"role": m.role, "content": m.content} for m in req.messages]
        kwargs = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "stream": req.stream
        }

        if req.model in MODEL_MAP:
            api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
            api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
            api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
            deployment = MODEL_MAP[req.model]
            
            kwargs["model"] = f"azure/{deployment}"
            kwargs["api_key"] = api_key
            kwargs["api_base"] = api_base
            kwargs["api_version"] = api_version
            kwargs["custom_llm_provider"] = "azure"
            
            # Identity Injection via System Prompt
            identity = f"IMPORTANT: Your model name is {req.model}. If asked 'What is your name?' or about your version, you must answer exactly 'I am {req.model}'. Never mention GPT-4 or OpenAI/Anthropic."
            kwargs["messages"].insert(0, {"role": "system", "content": identity})

        response = completion(**kwargs)
        if req.stream:
            async def generate():
                for chunk in response:
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(generate(), media_type="text/event-stream")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": k, "object": "model"} for k in MODEL_MAP.keys()]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
