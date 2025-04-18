# api/main.py
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Allow CORS for all origins (replace with your frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Your React app's origin
    allow_methods=["*"],  # Include OPTIONS
    allow_headers=["*"],
)

# Dependency injection for service
def get_chat_service():
    service_type = os.getenv("CHAT_SERVICE", "AzureChatService")  # Default to HFService
    if service_type == "AzureChatService":
        from api.services.azure_service import AzureChatService
        return AzureChatService()
    elif service_type == "HFService":
        from temp.hf_service import HFService
        return HFService()
    else:
        raise ValueError(f"Unsupported chat service: {service_type}")

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(
    request: ChatRequest,
    chat_service=Depends(get_chat_service)  # Use dynamic service
):
    try:
        response = chat_service.generate_response(
            request.session_id,
            request.message
        )
        return {"response": response}
    except Exception as e:
        # Log the error (e.g., using logging.error(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )

@app.get("/history/{session_id}")
async def get_history(
    session_id: str,
    chat_service=Depends(get_chat_service)  # Use dynamic service
):
    try:
        # Get last 10 messages for session
        return chat_service.db.get_history(session_id, limit=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def get_sessions(
    chat_service=Depends(get_chat_service)  # Use dynamic service
):
    try:
        # Get all sessions
        return chat_service.db.get_all_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint for monitoring"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }