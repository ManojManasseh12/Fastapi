from google import genai
from app.core.config import settings

<<<<<<< HEAD
def get_genai_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

client = None
if settings.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass
=======
client=genai.Client(api_key="setting.GEMINI_API_KEY")
>>>>>>> 4a480110f464f2dfc4ad365bab9edf9efc27ff4e
