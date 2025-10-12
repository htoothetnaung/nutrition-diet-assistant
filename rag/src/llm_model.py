from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_gemini_llm(model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set.")
    # Note: Avoid passing unsupported retry/backoff kwargs via bind/constructor to prevent runtime errors.
    # The underlying client manages its own retry policy. Use a lighter model to reduce quota pressure.
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=key,
        max_output_tokens=500,  # Increased to allow more detailed responses
        temperature=0.1,  # Reduced further for more factual responses
        top_p=0.95,
        top_k=40,
    )
    return llm
