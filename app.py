import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import litellm
from litellm import completion
import json

app = FastAPI(title="LiteLLM Gateway", version="1.0.0")

# Configure LiteLLM
litellm.set_verbose = os.getenv("LITELLM_VERBOSE", "False").lower() == "true"

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
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7

@app.on_event("startup")
async def startup_event():
    """Initialize LiteLLM configuration"""
    print("🚀 LiteLLM Gateway starting...")
    print(f"Available models configured via environment variables")
    
    # LiteLLM automatically uses API keys from environment:
    # OPENAI_API_KEY, AZURE_API_KEY, ANTHROPIC_API_KEY, etc.
    
    # Configure Azure Foundry specific mappings if needed
    # This is a basic setup; for more complex routing, LiteLLM's router or config.yaml is better.
    # Here we assume environment variables are set for the default Azure provider if used directly,
    # or we rely on LiteLLM's ability to handle multiple azure configs if properly named.
    # For simplicity in this script, we'll assume the user sets AZURE_API_KEY/BASE etc for one main azure account
    # OR uses specific model names that LiteLLM recognizes if they map to different env vars.
    pass
    
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve simple web UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LiteLLM Chat Interface</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 1200px;
                height: 80vh;
                min-height: 500px;
                max-height: 900px;
                display: flex;
                flex-direction: column;
                resize: both;
                overflow: hidden;
            }
            .header {
                padding: 20px;
                border-bottom: 1px solid #e0e0e0;
                background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                color: white;
                border-radius: 16px 16px 0 0;
                flex-shrink: 0;
            }
            .header h1 { font-size: 24px; margin-bottom: 8px; }
            .header p { opacity: 0.9; font-size: 14px; }
            .messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .message {
                margin-bottom: 16px;
                display: flex;
                gap: 12px;
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user { justify-content: flex-end; }
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 12px;
                word-wrap: break-word;
                line-height: 1.5;
            }
            .message.user .message-content {
                background: #48bb78;
                color: white;
            }
            .message.assistant .message-content {
                background: white;
                border: 1px solid #e0e0e0;
                color: #333;
            }
            .message-content h1, .message-content h2, .message-content h3 {
                margin-top: 12px;
                margin-bottom: 8px;
            }
            .message-content h1 { font-size: 1.5em; }
            .message-content h2 { font-size: 1.3em; }
            .message-content h3 { font-size: 1.1em; }
            .message-content p { margin-bottom: 8px; }
            .message-content ul, .message-content ol {
                margin-left: 20px;
                margin-bottom: 8px;
            }
            .message-content li { margin-bottom: 4px; }
            .message-content pre {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                margin: 8px 0;
            }
            .message-content code {
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
            .message-content pre code {
                background: transparent;
                padding: 0;
            }
            .message-content blockquote {
                border-left: 4px solid #48bb78;
                padding-left: 12px;
                margin: 8px 0;
                color: #666;
            }
            .message-content table {
                border-collapse: collapse;
                width: 100%;
                margin: 8px 0;
            }
            .message-content th, .message-content td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .message-content th {
                background: #f0f0f0;
                font-weight: bold;
            }
            .input-area {
                padding: 20px;
                border-top: 1px solid #e0e0e0;
                background: white;
                border-radius: 0 0 16px 16px;
                flex-shrink: 0;
            }
            .model-selector {
                margin-bottom: 12px;
            }
            .model-selector select {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
            }
            .input-group {
                display: flex;
                gap: 12px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
            }
            button {
                padding: 12px 24px;
                background: #48bb78;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.2s;
            }
            button:hover { background: #38a169; }
            button:disabled { 
                background: #ccc;
                cursor: not-allowed;
            }
            .loading {
                text-align: center;
                padding: 12px;
                color: #666;
                font-style: italic;
            }
            .resize-handle {
                position: absolute;
                bottom: 0;
                right: 0;
                width: 20px;
                height: 20px;
                cursor: nwse-resize;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 LiteLLM Gateway</h1>
                <p>Chat with AI models via LiteLLM proxy • Markdown supported</p>
            </div>
            
            <div class="messages" id="messages">
                <div class="message assistant">
                    <div class="message-content">
                        <strong>Hello!</strong> I'm ready to help. Ask me anything!<br>
                        <em>Responses support markdown formatting.</em>
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="model-selector">
                    <select id="modelSelect">
                        <option value="azure/gpt-4">Azure GPT-4</option>
                        <option value="azure/gpt-5">Azure GPT-3.5</option>
                        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Anthropic)</option>
                    </select>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message..." />
                    <button onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
            </div>
        </div>

        <script>
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const modelSelect = document.getElementById('modelSelect');

            // Configure marked options
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: false,
                mangle: false
            });

            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            function addMessage(role, content, isMarkdown = false) {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${role}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                
                if (isMarkdown && role === 'assistant') {
                    contentDiv.innerHTML = marked.parse(content);
                } else {
                    contentDiv.textContent = content;
                }
                
                msgDiv.appendChild(contentDiv);
                messagesDiv.appendChild(msgDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                const model = modelSelect.value;
                
                addMessage('user', message);
                messageInput.value = '';
                sendBtn.disabled = true;

                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'loading';
                loadingDiv.textContent = 'Thinking...';
                messagesDiv.appendChild(loadingDiv);

                try {
                    const response = await fetch('/v1/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            prompt: message,
                            model: model,
                            max_tokens: 1024,
                            temperature: 0.7
                        })
                    });

                    loadingDiv.remove();

                    if (!response.ok) {
                        const error = await response.json();
                        addMessage('assistant', `Error: ${error.detail || 'Unknown error'}`);
                        return;
                    }

                    const data = await response.json();
                    addMessage('assistant', data.response, true);
                    
                } catch (error) {
                    loadingDiv.remove();
                    addMessage('assistant', `Error: ${error.message}`);
                } finally {
                    sendBtn.disabled = false;
                    messageInput.focus();
                }
            }
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "litellm-gateway"}

