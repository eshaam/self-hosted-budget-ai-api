from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .auth import verify_api_key, is_whitelisted
from .models import generate_response, get_available_models, get_current_model
from .config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://self-hosted-budget-ai-api.eshaam.co.za"
    ] if settings.DEV_MODE else [
        "https://self-hosted-budget-ai-api.eshaam.co.za"
    ],
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
    model: str = None  # Optional model selection

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/generate")
async def generate_text(request: Request, generate_request: GenerateRequest):
    try:
        print(f"Received request with prompt: {generate_request.prompt}")
        
        # Check if request is from frontend (localhost) or external API access
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        
        print(f"Origin: {origin}, Referer: {referer}")
        
        # Allow frontend access without API key
        is_frontend_request = (
            origin and ("localhost" in origin or "127.0.0.1" in origin or "self-hosted-budget-ai-api.eshaam.co.za" in origin) or
            referer and ("localhost" in referer or "127.0.0.1" in referer or "self-hosted-budget-ai-api.eshaam.co.za" in referer)
        )
        
        print(f"Is frontend request: {is_frontend_request}")
        
        # Require API key for external/direct API access
        if not is_frontend_request:
            api_key = request.headers.get("X-API-Key")
            if not verify_api_key(api_key):
                raise HTTPException(status_code=401, detail="Invalid API key required for direct API access")

        print("About to call generate_response with 10min timeout")
        
        # Run model generation in thread pool to avoid blocking
        import asyncio
        import concurrent.futures
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            try:
                # Wait up to 10 minutes for response
                response_text = await asyncio.wait_for(
                    loop.run_in_executor(executor, generate_response, generate_request.prompt, generate_request.model), 
                    timeout=600.0
                )
                print(f"Generated response: {response_text[:100]}...")
                return {"response": response_text}
            except asyncio.TimeoutError:
                print("Request timed out after 10 minutes")
                return {"response": "I apologize, but your request is taking longer than expected to process. Please try with a shorter prompt or try again later."}
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in generate_text: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/models")
async def get_models():
    """Get available models"""
    return {
        "available_models": get_available_models(),
        "current_model": get_current_model()
    }

@app.post("/api/models/{model_name}")
async def switch_model(model_name: str):
    """Switch to a different model"""
    available = get_available_models()
    if model_name not in available and model_name not in available.values():
        raise HTTPException(status_code=400, detail=f"Model {model_name} not available")
    
    # Test loading the model
    try:
        test_response = generate_response("Hello", model_name)
        return {
            "message": f"Successfully switched to {model_name}",
            "current_model": get_current_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model {model_name}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
