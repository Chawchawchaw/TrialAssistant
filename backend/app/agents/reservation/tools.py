"""Reservation Agent tools.

Wraps MCP lab resource functions as callable tools.
"""

import logging
from typing import Any

from app.mcp.server import create_booking, query_lab_resources

logger = logging.getLogger(__name__)


def call_query_lab_resources() -> list[dict[str, Any]]:
    """Query available laboratory resources.

    Returns:
        List of labs with equipment and slots.
    """
    logger.info("Tool: query_lab_resources()")
    return query_lab_resources()


def call_create_booking(
    lab_id: str,
    user_name: str,
    date: str,
    time_slot: str,
    purpose: str,
) -> dict[str, Any]:
    """Create a lab reservation.

    This is a high-risk operation requiring human confirmation.

    Args:
        lab_id: Laboratory ID.
        user_name: Person making the booking.
        date: Booking date (YYYY-MM-DD).
        time_slot: Time slot string.
        purpose: Purpose description.

    Returns:
        Booking result.
    """
    logger.info(f"Tool: create_booking(lab_id={lab_id}, date={date}, slot={time_slot})")
    return create_booking(lab_id, user_name, date, time_slot, purpose)


TOOL_REGISTRY = {
    "query_lab_resources": {
        "func": call_query_lab_resources,
        "description": "查询所有实验室资源，包括设备状态和可预约时间段",
        "parameters": {},
    },
    "create_booking": {
        "func": call_create_booking,
        "description": "创建实验室预约（高风险操作，需人工确认）",
        "parameters": {
            "lab_id": "实验室ID",
            "user_name": "预约人名称",
            "date": "预约日期，格式 YYYY-MM-DD",
            "time_slot": "时间段，如 09:00-12:00",
            "purpose": "预约用途说明",
        },
    },
}
