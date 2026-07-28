"""Experiment Status Agent — queries experiment/test execution status."""

import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.experiment_status.prompt import (
    EXPERIMENT_STATUS_HUMAN_PROMPT,
    EXPERIMENT_STATUS_SYSTEM_PROMPT,
)
from app.agents.experiment_status.tools import TOOL_REGISTRY
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def experiment_status_agent_node(state: AgentState) -> dict:
    """Experiment status query node.

    Analyzes user request, extracts order number or customer name,
    calls the appropriate MCP tool, and returns results.

    Args:
        state: Current AgentState.

    Returns:
        Updated state with tool_results and final_answer.
    """
    logger.info("Experiment Status Agent: processing request")

    last_message = state["messages"][-1].content if state["messages"] else ""

    # Step 1: Try to extract order number or customer name from message
    order_no = _extract_order_no(last_message)

    if order_no:
        # Direct order number query
        result = TOOL_REGISTRY["query_experiment_status"]["func"](order_no)
        tool_results = {"status_query": result}
    else:
        # Use LLM to determine what to query
        tool_results = _llm_determine_and_query(last_message)

    # Step 2: Generate final answer
    final_answer = _format_status_response(tool_results, last_message)

    logger.info("Experiment Status Agent: completed")

    return {
        "tool_results": tool_results,
        "final_answer": final_answer,
    }


def _extract_order_no(message: str) -> str | None:
    """Extract order number from message using regex.

    Order format: TA + year + month + 4 digits, e.g. TA2024070001
    """
    match = re.search(r'TA\d{10}', message)
    return match.group(0) if match else None


def _llm_determine_and_query(message: str) -> dict:
    """Use LLM to determine what to query based on the user message."""
    llm = get_llm()

    tool_descriptions = "\n".join(
        f"- {name}: {info['description']} (参数: {json.dumps(info['parameters'], ensure_ascii=False)})"
        for name, info in TOOL_REGISTRY.items()
    )

    system_msg = f"""你是一个工具调度员。根据用户消息，判断调用哪个工具以及传入什么参数。

可用工具：
{tool_descriptions}

请严格按以下 JSON 格式输出（只输出 JSON，不要其他文字）：
{{"tool": "工具名", "parameters": {{"参数名": "参数值"}}}}

如果无法确定，输出：
{{"tool": null, "parameters": {{}}}}
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=message),
        ])

        result = json.loads(response.content.strip())
        tool_name = result.get("tool")
        params = result.get("parameters", {})

        if tool_name and tool_name in TOOL_REGISTRY:
            logger.info(f"Experiment Status Agent: LLM selected tool={tool_name}, params={params}")
            tool_result = TOOL_REGISTRY[tool_name]["func"](**params)
            return {"status_query": tool_result}
        else:
            return {"status_query": {"error": "无法识别查询内容，请提供订单号或客户名称。"}}

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Experiment Status Agent: LLM tool selection failed: {e}")
        return {"status_query": {"error": "无法识别查询内容，请提供订单号或客户名称。"}}


def _format_status_response(tool_results: dict, user_message: str) -> str:
    """Format the query result into a natural language response."""
    status_data = tool_results.get("status_query", {})

    if isinstance(status_data, list):
        # List of orders
        if not status_data:
            return "暂未找到相关订单信息。"

        if "error" in status_data[0]:
            return status_data[0]["error"]

        lines = ["为您找到以下订单：\n"]
        for order in status_data:
            progress_bar = "▓" * (order.get("progress", 0) // 10) + "░" * (10 - order.get("progress", 0) // 10)
            lines.append(
                f"📋 订单 {order['order_no']}\n"
                f"   产品：{order['product_name']}\n"
                f"   状态：{_status_text(order['status'])}\n"
                f"   进度：[{progress_bar}] {order.get('progress', 0)}%\n"
            )
        return "\n".join(lines)

    if "error" in status_data:
        return status_data["error"]

    if not status_data.get("found"):
        return f"未找到订单 {status_data.get('order_no', '')} 的信息。"

    # Single order detail
    order = status_data
    progress_bar = "▓" * (order.get("progress", 0) // 10) + "░" * (10 - order.get("progress", 0) // 10)

    response = [
        f"📋 **订单 {order['order_no']}**\n",
        f"**客户**：{order.get('customer_name', '-')}",
        f"**产品**：{order.get('product_name', '-')}",
        f"**状态**：{_status_text(order['status'])}",
        f"**进度**：[{progress_bar}] {order.get('progress', 0)}%",
    ]

    if order.get("current_stage"):
        response.append(f"**当前阶段**：{order['current_stage']}")
    if order.get("expected_finish"):
        response.append(f"**预计完成**：{order['expected_finish']}")

    # Stages detail
    stages = order.get("stages", [])
    if stages:
        response.append("\n**各阶段详情**：")
        for stage in stages:
            icon = "✅" if stage["status"] == "DONE" else "🔄" if stage["status"] == "IN_PROGRESS" else "⏳"
            response.append(f"  {icon} {stage['name']}")

    return "\n".join(response)


def _status_text(status: str) -> str:
    """Convert status code to Chinese text."""
    status_map = {
        "PENDING": "待处理",
        "SAMPLE_RECEIVED": "样品已接收",
        "TESTING": "测试中",
        "REPORT_REVIEW": "报告审核中",
        "COMPLETED": "已完成",
        "CANCELLED": "已取消",
    }
    return status_map.get(status, status)
