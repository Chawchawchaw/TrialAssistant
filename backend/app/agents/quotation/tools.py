"""Quotation Agent tools.

Wraps MCP price and calculation functions as callable tools.
"""

import logging
from typing import Any

from app.mcp.server import calculate_total_price, query_test_price, search_test_items

logger = logging.getLogger(__name__)


def call_query_test_price(test_items: list[str]) -> dict[str, Any]:
    """Query prices for specified test items from LIMS.

    Args:
        test_items: List of test item names.

    Returns:
        Price data for found and not-found items.
    """
    logger.info(f"Tool: query_test_price(items={test_items})")
    return query_test_price(test_items)


def call_calculate_total_price(prices: list[int]) -> dict[str, Any]:
    """Calculate total quotation amount.

    ⚠️ This tool MUST be used for all amount calculations.
    LLM must NOT compute totals directly.

    Args:
        prices: List of individual item prices.

    Returns:
        Total price calculation result.
    """
    logger.info(f"Tool: calculate_total_price(prices={prices})")
    return calculate_total_price(prices)


def call_search_test_items(keyword: str) -> list[dict[str, Any]]:
    """Search for test items matching a keyword.

    Args:
        keyword: Search keyword.

    Returns:
        List of matching test items.
    """
    logger.info(f"Tool: search_test_items(keyword={keyword})")
    return search_test_items(keyword)


# Tool registry for this agent
TOOL_REGISTRY = {
    "query_test_price": {
        "func": call_query_test_price,
        "description": "查询检测项目的价格，输入检测项目名称列表，返回每个项目的价格和标准",
        "parameters": {"test_items": "检测项目名称列表，如 ['高温测试', '振动测试']"},
    },
    "calculate_total_price": {
        "func": call_calculate_total_price,
        "description": "【必用】计算报价总金额，输入价格列表返回总金额。LLM禁止自行计算金额！",
        "parameters": {"prices": "各检测项目的价格列表，如 [3000, 5000]"},
    },
    "search_test_items": {
        "func": call_search_test_items,
        "description": "搜索检测项目，当用户描述的测试项目名称不标准时先用此工具搜索",
        "parameters": {"keyword": "搜索关键词，如 '高温'、'振动'"},
    },
}
