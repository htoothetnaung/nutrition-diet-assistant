from typing import Any, Callable, Dict

# Retrieval tool factory expects a LangChain RetrievalQA chain-like object
# and returns a callable tool: retrieval(query:str) -> Dict

def make_retrieval_tool(qa_chain: Any) -> Callable[..., Dict[str, Any]]:
    def retrieval(query: str) -> Dict[str, Any]:
        try:
            # Prefer .invoke; fall back to ._call for older chains
            if hasattr(qa_chain, "invoke"):
                result = qa_chain.invoke({"query": query})
            else:
                result = qa_chain._call({"query": query})
            text = ""
            sources = []
            if isinstance(result, dict):
                text = result.get("result") or result.get("answer") or ""
                sources = result.get("source_documents") or []
            else:
                text = str(result)
            return {
                "text": text,
                "source_count": len(sources),
            }
        except Exception as e:
            return {"text": f"Retrieval error: {e}", "source_count": 0}
    return retrieval


def make_macro_calculator_tool(
    extract_ingredients_fn: Callable[[str], Dict[str, Any]],
    compute_nutrition_fn: Callable[[Any], Dict[str, Any]],
) -> Callable[..., Dict[str, Any]]:
    def macro_calculator(query: str) -> Dict[str, Any]:
        # Extract ingredients from the natural-language query
        ext = extract_ingredients_fn(query) or {}
        items = ext.get("items") or []
        if not items:
            # If LLM extraction unavailable, try a trivial fallback: treat whole query as one serving
            items = [{"name": query.strip()[:32], "quantity": 1, "unit": "serving"}] if query.strip() else []
        if not items:
            return {"totals": {}, "details": [], "note": "no items"}
        nutrition = compute_nutrition_fn(items) or {}
        return nutrition
    return macro_calculator
