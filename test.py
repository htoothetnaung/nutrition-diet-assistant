from dotenv import load_dotenv
import os

load_dotenv()  # this reads your .env file
print("Using GEMINI key:", os.getenv("GOOGLE_API_KEY"))
