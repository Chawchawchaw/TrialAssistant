"""Report Agent tools.

Wraps MCP report functions as callable tools.
"""

import logging
from typing import Any

from app.mcp.server import download_report, query_report

logger = logging.getLogger(__name__)


def call_query_report(order_no: str) -> dict[str, Any]:
    """Query report status for an order.

    Args:
        order_no: The order number.

    Returns:
        Report status data.
    """
    logger.info(f"Tool: query_report(order_no={order_no})")
    return query_report(order_no)


def call_download_report(report_id: str) -> dict[str, Any]:
    """Get download URL for a report.

    Args:
        report_id: The report ID.

    Returns:
        Download URL data.
    """
    logger.info(f"Tool: download_report(report_id={report_id})")
    return download_report(report_id)


TOOL_REGISTRY = {
    "query_report": {
        "func": call_query_report,
        "description": "根据订单号查询检测报告的状态",
        "parameters": {"order_no": "订单号，如 TA2024070001"},
    },
    "download_report": {
        "func": call_download_report,
        "description": "根据报告ID获取报告下载链接",
        "parameters": {"report_id": "报告ID，如 REP-2024-0123"},
    },
}