@app.get("/ready")
async def ready():
    """Readiness check"""
    return {"ready": True, "service": "litellm-gateway"}

@app.post("/v1/chat")
async def chat_simple(req: SimpleRequest):
    """Simplified chat endpoint for web UI"""
    try:
        model = req.model or os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": req.prompt}],
            "max_tokens": req.max_tokens,
            "temperature": req.temperature
        }
        
        # Inject Azure Foundry credentials if using Azure models
        if model.startswith("azure/"):
            if "gpt-4" in model:
                api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
                api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
                api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
                deployment = os.getenv("AZURE_GPT4_DEPLOYMENT", "gpt-4")
                
                # Use 'azure' provider for Standard Azure resources
                kwargs["model"] = f"azure/{deployment}"
                kwargs["api_key"] = api_key
                kwargs["api_base"] = api_base
                kwargs["api_version"] = api_version
                
            elif "gpt-5" in model:
                api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
                api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
                api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
                deployment = os.getenv("AZURE_GPT5_DEPLOYMENT", "gpt-5")
                
                kwargs["model"] = f"azure/{deployment}"
                kwargs["api_key"] = api_key
                kwargs["api_base"] = api_base
                kwargs["api_version"] = api_version

        response = completion(**kwargs)
        
        return {
            "response": response.choices[0].message.content,
            "model": model,
            "usage": response.usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
        
        kwargs = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "stream": req.stream
        }

        # Inject Azure Foundry credentials if using Azure models
        if req.model.startswith("azure/"):
            if "gpt-4" in req.model:
                api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
                api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
                api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
                deployment = os.getenv("AZURE_GPT4_DEPLOYMENT", "gpt-4")
                
                print(f"DEBUG: Using Foundry Config for GPT-4. Base: {api_base}, Deployment: {deployment}")
                
                # Use 'azure' provider for Standard Azure resources (created by setup script)
                # This ensures 'api-key' header is used, not 'Authorization: Bearer'
                kwargs["model"] = f"azure/{deployment}"
                kwargs["api_key"] = api_key
                kwargs["api_base"] = api_base
                kwargs["api_version"] = api_version
                
            elif "gpt-5" in req.model:
                api_key = os.getenv("AZURE_FOUNDRY_API_KEY")
                api_base = os.getenv("AZURE_FOUNDRY_API_BASE")
                api_version = os.getenv("AZURE_FOUNDRY_API_VERSION")
                deployment = os.getenv("AZURE_GPT5_DEPLOYMENT", "gpt-5")
                
                print(f"DEBUG: Using Foundry Config for GPT-5. Base: {api_base}, Deployment: {deployment}")
                
                kwargs["model"] = f"azure/{deployment}"
                kwargs["api_key"] = api_key
                kwargs["api_base"] = api_base
                kwargs["api_version"] = api_version

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
    """List available models"""
    return {
        "object": "list",
        "data": [
            {"id": "gpt-3.5-turbo", "object": "model"},
            {"id": "gpt-4", "object": "model"},
            {"id": "claude-3-5-sonnet-20241022", "object": "model"},
            {"id": "azure/gpt-4", "object": "model"},
            {"id": "azure/gpt-5", "object": "model"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)