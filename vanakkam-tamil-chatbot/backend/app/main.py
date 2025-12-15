from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from .models import ChatRequest, ChatResponse
from .prompts import BASE_PROMPT
from .gemini import generate_reply
from .utils import format_error

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vanakkam Tamil AI",
    description="Tamil AI Chatbot Assistant",
    version="1.0.0"
)

# CORS Middleware - Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Dev & prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "service": "Vanakkam Tamil AI"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Chat endpoint - accepts Tamil messages and returns AI responses"""
    try:
        if not req.message or not req.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Processing message: {req.message[:50]}...")
        
        full_prompt = f"{BASE_PROMPT}\nபயனர்: {req.message}"
        reply = generate_reply(full_prompt)
        
        logger.info("Response generated successfully")
        return ChatResponse(response=reply)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=format_error(str(e))
        )
