"""Chitchat Agent — handles non-business conversation."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.chitchat.prompt import CHITCHAT_HUMAN_PROMPT, CHITCHAT_SYSTEM_PROMPT
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def chitchat_agent_node(state: AgentState) -> dict:
    """Chitchat conversation node.

    Handles greetings, thanks, and other non-business interactions.
    Does NOT call any business tools or databases.

    Args:
        state: Current AgentState.

    Returns:
        Updated state with the chitchat reply as final_answer.
    """
    logger.info("Chitchat Agent: processing message")

    last_message = state["messages"][-1].content if state["messages"] else ""

    llm = get_llm()
    messages = [
        SystemMessage(content=CHITCHAT_SYSTEM_PROMPT),
        HumanMessage(content=CHITCHAT_HUMAN_PROMPT.format(message=last_message)),
    ]

    response = llm.invoke(messages)
    reply = response.content.strip()

    logger.info(f"Chitchat Agent: reply generated")

    return {"final_answer": reply, "tool_results": {}}
