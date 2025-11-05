import os  
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel  
from model_runner import ModelRunner  
  
app = FastAPI()  
model = None  
  
class InferenceRequest(BaseModel):  
    prompt: str  
    max_tokens: int = 256  
    model_id: str | None = None  
  
@app.on_event("startup")  
async def startup_event():  
    global model  
    model_path = os.environ.get("MODEL_PATH", "/models")  
    default_model = os.environ.get("DEFAULT_MODEL", "default")  
    model = ModelRunner(default_model, model_path)  
    model.load()  
  
@app.get("/health")  
async def health():  
    return {"status": "ok"}  
  
@app.get("/ready")  
async def ready():  
    return {"ready": model is not None and model.loaded()}  
  
@app.post("/predict")  
async def predict(req: InferenceRequest):  
    if model is None:  
        raise HTTPException(status_code=500, detail="Model runner not initialized")  
    out = model.predict(req.prompt, max_tokens=req.max_tokens, model_id=req.model_id)  
    return out  
    