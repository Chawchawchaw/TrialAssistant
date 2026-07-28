"""Experiment Status Agent tools.

Wraps MCP server functions as callable tools for the agent.
"""

import logging
from typing import Any

from app.mcp.server import list_orders_by_customer, query_experiment_status

logger = logging.getLogger(__name__)


def call_query_experiment_status(order_no: str) -> dict[str, Any]:
    """Query experiment/test status from LIMS.

    Args:
        order_no: The order number to query.

    Returns:
        Experiment status data.
    """
    logger.info(f"Tool: query_experiment_status(order_no={order_no})")
    return query_experiment_status(order_no)


def call_list_orders_by_customer(customer_name: str) -> list[dict[str, Any]]:
    """List all orders for a customer.

    Args:
        customer_name: Customer name to search for.

    Returns:
        List of customer orders.
    """
    logger.info(f"Tool: list_orders_by_customer(customer_name={customer_name})")
    return list_orders_by_customer(customer_name)


# Tool registry for this agent
TOOL_REGISTRY = {
    "query_experiment_status": {
        "func": call_query_experiment_status,
        "description": "根据订单号查询试验状态",
        "parameters": {"order_no": "订单号，如 TA2024070001"},
    },
    "list_orders_by_customer": {
        "func": call_list_orders_by_customer,
        "description": "根据客户名称查询该客户的所有订单",
        "parameters": {"customer_name": "客户名称"},
    },
}
