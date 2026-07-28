"""Report Agent — queries test report status and download links."""

import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.report.prompt import REPORT_HUMAN_PROMPT, REPORT_SYSTEM_PROMPT
from app.agents.report.tools import TOOL_REGISTRY
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def report_agent_node(state: AgentState) -> dict:
    """Report query node.

    Analyzes user request, extracts order number or report ID,
    calls the appropriate MCP tool, and returns results.

    Args:
        state: Current AgentState.

    Returns:
        Updated state with report results.
    """
    logger.info("Report Agent: processing request")

    last_message = state["messages"][-1].content if state["messages"] else ""

    # Try to extract order number or report ID
    order_no = _extract_order_no(last_message)
    report_id = _extract_report_id(last_message)

    if report_id:
        result = TOOL_REGISTRY["download_report"]["func"](report_id)
        tool_results = {"report_result": result}
    elif order_no:
        result = TOOL_REGISTRY["query_report"]["func"](order_no)
        tool_results = {"report_result": result}
    else:
        tool_results = {"report_result": {"error": "请提供订单号或报告ID以便查询。"}}

    final_answer = _format_report_response(tool_results)

    return {
        "tool_results": tool_results,
        "final_answer": final_answer,
    }


def _extract_order_no(message: str) -> str | None:
    """Extract order number from message."""
    match = re.search(r'TA\d{10}', message)
    return match.group(0) if match else None


def _extract_report_id(message: str) -> str | None:
    """Extract report ID from message."""
    match = re.search(r'REP-\d{4}-\d{4}', message)
    return match.group(0) if match else None


def _format_report_response(tool_results: dict) -> str:
    """Format report query result into readable response."""
    data = tool_results.get("report_result", {})

    if "error" in data:
        return data["error"]

    if not data.get("found"):
        return data.get("error", "未找到相关报告信息。")

    status = data.get("status", "")
    status_map = {
        "COMPLETED": "✅ 报告已完成",
        "REVIEWING": "🔄 报告审核中",
        "NOT_AVAILABLE": "⏳ 报告暂未生成",
        "PENDING": "⏳ 待处理",
    }

    lines = [
        f"📄 **报告查询结果**\n",
        f"**订单号**：{data.get('order_no', '-')}",
        f"**状态**：{status_map.get(status, status)}",
    ]

    if data.get("report_id"):
        lines.append(f"**报告编号**：{data['report_id']}")

    if data.get("file_url"):
        lines.append(f"**下载链接**：{data['file_url']}")
    elif status == "REVIEWING":
        lines.append("\n报告正在审核中，审核通过后即可下载。")
    elif status == "NOT_AVAILABLE":
        lines.append("\n试验尚未完成，报告暂未生成。")

    if data.get("summary"):
        lines.append(f"\n**摘要**：{data['summary']}")

    return "\n".join(lines)
