from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import logging
from typing import Optional
import json
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Tamil AI Assistant", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCf-KNUi59GgWTRVKH1tBaabmSqoGPTJgk"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {e}")
    model = None

# Request models
class ChatRequest(BaseModel):
    message: str
    type: str = "generate"  # generate, explain, culture, grammar, story

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None
    timestamp: str

# System prompts for different types of requests
SYSTEM_PROMPTS = {
    "base": """நீங்கள் ஒரு தமிழ் AI உதவியாளர். உங்கள் பெயர் 'வணக்கம்'. நீங்கள் தமிழ் மொழி, கலாச்சாரம், இலக்கியம், வரலாறு மற்றும் பாரம்பரியம் பற்றிய நிபுணர்.

முக்கியமான வழிகாட்டுதல்கள்:
1. எப்போதும் தமிழில் பதில் அளிக்கவும்
2. பயனர் ஆங்கிலம், தமிழ் அல்லது தங்கிஷ் (Tanglish) மொழியில் கேட்டாலும், தமிழில் பதில் கொடுங்கள்
3. மிகவும் நட்புரீதியாக மற்றும் மரியாதையுடன் பேசுங்கள்
4. தமிழ் கலாச்சாரம் மற்றும் மரபுகளை பிரதிபலிக்கும் வகையில் பதில் அளிக்கவும்
5. உணர்ச்சிகரமான மற்றும் அர்த்தமுள்ள பதில்களை வழங்கவும்

நீங்கள் உதவ முடிந்த பகுதிகள்:
- தமிழ் மொழி கற்றல் மற்றும் இலக்கணம்
- தமிழ் இலக்கியம் மற்றும் கவிதைகள்
- தமிழ் கலாச்சாரம் மற்றும் பாரம்பரியம்
- தமிழ் வரலாறு மற்றும் பெருமைகள்
- கதைகள் மற்றும் புராணங்கள்
- தமிழ் பண்டிகைகள் மற்றும் சமயம்""",

    "story": """நீங்கள் ஒரு சிறந்த தமிழ் கதை சொல்லும் நிபுணர். உங்கள் கதைகள்:
1. பாரம்பரிய தமிழ் கதை பாணியில் இருக்க வேண்டும்
2. தமிழ் கலாச்சார மதிப்புகளை பிரதிபலிக்க வேண்டும்
3. சுவாரசியமாக மற்றும் கல்வி பயனுள்ளதாக இருக்க வேண்டும்
4. உண்மையான தமிழ் பாணியில் "ஒரு காலத்தில்..." என்று தொடங்க வேண்டும்
5. நெறிமுறை மற்றும் நல்ல மதிப்புகளை கற்பிக்க வேண்டும்""",

    "culture": """நீங்கள் தமிழ் கலாச்சாரம் மற்றும் பாரம்பரியத்தின் நிபுணர். உங்கள் பதில்கள்:
1. தமிழ் கலாச்சாரத்தின் செழுமையை விளக்க வேண்டும்
2. வரலாற்று உண்மைகளுடன் இருக்க வேண்டும்
3. பண்டிகைகள், சடங்குகள், கலைகள் பற்றி விரிவாக கூற வேண்டும்
4. தமிழர்களின் பெருமை மற்றும் சாதனைகளை வெளிப்படுத்த வேண்டும்
5. பாரம்பரிய மற்றும் நவீன தமிழ் கலாச்சாரத்தை இணைக்க வேண்டும்""",

    "grammar": """நீங்கள் தமிழ் இலக்கண நிபுணர். உங்கள் விளக்கங்கள்:
1. எளிமையான மற்றும் புரிந்துகொள்ளக்கூடிய முறையில் இருக்க வேண்டும்
2. உதாரணங்களுடன் விளக்க வேண்டும்
3. தொல்காப்பியம், நன்னூல் போன்ற பாரம்பரிய இலக்கண நூல்களை குறிப்பிட வேண்டும்
4. நடைமுறை பயன்பாட்டை காட்ட வேண்டும்
5. பிழைகளை சரிசெய்வதில் உதவ வேண்டும்""",

    "explain": """நீங்கள் ஒரு தமிழ் ஆசிரியர். உங்கள் விளக்கங்கள்:
1. படிப்படியாக மற்றும் தெளிவாக இருக்க வேண்டும்
2. எளிய தமிழில் கடினமான கருத்துக்களை விளக்க வேண்டும்
3. தமிழ் மொழியின் சொல்லாற்றலை பயன்படுத்த வேண்டும்
4. உதாரணங்கள் மற்றும் ஒப்புமைகளை பயன்படுத்த வேண்டும்
5. கற்பவரின் ஆர்வத்தை தூண்ட வேண்டும்"""
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "வணக்கம்! Tamil AI Assistant Backend is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Gemini API connection
        test_response = model.generate_content("வணக்கம்")
        return {
            "status": "healthy",
            "gemini_api": "connected",
            "model": "gemini-2.0-flash-exp",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Main chat endpoint for Tamil AI assistant"""
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized")
        
        # Get appropriate system prompt based on request type
        system_prompt = SYSTEM_PROMPTS.get(request.type, SYSTEM_PROMPTS["base"])
        
        # Create the full prompt
        full_prompt = f"""{system_prompt}

பயனர் செய்தி: {request.message}

தயவுசெய்து மேலே உள்ள வழிகாட்டுதல்களின் படி தமிழில் பதில் அளிக்கவும்."""

        # Generate response using Gemini
        logger.info(f"Processing {request.type} request: {request.message[:50]}...")
        
        response = model.generate_content(full_prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Empty response from Gemini API")
        
        # Clean and format the response
        formatted_response = clean_response(response.text)
        
        logger.info(f"Generated response length: {len(formatted_response)}")
        
        return ChatResponse(
            response=formatted_response,
            audio_url=None,  # Can be implemented later for text-to-speech
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        
        # Provide user-friendly Tamil error messages
        error_message = get_tamil_error_message(str(e))
        raise HTTPException(status_code=500, detail=error_message)

def clean_response(text: str) -> str:
    """Clean and format the AI response"""
    # Remove any unwanted characters or formatting
    cleaned_text = text.strip()
    
    # Add emojis based on content for better UX
    if any(word in cleaned_text for word in ['கதை', 'story', 'ஒரு காலத்தில்']):
        cleaned_text = f"📚 {cleaned_text}"
    elif any(word in cleaned_text for word in ['கலாச்சார', 'பண்பாடு', 'culture']):
        cleaned_text = f"🏛️ {cleaned_text}"
    elif any(word in cleaned_text for word in ['இலக்கண', 'grammar']):
        cleaned_text = f"📖 {cleaned_text}"
    elif any(word in cleaned_text for word in ['விளக்க', 'explain']):
        cleaned_text = f"💡 {cleaned_text}"
    else:
        cleaned_text = f"✨ {cleaned_text}"
    
    return cleaned_text

def get_tamil_error_message(error: str) -> str:
    """Convert error messages to user-friendly Tamil messages"""
    if "quota" in error.lower() or "limit" in error.lower():
        return "மன்னிக்கவும், API வரம்பு முடிந்துவிட்டது. சிறிது நேரம் கழித்து முயற்சிக்கவும். 🙏"
    elif "network" in error.lower() or "connection" in error.lower():
        return "இணையதள இணைப்பில் சிக்கல். தயவுசெய்து உங்கள் இணைப்பை சரிபார்க்கவும். 🌐"
    elif "api" in error.lower():
        return "API சேவையில் தற்காலிக சிக்கல். சிறிது நேரம் கழித்து முயற்சிக்கவும். ⚡"
    elif "empty response" in error.lower():
        return "மன்னிக்கவும், பதில் உருவாக்க முடியவில்லை. மீண்டும் வேறு விதமாக கேட்கவும். 🤔"
    else:
        return f"எதிர்பாராத பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும். 🙏 ({error[:50]}...)"

# Additional endpoints for specific features

@app.post("/story")
async def generate_story(request: ChatRequest):
    """Dedicated endpoint for story generation"""
    request.type = "story"
    return await chat_with_ai(request)

@app.post("/culture")
async def explain_culture(request: ChatRequest):
    """Dedicated endpoint for cultural explanations"""
    request.type = "culture"
    return await chat_with_ai(request)

@app.post("/grammar")
async def explain_grammar(request: ChatRequest):
    """Dedicated endpoint for grammar explanations"""
    request.type = "grammar"
    return await chat_with_ai(request)

@app.post("/explain")
async def explain_concept(request: ChatRequest):
    """Dedicated endpoint for general explanations"""
    request.type = "explain"
    return await chat_with_ai(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)