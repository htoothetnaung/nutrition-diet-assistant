from typing import Any, Dict, List

SAFEGUARD_TOPICS = [
    "diagnose", "prescribe", "medication", "drug", "disease", "treat", "cure",
]

def basic_verifier(answer: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Very simple verifier:
    - Flags medical-advice-like content
    - If retrieval tool produced 0 sources, add a low-confidence note
    Returns: {ok: bool, note: str, fallback?: str}
    """
    ans = (answer or "").lower()
    note_parts = []
    ok = True

    # Check for unsafe medical claims
    if any(tok in ans for tok in SAFEGUARD_TOPICS):
        ok = False
        note_parts.append("Medical-content detected; redirect to professional advice.")
        fallback = (
            "I can provide general nutrition information, but I can’t offer medical advice. "
            "Please consult a qualified healthcare professional for diagnosis or treatment."
        )
        return {"ok": ok, "note": "; ".join(note_parts), "fallback": fallback}

    # If last step was retrieval and had no sources, mark low confidence
    if results:
        last = results[-1]
        if last.get("tool") == "retrieval":
            meta_sources = last.get("result", {}).get("source_count", 0)
            if not meta_sources:
                note_parts.append("No citations; low confidence.")

    return {"ok": ok, "note": "; ".join(note_parts)}
