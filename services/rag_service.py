import os
import sys
from typing import Any, Dict

# Ensure local RAG package is importable when called outside app.py
RAG_SRC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag", "src")
if RAG_SRC not in sys.path:
    sys.path.insert(0, RAG_SRC)

try:
    from config_loader import load_config
    from embedding_model import get_embeddings
    from llm_model import get_llm
    from vector_store import get_vector_store
    from rag_chain import build_rag_chain
except Exception:
    # These imports will be attempted again inside init_rag and errors returned
    load_config = None  # type: ignore


def init_rag(cfg_path: str) -> Dict[str, Any]:
    """
    Initialize RAG components from a config path.
    Returns dict: {"qa_chain", "llm", "retriever"}
    Raises exceptions on failures so caller can render UI error.
    """
    # Import inside to surface errors to caller in environments where top-level failed
    from config_loader import load_config as _load_config
    from embedding_model import get_embeddings as _get_emb
    from llm_model import get_llm as _get_llm
    from vector_store import get_vector_store as _get_vs
    from rag_chain import build_rag_chain as _build

    cfg = _load_config(cfg_path)
    # Model names in config are kept under 'gemini' key for backward compatibility.
    emb = _get_emb(model_name=cfg["gemini"]["embedding_model"])
    vs_cfg = cfg["data_ingestion"]["vector_store"]
    vs = _get_vs(config=vs_cfg, embedding_function=emb)
    retriever = vs.as_retriever(
        search_kwargs={
            "k": cfg["rag"]["retrieval_k"],
            "score_threshold": 0.5,
        }
    )
    llm = _get_llm(model_name=cfg["gemini"]["llm_model"])
    qa_chain = _build(
        llm=llm,
        retriever=retriever,
        chain_type=cfg["rag"]["chain_type"],
        return_source_documents=True,
    )
    return {"qa_chain": qa_chain, "llm": llm, "retriever": retriever}
