"""Router Agent — intent classification node for the LangGraph workflow."""

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.router.prompt import ROUTER_HUMAN_PROMPT, ROUTER_SYSTEM_PROMPT
from app.agents.router.schema import IntentResult
from app.core.agent_state import AgentState
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_router_llm():
    """Get LLM with low temperature for deterministic intent classification."""
    return ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        temperature=0.01,  # Near-zero for deterministic JSON output
    )


def router_agent_node(state: AgentState) -> dict:
    """Intent classification node.

    Analyzes the user's latest message and determines which agent should handle it.

    Args:
        state: Current AgentState containing messages and conversation context.

    Returns:
        Updated state with intent, confidence, and current_agent fields.
    """
    logger.info("Router Agent: classifying intent")

    # Get the last user message
    last_message = state["messages"][-1].content if state["messages"] else ""

    llm = _get_router_llm()

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=ROUTER_HUMAN_PROMPT.format(message=last_message)),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    logger.info(f"Router Agent: raw response: {content[:100]}")

    # Clean response - remove markdown code blocks if present
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        content = content.rsplit("```", 1)[0]
    content = content.strip()

    try:
        result = IntentResult(**json.loads(content))
        logger.info(f"Router Agent: intent={result.intent}, confidence={result.confidence}")

        return {
            "intent": result.intent,
            "confidence": result.confidence,
            "current_agent": _map_intent_to_agent(result.intent),
        }
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Router Agent: failed to parse: content='{content[:200]}', error={e}")
        # Default to chitchat on failure
        return {
            "intent": "chitchat",
            "confidence": 0.0,
            "current_agent": "chitchat",
        }


def _map_intent_to_agent(intent: str) -> str:
    """Map intent string to agent name."""
    intent_agent_map = {
        "chitchat": "chitchat",
        "knowledge_query": "knowledge",
        "experiment_status": "experiment_status",
        "quotation": "quotation",
        "reservation": "reservation",
        "report_query": "report",
        # Common LLM intent aliases
        "qa": "knowledge",
        "knowledge": "knowledge",
        "status": "experiment_status",
        "price": "quotation",
        "pricing": "quotation",
        "booking": "reservation",
        "report": "report",
    }
    return intent_agent_map.get(intent, "chitchat")
