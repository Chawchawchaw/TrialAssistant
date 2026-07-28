"""Knowledge Agent tools.

Wraps RAG service functions as callable tools for the agent.
"""

import logging
from typing import Any

from app.services.rag_service import format_rag_context, search_knowledge

logger = logging.getLogger(__name__)


def call_search_knowledge(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search the knowledge base for relevant documents.

    Args:
        query: The search query.
        top_k: Number of top results to return.

    Returns:
        List of relevant document chunks.
    """
    logger.info(f"Tool: search_knowledge(query='{query[:50]}...', top_k={top_k})")
    return search_knowledge(query, top_k)


def call_format_rag_context(results: list[dict[str, Any]]) -> str:
    """Format search results into context string.

    Args:
        results: Search results from knowledge base.

    Returns:
        Formatted context string.
    """
    return format_rag_context(results)


TOOL_REGISTRY = {
    "search_knowledge": {
        "func": call_search_knowledge,
        "description": "从检测知识库中检索相关文档，输入用户问题返回相关文档片段",
        "parameters": {"query": "用户的查询问题", "top_k": "返回结果数量（默认5）"},
    },
}
