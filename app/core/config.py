from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")

<<<<<<< HEAD
settings=Settings()
=======
settings=Settings
>>>>>>> 4a480110f464f2dfc4ad365bab9edf9efc27ff4e
