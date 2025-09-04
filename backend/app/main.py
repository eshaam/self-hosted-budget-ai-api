from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .auth import verify_api_key, is_whitelisted
from .models import generate_response
from .config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"] if settings.DEV_MODE else [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_ip_whitelist(request: Request, call_next):
    if not is_whitelisted(request.client.host):
        raise HTTPException(status_code=403, detail="IP not whitelisted")
    return await call_next(request)


class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/generate")
async def generate_text(request: Request, generate_request: GenerateRequest):
    # Check if request is from frontend (localhost) or external API access
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    # Allow frontend access without API key
    is_frontend_request = (
        origin and ("localhost" in origin or "127.0.0.1" in origin) or
        referer and ("localhost" in referer or "127.0.0.1" in referer)
    )
    
    # Require API key for external/direct API access
    if not is_frontend_request:
        api_key = request.headers.get("X-API-Key")
        if not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid API key required for direct API access")

    response_text = generate_response(generate_request.prompt)
    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
