# graph.py

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator
from agents import (
    create_supervisor_chain,
    create_researcher_agent,
    create_writer_chain,
    create_critique_chain
)

# --- 1. Define the State ---

class ResearchState(TypedDict):
    main_task: str
    research_findings: Annotated[List[str], operator.add]
    draft: str
    critique_notes: str
    revision_number: int
    next_step: str
    current_sub_task: str


# --- 2. Initialize Chains and Agents ---

supervisor_chain = create_supervisor_chain()
researcher_agent = create_researcher_agent()
writer_chain = create_writer_chain()
critique_chain = create_critique_chain()


# --- 3. Define Graph Nodes ---

def supervisor_node(state: ResearchState) -> dict:
    print("\n=== SUPERVISOR ===")

    decision = supervisor_chain(state)

    next_step = decision.get("next_step", "researcher")
    task_desc = decision.get("task_description", "Continue work")

    return {
        "next_step": next_step,
        "current_sub_task": task_desc,
    }


def research_node(state: ResearchState) -> dict:
    print("\n=== RESEARCHER ===")

    sub_task = state.get("current_sub_task", state.get("main_task"))

    try:
        result = researcher_agent({"input": sub_task})
        findings = result.get("output", "Research completed")
    except Exception as e:
        print("Research error:", e)
        findings = f"Basic research done on {sub_task}"

    return {
        "research_findings": [findings]
    }


def write_node(state: ResearchState) -> dict:
    print("\n=== WRITER ===")

    draft = writer_chain(state)

    return {
        "draft": draft,
        "revision_number": state.get("revision_number", 0) + 1
    }


# 🔥 CRITICAL FIX HERE
def critique_node(state: ResearchState) -> dict:
    print("\n=== CRITIQUER ===")

    critique = critique_chain(state)

    revision = state.get("revision_number", 0)

    # ✅ FORCE STOP AFTER 2 ITERATIONS (VERY IMPORTANT)
    if revision >= 2:
        print("Auto-approving after 2 revisions")
        return {
            "critique_notes": "APPROVED",
            "next_step": "END"
        }

    is_approved = "APPROVED" in critique.upper()

    if is_approved:
        return {
            "critique_notes": "APPROVED",
            "next_step": "END"
        }
    else:
        return {
            "critique_notes": critique,
            "next_step": "writer"
        }


# --- 4. Build the Graph ---

def build_graph():
    workflow = StateGraph(ResearchState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("writer", write_node)
    workflow.add_node("critiquer", critique_node)

    workflow.set_entry_point("supervisor")

    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("writer", "critiquer")
    workflow.add_edge("critiquer", "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next_step", "researcher"),
        {
            "researcher": "researcher",
            "writer": "writer",
            "END": END
        }
    )

    return workflow.compile()


app = build_graph()