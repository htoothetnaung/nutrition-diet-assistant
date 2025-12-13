from typing import Any, Dict, List
import streamlit as st

def render_agent_trace(trace: List[Dict[str, Any]]) -> None:
    if not trace:
        return
    with st.expander("Agent Trace", expanded=False):
        for entry in trace:
            et = entry.get("type")
            if et == "plan":
                st.write({"plan_steps": entry.get("steps")})
            elif et == "action":
                st.write({
                    "action_tool": entry.get("tool"),
                    "meta": entry.get("result_meta"),
                })
            elif et == "verification":
                st.write({"verification": entry})
            elif et == "error":
                st.write({"error": entry.get("error")})
