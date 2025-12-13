from typing import Optional
import os

from langchain_google_genai import ChatGoogleGenerativeAI
try:
    # Available via langchain-openai package
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore


def get_gemini_llm(model_name: str = "gemini-2.0-flash", api_key: Optional[str] = None):
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set.")
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=key,
        max_output_tokens=500,
        temperature=0.1,
        top_p=0.95,
        top_k=40,
    )
    return llm


def get_openrouter_llm(model_name: str = "openai/gpt-4o-mini", api_key: Optional[str] = None):
    """
    Returns an OpenRouter-backed Chat LLM using OpenAI-compatible API via LangChain's ChatOpenAI.
    Requires langchain-openai installed and OPENROUTER_API_KEY set.
    """
    if ChatOpenAI is None:
        raise ImportError("langchain-openai is required for OpenRouter. Please add 'langchain-openai' to requirements.")
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is not set.")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    # Note: Use model ids as listed by OpenRouter, e.g. 'openai/gpt-4o-mini', 'anthropic/claude-3.5-haiku', 'qwen/qwen2.5-7b-instruct'
    llm = ChatOpenAI(
        model=model_name,
        api_key=key,
        base_url=base_url,
        temperature=0.1,
        max_tokens=500,
    )
    return llm


def get_llm(model_name: Optional[str] = None, api_key: Optional[str] = None):
    """
    Provider-agnostic LLM getter.
    Selects provider by env LLM_PROVIDER in {"gemini", "openrouter"}. Defaults to gemini.
    For model defaults, uses:
      - gemini: env LLM_MODEL or config default "gemini-2.0-flash"
      - openrouter: env LLM_MODEL or default "openai/gpt-4o-mini"
    """
    provider = (os.getenv("LLM_PROVIDER", "gemini") or "gemini").lower()
    if provider == "openrouter":
        default_model = "openai/gpt-4o-mini"
        return get_openrouter_llm(model_name or os.getenv("LLM_MODEL", default_model), api_key)
    # default: gemini
    default_model = "gemini-2.0-flash"
    return get_gemini_llm(model_name or os.getenv("LLM_MODEL", default_model), api_key)
