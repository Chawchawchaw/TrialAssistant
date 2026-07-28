"""Summary Agent — integrates agent outputs into a natural language response."""

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.summary.prompt import SUMMARY_HUMAN_PROMPT, SUMMARY_SYSTEM_PROMPT
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def summary_agent_node(state: AgentState) -> dict:
    """Summary node that integrates results into a final response.

    If the business agent already produced a final_answer, use it directly.
    Otherwise, use LLM to generate a summary from tool_results.

    Args:
        state: Current AgentState with tool_results from the business agent.

    Returns:
        Updated state with the final_answer.
    """
    logger.info("Summary Agent: generating final response")

    # If agent already generated a final answer, pass through
    if state.get("final_answer"):
        logger.info("Summary Agent: using existing final_answer")
        return {"final_answer": state["final_answer"]}

    # If no tool results, generate a fallback response
    if not state.get("tool_results"):
        logger.info("Summary Agent: no tool results, generating default response")
        return {
            "final_answer": "抱歉，我暂时无法处理您的请求，请稍后再试。"
        }

    user_message = state["messages"][-1].content if state["messages"] else ""
    agent_result = json.dumps(state["tool_results"], ensure_ascii=False, indent=2)

    llm = get_llm()
    messages = [
        SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
        HumanMessage(content=SUMMARY_HUMAN_PROMPT.format(
            agent_result=agent_result,
            user_message=user_message,
        )),
    ]

    response = llm.invoke(messages)
    reply = response.content.strip()

    logger.info("Summary Agent: final response generated")

    return {"final_answer": reply}
