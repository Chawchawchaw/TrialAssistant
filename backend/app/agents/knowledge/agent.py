"""Knowledge Agent — RAG-based detection knowledge Q&A."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.knowledge.prompt import KNOWLEDGE_HUMAN_PROMPT, KNOWLEDGE_SYSTEM_PROMPT
from app.agents.knowledge.tools import TOOL_REGISTRY
from app.core.agent_state import AgentState
from app.core.llm import get_llm
from app.services.rag_service import format_rag_context

logger = logging.getLogger(__name__)


def knowledge_agent_node(state: AgentState) -> dict:
    """Knowledge Q&A node.

    Full RAG pipeline:
    1. Understand user question
    2. Retrieve relevant documents from Milvus
    3. Generate answer grounded in retrieved context

    Args:
        state: Current AgentState.

    Returns:
        Updated state with knowledge results.
    """
    logger.info("Knowledge Agent: processing question")

    last_message = state["messages"][-1].content if state["messages"] else ""

    # Step 1: Retrieve relevant documents
    search_results = TOOL_REGISTRY["search_knowledge"]["func"](query=last_message, top_k=5)

    if not search_results:
        return {
            "tool_results": {"knowledge_results": []},
            "final_answer": (
                "抱歉，我在知识库中未找到相关信息。"
                "请尝试换个问法，或联系人工客服获取帮助。"
            ),
        }

    # Step 2: Format context
    context = format_rag_context(search_results)

    # Step 3: Generate answer with LLM
    llm = get_llm()
    messages = [
        SystemMessage(content=KNOWLEDGE_SYSTEM_PROMPT),
        HumanMessage(
            content=KNOWLEDGE_HUMAN_PROMPT.format(
                question=last_message,
                context=context,
            )
        ),
    ]

    response = llm.invoke(messages)
    answer = response.content.strip()

    # Step 4: Add source references
    sources = [
        {
            "title": r["title"],
            "category": r["category"],
            "score": r["score"],
        }
        for r in search_results[:3]  # Top 3 sources
    ]

    # Format sources as footnote
    if sources:
        source_lines = ["\n\n📚 **参考来源**："]
        for i, s in enumerate(sources, 1):
            source_lines.append(f"{i}. {s['title']}（{s['category']}）")
        answer += "\n".join(source_lines)

    tool_results = {
        "knowledge_results": search_results,
        "sources": sources,
    }

    logger.info(f"Knowledge Agent: answer generated from {len(search_results)} sources")

    return {
        "tool_results": tool_results,
        "final_answer": answer,
    }
