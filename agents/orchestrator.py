from typing import Any, Dict, List, Optional

class AgentToolError(Exception):
    pass

class AgentOrchestrator:
    """
    Minimal agentic orchestrator using a simple plan-act-verify loop.
    Tools are provided via a registry (dict of callables).
    Produces a final answer and an agent trace for UI display.
    """

    def __init__(self, tools: Dict[str, Any], verifier=None):
        self.tools = tools
        self.verifier = verifier

    def plan(self, query: str) -> List[Dict[str, Any]]:
        """
        Simple planner: choose a single tool based on the query.
        - If nutrition calculation terms present -> macro_calculator
        - Else -> retrieval (RAG)
        """
        q = (query or "").lower()
        steps: List[Dict[str, Any]] = []
        if any(k in q for k in ["calorie", "calories", "protein", "carb", "fat", "fiber"]) and any(k in q for k in ["how much", "how many", "per 100g", "per serving"]):
            steps.append({"tool": "macro_calculator", "input": {"query": query}})
        else:
            steps.append({"tool": "retrieval", "input": {"query": query}})
        return steps

    def act(self, step: Dict[str, Any]) -> Dict[str, Any]:
        name = step.get("tool")
        fn = self.tools.get(name)
        if not fn:
            raise AgentToolError(f"Unknown tool: {name}")
        result = fn(**(step.get("input") or {}))
        return {"tool": name, "result": result}

    def reflect(self, results: List[Dict[str, Any]]) -> str:
        """
        Naive synthesis: if retrieval -> take text; if calculator -> format macro totals.
        """
        if not results:
            return "I couldn't find an answer."
        last = results[-1]
        tool = last.get("tool")
        data = last.get("result")
        if tool == "retrieval":
            return data.get("text") or data.get("answer") or ""
        if tool == "macro_calculator":
            totals = (data or {}).get("totals") or {}
            if totals:
                return (
                    f"Estimated nutrition: Calories {totals.get('calories', 0)} kcal, "
                    f"Protein {totals.get('protein_g', 0)}g, Carbs {totals.get('carbs_g', 0)}g, Fat {totals.get('fat_g', 0)}g."
                )
            return "No nutrition estimate available."
        return str(data)

    def run(self, query: str) -> Dict[str, Any]:
        trace: List[Dict[str, Any]] = []
        steps = self.plan(query)
        trace.append({"type": "plan", "steps": steps})

        results: List[Dict[str, Any]] = []
        for s in steps:
            try:
                out = self.act(s)
                results.append(out)
                trace.append({"type": "action", "tool": out.get("tool"), "result_meta": {k: v for k, v in out.get("result", {}).items() if k in ("k", "source_count", "confidence")}})
            except Exception as e:
                trace.append({"type": "error", "error": str(e)})
                return {"answer": f"Agent error: {e}", "trace": trace}

        answer = self.reflect(results)
        verification = None
        if self.verifier:
            try:
                verification = self.verifier(answer, results)
                trace.append({"type": "verification", "ok": verification.get("ok"), "note": verification.get("note")})
                if not verification.get("ok") and verification.get("fallback"):
                    answer = verification.get("fallback")
            except Exception as e:
                trace.append({"type": "verification_error", "error": str(e)})

        return {"answer": answer, "trace": trace}
