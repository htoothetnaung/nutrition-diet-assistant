from typing import Optional
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
try:
    # Provided by langchain-openai
    from langchain_openai import OpenAIEmbeddings  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAIEmbeddings = None  # type: ignore


def get_gemini_embeddings(model_name: str = "text-embedding-004", api_key: Optional[str] = None):
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set.")
    emb = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=key)
    return emb


def get_openrouter_embeddings(model_name: str = "openai/text-embedding-3-small", api_key: Optional[str] = None):
    """
    Returns OpenRouter-backed embeddings using OpenAI-compatible Embeddings API.
    Recommended low-cost defaults: 'openai/text-embedding-3-small'.
    Alternative: 'voyage/voyage-2' if supported in your account.
    """
    if OpenAIEmbeddings is None:
        raise ImportError("langchain-openai is required for OpenRouter embeddings. Add 'langchain-openai' to requirements.")
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is not set.")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    emb = OpenAIEmbeddings(
        model=model_name,
        api_key=key,
        base_url=base_url,
    )
    return emb


def get_embeddings(model_name: Optional[str] = None, api_key: Optional[str] = None):
    """
    Provider-agnostic embeddings getter.
    Selects provider via env LLM_PROVIDER in {"gemini", "openrouter"}. Defaults to gemini.
    Model defaults:
      - gemini: env EMBEDDING_MODEL or "text-embedding-004"
      - openrouter: env EMBEDDING_MODEL or "openai/text-embedding-3-small"
    """
    provider = (os.getenv("LLM_PROVIDER", "gemini") or "gemini").lower()
    if provider == "openrouter":
        default_model = "openai/text-embedding-3-small"
        return get_openrouter_embeddings(model_name or os.getenv("EMBEDDING_MODEL", default_model), api_key)
    default_model = "text-embedding-004"
    return get_gemini_embeddings(model_name or os.getenv("EMBEDDING_MODEL", default_model), api_key)
