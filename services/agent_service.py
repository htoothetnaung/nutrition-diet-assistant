from typing import Any, Dict

from agents.orchestrator import AgentOrchestrator
from agents.tools import make_retrieval_tool, make_macro_calculator_tool
from agents.verifier import basic_verifier


def build_agent(qa_chain: Any, extract_ingredients_fn, compute_nutrition_fn) -> AgentOrchestrator:
    retrieval = make_retrieval_tool(qa_chain)
    macro_calc = make_macro_calculator_tool(extract_ingredients_fn, compute_nutrition_fn)
    tools = {
        "retrieval": retrieval,
        "macro_calculator": macro_calc,
    }
    return AgentOrchestrator(tools=tools, verifier=basic_verifier)


def run_agent(agent: AgentOrchestrator, query: str) -> Dict[str, Any]:
    return agent.run(query)
