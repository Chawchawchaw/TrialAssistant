"""Main LangGraph workflow for the Trial Assistant.

Flow:
    User -> Assistant Node -> Router Node -> Conditional Edge
    -> Business Agent (chitchat/knowledge/experiment_status/quotation/reservation/report)
    -> Summary Node -> Response
"""

import logging
from typing import Literal

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.chitchat.agent import chitchat_agent_node
from app.agents.experiment_status.agent import experiment_status_agent_node
from app.agents.knowledge.agent import knowledge_agent_node
from app.agents.quotation.agent import quotation_agent_node
from app.agents.report.agent import report_agent_node
from app.agents.reservation.agent import reservation_agent_node
from app.agents.router.agent import router_agent_node
from app.agents.summary.agent import summary_agent_node
from app.core.agent_state import AgentState

logger = logging.getLogger(__name__)


def _create_workflow() -> StateGraph:
    """Create and configure the main LangGraph StateGraph.

    Flow:
        START -> assistant_node -> router_node -> conditional_edge
            -> business_agent -> summary_node -> END

    Returns:
        Configured StateGraph (not yet compiled).
    """
    workflow = StateGraph(AgentState)

    # ── Register nodes ──────────────────────────────────────────────
    workflow.add_node("assistant", assistant_node)
    workflow.add_node("router", router_agent_node)
    workflow.add_node("chitchat", chitchat_agent_node)
    workflow.add_node("summary", summary_agent_node)

    # Business agent nodes
    workflow.add_node("knowledge", knowledge_agent_node)
    workflow.add_node("experiment_status", experiment_status_agent_node)
    workflow.add_node("quotation", quotation_agent_node)
    workflow.add_node("reservation", reservation_agent_node)
    workflow.add_node("report", report_agent_node)

    # ── Define edges ────────────────────────────────────────────────
    workflow.set_entry_point("assistant")

    workflow.add_edge("assistant", "router")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "chitchat": "chitchat",
            "knowledge": "knowledge",
            "experiment_status": "experiment_status",
            "quotation": "quotation",
            "reservation": "reservation",
            "report": "report",
        },
    )

    # All business agents go to summary
    for agent in ["chitchat", "knowledge", "experiment_status", "quotation", "reservation", "report"]:
        workflow.add_edge(agent, "summary")

    workflow.add_edge("summary", END)

    return workflow


def assistant_node(state: AgentState) -> dict:
    """Entry node — initializes the conversation state.

    This node runs first to set up any initial state needed before routing.

    Args:
        state: Initial AgentState.

    Returns:
        Pass-through; no modifications to state.
    """
    logger.info(f"Assistant: starting new conversation for user {state.get('user_id', 'unknown')}")
    return {}


def placeholder_agent_node(state: AgentState) -> dict:
    """Placeholder for business agents not yet implemented.

    In Phase 1, this handles knowledge, experiment_status, quotation,
    reservation, and report intents with a friendly message.

    Args:
        state: Current AgentState.

    Returns:
        State with a placeholder response.
    """
    logger.info(f"Placeholder Agent: handling intent '{state.get('intent', 'unknown')}'")
    return {
        "final_answer": (
            f"抱歉，{state.get('intent', '该功能')}功能正在开发中，"
            "预计在下一阶段上线。请稍后再试！"
        ),
    }


# Intent-to-agent mapping
_INTENT_TO_AGENT: dict[str, str] = {
    "chitchat": "chitchat",
    "knowledge": "knowledge",
    "knowledge_query": "knowledge",
    "experiment_status": "experiment_status",
    "quotation": "quotation",
    "reservation": "reservation",
    "report": "report",
    "report_query": "report",
    # LLM alias fallbacks
    "qa": "knowledge",
    "status": "experiment_status",
    "price": "quotation",
    "pricing": "quotation",
    "booking": "reservation",
}


def route_by_intent(state: AgentState) -> Literal[
    "chitchat", "knowledge", "experiment_status", "quotation", "reservation", "report"
]:
    """Determine which agent to route to based on the identified intent.

    Args:
        state: Current AgentState containing the intent field.

    Returns:
        The name of the target agent node.
    """
    intent = state.get("intent", "chitchat")
    agent = _INTENT_TO_AGENT.get(intent, "chitchat")
    logger.info(f"Router: intent='{intent}' -> agent='{agent}'")
    return agent  # type: ignore[return-value]


# Compiled workflow singleton
_compiled_workflow: CompiledStateGraph | None = None


def get_workflow() -> CompiledStateGraph:
    """Get or create the compiled LangGraph workflow singleton.

    Returns:
        The compiled StateGraph ready for invocation.
    """
    global _compiled_workflow
    if _compiled_workflow is None:
        workflow = _create_workflow()
        _compiled_workflow = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")
    return _compiled_workflow
