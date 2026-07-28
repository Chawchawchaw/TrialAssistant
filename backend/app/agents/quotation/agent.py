"""Quotation Agent — generates price quotes based on test requirements."""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.quotation.prompt import QUOTATION_HUMAN_PROMPT, QUOTATION_SYSTEM_PROMPT
from app.agents.quotation.tools import TOOL_REGISTRY
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def quotation_agent_node(state: AgentState) -> dict:
    """Quotation generation node.

    Extracts test items from user request, queries prices via MCP tools,
    calculates total via dedicated calculate tool, and returns formatted quote.

    ⚠️ All price calculations MUST go through calculate_total_price tool.

    Args:
        state: Current AgentState.

    Returns:
        Updated state with quotation results.
    """
    logger.info("Quotation Agent: processing request")

    last_message = state["messages"][-1].content if state["messages"] else ""

    # Step 1: Extract test items from user message using LLM
    test_items = _extract_test_items(last_message)

    if not test_items:
        return {
            "tool_results": {"error": "无法识别检测项目"},
            "final_answer": "请问您需要查询哪些检测项目的报价？例如：高温测试、振动测试等。",
        }

    logger.info(f"Quotation Agent: identified test items: {test_items}")

    # Step 2: Search for standard names if items seem non-standard
    standardized_items = []
    for item in test_items:
        matched = call_search_test_items(item)
        if matched:
            standardized_items.append(matched[0]["name"])
        else:
            standardized_items.append(item)

    logger.info(f"Quotation Agent: standardized items: {standardized_items}")

    # Step 3: Query prices
    price_result = TOOL_REGISTRY["query_test_price"]["func"](standardized_items)
    found_items = price_result.get("items", [])
    not_found = price_result.get("not_found", [])

    if not found_items:
        return {
            "tool_results": {"price_result": price_result},
            "final_answer": f"抱歉，未找到以下检测项目的价格信息：{'、'.join(not_found)}。请确认检测项目名称是否正确。",
        }

    # Step 4: Calculate total price using dedicated tool (NOT LLM)
    prices = [item["price"] for item in found_items]
    calc_result = TOOL_REGISTRY["calculate_total_price"]["func"](prices)

    logger.info(f"Quotation Agent: prices={prices}, total={calc_result['total_price']}")

    # Step 5: Format result
    tool_results = {
        "items": found_items,
        "total_price": calc_result["total_price"],
        "not_found": not_found,
    }

    final_answer = _format_quotation(tool_results)

    return {
        "tool_results": tool_results,
        "final_answer": final_answer,
    }


def call_search_test_items(keyword: str) -> list[dict[str, Any]]:
    """Search test items by keyword."""
    return TOOL_REGISTRY["search_test_items"]["func"](keyword)


def _extract_test_items(message: str) -> list[str]:
    """Use LLM to extract test item names from user message."""
    llm = get_llm()

    system_msg = """你是一个检测项目识别专家。从用户的消息中提取需要报价的检测项目名称。

规则：
1. 提取所有提到的检测项目名称
2. 如果用户提到产品类型（如"电池"、"手机"），推断可能需要的相关检测项目
3. 返回 JSON 格式：{"test_items": ["项目1", "项目2"]}
4. 如果用户没有提到任何检测项目，返回空列表
5. 只输出 JSON，不要其他文字
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=f"用户消息：{message}"),
        ])

        result = json.loads(response.content.strip())
        items = result.get("test_items", [])
        return [item.strip() for item in items if item.strip()]

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Quotation Agent: failed to extract test items: {e}")
        return []


def _format_quotation(result: dict) -> str:
    """Format quotation result into a readable response."""
    items = result.get("items", [])
    total = result.get("total_price", 0)
    not_found = result.get("not_found", [])

    if not items:
        return "暂未找到相关检测项目的报价信息。"

    lines = [
        "📊 **检测报价单**\n",
        f"{'检测项目':<20} {'标准':<20} {'价格(元)':<10} {'周期':<12}",
        f"{'─'*20} {'─'*20} {'─'*10} {'─'*12}",
    ]

    for item in items:
        lines.append(
            f"{item['name']:<20} {item.get('standard', '-'):<20} "
            f"{item['price']:<8,} {item.get('duration', '-'):<12}"
        )

    lines.append(f"\n{'─'*62}")
    lines.append(f"{'总价':<40} ¥{total:,}")

    if not_found:
        lines.append(f"\n⚠️ 以下项目未找到价格信息，已排除：{'、'.join(not_found)}")

    lines.append("\n💡 以上报价仅供参考，实际价格以正式报价单为准。")

    return "\n".join(lines)
