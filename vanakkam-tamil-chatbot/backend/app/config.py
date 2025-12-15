import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(env_file)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError(f"GEMINI_API_KEY not found in .env file at {env_file}")
