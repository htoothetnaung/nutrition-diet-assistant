from typing import Optional
import os

try:
    # Available via langchain-openai package
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore


def get_openrouter_llm(model_name: Optional[str] = None, api_key: Optional[str] = None):
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
    chosen_model = model_name or os.getenv("LLM_MODEL")
    if not chosen_model:
        raise ValueError("OpenRouter model not specified. Set LLM_MODEL or pass model_name explicitly.")
    # Note: Use model ids as listed by OpenRouter, e.g. 'openai/gpt-4o-mini', 'anthropic/claude-3.5-haiku', 'qwen/qwen2.5-7b-instruct'
    llm = ChatOpenAI(
        model=chosen_model,
        api_key=key,
        base_url=base_url,
        temperature=0.1,
        max_tokens=500,
    )
    return llm


def get_llm(model_name: Optional[str] = None, api_key: Optional[str] = None):
    """
    OpenRouter-only LLM getter. Requires OPENROUTER_API_KEY and an explicit model via
    argument or env LLM_MODEL.
    """
    return get_openrouter_llm(model_name or os.getenv("LLM_MODEL"), api_key)
