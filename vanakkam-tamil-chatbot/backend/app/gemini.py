import google.generativeai as genai
from .config import GEMINI_API_KEY, MODEL_NAME

genai.configure(api_key=GEMINI_API_KEY)

# Get available model by checking what's actually available
def get_available_model():
    try:
        # First try the configured model with proper format
        model_name = f"models/{MODEL_NAME}" if not MODEL_NAME.startswith("models/") else MODEL_NAME
        test_model = genai.GenerativeModel(model_name)
        print(f"Using configured model: {model_name}")
        return model_name
    except Exception as e:
        print(f"Configured model not available: {e}")
    
    # Try to list available models and use the first one that supports generateContent
    try:
        models = genai.list_models()
        for model in models:
            if "generateContent" in model.supported_generation_methods:
                model_name = model.name
                print(f"Found available model: {model_name}")
                return model_name
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Fallback to known models in order of preference
    fallback_models = [
        "models/gemini-2.5-pro",
        "models/gemini-2.5-flash",
        "models/gemini-pro-latest",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-pro"
    ]
    
    for model_name in fallback_models:
        try:
            test_model = genai.GenerativeModel(model_name)
            print(f"Using fallback model: {model_name}")
            return model_name
        except Exception:
            continue
    
    # Final fallback
    return f"models/{MODEL_NAME}"

model_name = get_available_model()
model = genai.GenerativeModel(model_name)

def generate_reply(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            raise RuntimeError("Empty response from Gemini")

        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")
