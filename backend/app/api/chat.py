"""Chat API endpoint — the main entry point for user interactions."""

import logging
import uuid

from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.core.agent_state import AgentState
from app.workflows.main_workflow import get_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request payload."""

    user_id: str = Field(description="The unique identifier of the user")
    message: str = Field(description="The user's message text")


class ChatResponse(BaseModel):
    """Chat response payload."""

    answer: str = Field(description="The assistant's reply")


class ErrorResponse(BaseModel):
    """Error response payload."""

    detail: str = Field(description="Error description")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user message through the LangGraph agent workflow.

    Args:
        request: Chat request containing user_id and message.

    Returns:
        ChatResponse with the assistant's answer.
    """
    logger.info(f"Chat API: received message from user {request.user_id}")

    try:
        workflow = get_workflow()

        # Build initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id,
            "conversation_id": str(uuid.uuid4()),
            "intent": None,
            "confidence": None,
            "current_agent": None,
            "tool_results": {},
            "need_human": False,
            "final_answer": None,
        }

        # Run the LangGraph workflow
        result = await workflow.ainvoke(initial_state)

        final_answer = result.get("final_answer") or "抱歉，我暂时无法处理您的请求，请稍后再试。"
        logger.info(f"Chat API: returning response for user {request.user_id}")

        return ChatResponse(answer=final_answer)

    except Exception as e:
        logger.exception(f"Chat API: error processing message: {e}")
        return ChatResponse(answer="系统繁忙，请稍后再试。")
