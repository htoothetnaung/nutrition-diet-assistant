from dotenv import load_dotenv
import os

load_dotenv()  
print("Using GEMINI key:", os.getenv("GOOGLE_API_KEY"))
