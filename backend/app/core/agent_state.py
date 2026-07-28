"""Unified Agent State for LangGraph workflow."""

from typing import Optional

from langgraph.graph import add_messages
from typing_extensions import Annotated, TypedDict


class AgentState(TypedDict):
    """Unified state for all agents in the LangGraph workflow.

    This state flows through the entire LangGraph StateGraph pipeline.
    Each agent reads from and writes to these fields as it executes.
    """

    # Core conversation fields
    messages: Annotated[list, add_messages]
    user_id: str
    conversation_id: str

    # Intent routing fields
    intent: Optional[str]
    confidence: Optional[float]
    current_agent: Optional[str]

    # Business data fields
    tool_results: dict
    need_human: bool
    final_answer: Optional[str]
