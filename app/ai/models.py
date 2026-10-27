from google import genai
from app.core.config import settings

def get_genai_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

client = None
if settings.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass