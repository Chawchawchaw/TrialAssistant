"""MCP Server — Mock Enterprise System Integration Layer.

This module simulates the MCP (Model Context Protocol) server that connects
Agents to enterprise systems (LIMS, CRM, etc.). Currently provides mock
implementations for all business capabilities.

In production, this would connect to real LIMS/CRM systems via API.
"""

import logging
from typing import Any

from app.mcp.mock_data import (
    MOCK_LABS,
    MOCK_ORDERS,
    MOCK_REPORTS,
    MOCK_RESERVATIONS,
    MOCK_TEST_PRICES,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Experiment Status Tools
# ═══════════════════════════════════════════════════════════════════

def query_experiment_status(order_no: str) -> dict[str, Any]:
    """Query experiment/test status from LIMS.

    Args:
        order_no: The order number to query.

    Returns:
        Experiment status information including current stage, progress, etc.
    """
    logger.info(f"MCP: query_experiment_status(order_no={order_no})")

    for order in MOCK_ORDERS:
        if order["order_no"] == order_no:
            return {
                "found": True,
                "order_no": order["order_no"],
                "customer_name": order["customer_name"],
                "product_name": order["product_name"],
                "status": order["status"],
                "current_stage": order["current_stage"],
                "progress": order["progress"],
                "expected_finish": order["expected_finish"],
                "stages": order["stages"],
            }

    return {
        "found": False,
        "order_no": order_no,
        "error": f"未找到订单 {order_no}，请确认订单号是否正确。",
    }


def list_orders_by_customer(customer_name: str) -> list[dict[str, Any]]:
    """List all orders for a given customer.

    Args:
        customer_name: Customer name to search for.

    Returns:
        List of orders belonging to the customer.
    """
    logger.info(f"MCP: list_orders_by_customer(customer_name={customer_name})")

    results = []
    for order in MOCK_ORDERS:
        if customer_name in order["customer_name"]:
            results.append({
                "order_no": order["order_no"],
                "product_name": order["product_name"],
                "status": order["status"],
                "progress": order["progress"],
            })

    return results if results else [{"error": f"未找到客户 '{customer_name}' 的订单。"}]


# ═══════════════════════════════════════════════════════════════════
# Price & Quotation Tools
# ═══════════════════════════════════════════════════════════════════

def query_test_price(test_items: list[str]) -> dict[str, Any]:
    """Query prices for specified test items from LIMS.

    Args:
        test_items: List of test item names to query prices for.

    Returns:
        Dictionary with items list (name, standard, price, duration) and
        any items not found.
    """
    logger.info(f"MCP: query_test_price(test_items={test_items})")

    found_items = []
    not_found = []

    price_lookup = {item["test_name"]: item for item in MOCK_TEST_PRICES}

    for name in test_items:
        if name in price_lookup:
            item = price_lookup[name]
            found_items.append({
                "name": item["test_name"],
                "standard": item["standard"],
                "price": item["price"],
                "duration": item["duration"],
            })
        else:
            not_found.append(name)

    return {
        "items": found_items,
        "not_found": not_found,
    }


def calculate_total_price(prices: list[int]) -> dict[str, Any]:
    """Calculate total quotation amount.

    This is a dedicated calculation tool — LLM must NOT compute amounts directly.

    Args:
        prices: List of individual item prices.

    Returns:
        Total price and item count.
    """
    logger.info(f"MCP: calculate_total_price(prices={prices})")

    total = sum(prices)
    return {
        "total_price": total,
        "item_count": len(prices),
        "currency": "CNY",
    }


def search_test_items(keyword: str) -> list[dict[str, Any]]:
    """Search for test items matching a keyword.

    Args:
        keyword: Search keyword to match against test names and standards.

    Returns:
        List of matching test items.
    """
    logger.info(f"MCP: search_test_items(keyword={keyword})")

    results = []
    keyword_lower = keyword.lower()

    for item in MOCK_TEST_PRICES:
        if keyword_lower in item["test_name"].lower() or keyword_lower in item["standard"].lower():
            results.append({
                "name": item["test_name"],
                "standard": item["standard"],
                "price": item["price"],
                "duration": item["duration"],
            })

    return results


# ═══════════════════════════════════════════════════════════════════
# Report Tools
# ═══════════════════════════════════════════════════════════════════

def query_report(order_no: str) -> dict[str, Any]:
    """Query report status and details.

    Args:
        order_no: The order number to check report for.

    Returns:
        Report information including status and download URL if available.
    """
    logger.info(f"MCP: query_report(order_no={order_no})")

    for report in MOCK_REPORTS:
        if report["order_no"] == order_no:
            return {
                "found": True,
                "order_no": report["order_no"],
                "report_id": report["report_id"],
                "status": report["status"],
                "file_url": report["file_url"],
                "created_at": report["created_at"],
                "summary": report["summary"],
            }

    return {
        "found": False,
        "order_no": order_no,
        "error": f"未找到订单 {order_no} 的报告信息。",
    }


def download_report(report_id: str) -> dict[str, Any]:
    """Get download URL for a report.

    Args:
        report_id: The report ID to download.

    Returns:
        Download URL for the report.
    """
    logger.info(f"MCP: download_report(report_id={report_id})")

    for report in MOCK_REPORTS:
        if report["report_id"] == report_id:
            if report["file_url"]:
                return {
                    "available": True,
                    "report_id": report_id,
                    "file_url": report["file_url"],
                }
            return {
                "available": False,
                "report_id": report_id,
                "error": "报告尚未生成，暂无下载链接。",
            }

    return {
        "available": False,
        "report_id": report_id,
        "error": f"未找到报告 {report_id}。",
    }


# ═══════════════════════════════════════════════════════════════════
# Lab Resource Tools
# ═══════════════════════════════════════════════════════════════════

def query_lab_resources() -> list[dict[str, Any]]:
    """Query available laboratory resources.

    Returns:
        List of labs with their equipment and available time slots.
    """
    logger.info("MCP: query_lab_resources()")

    return [
        {
            "lab_id": lab["lab_id"],
            "name": lab["name"],
            "location": lab["location"],
            "equipment": lab["equipment"],
            "available_slots": lab["available_slots"],
        }
        for lab in MOCK_LABS
    ]


def create_booking(
    lab_id: str,
    user_name: str,
    date: str,
    time_slot: str,
    purpose: str,
) -> dict[str, Any]:
    """Create a lab reservation/booking.

    This is a high-risk operation that requires human confirmation.

    Args:
        lab_id: Laboratory ID.
        user_name: Name of the person making the booking.
        date: Booking date (YYYY-MM-DD).
        time_slot: Time slot string (e.g., "09:00-12:00").
        purpose: Purpose of the booking.

    Returns:
        Booking confirmation or error.
    """
    logger.info(f"MCP: create_booking(lab_id={lab_id}, date={date}, slot={time_slot})")

    # Validate lab exists
    lab = None
    for l in MOCK_LABS:
        if l["lab_id"] == lab_id:
            lab = l
            break

    if not lab:
        return {
            "success": False,
            "error": f"未找到实验室 {lab_id}。",
        }

    # Validate slot availability
    slot_available = False
    for slot_group in lab["available_slots"]:
        if slot_group["date"] == date and time_slot in slot_group["slots"]:
            slot_available = True
            break

    if not slot_available:
        return {
            "success": False,
            "error": f"实验室 {lab['name']} 在 {date} {time_slot} 时段不可用。",
        }

    # Create booking
    booking_id = f"BK-{len(MOCK_RESERVATIONS) + 1:04d}"
    booking = {
        "booking_id": booking_id,
        "lab_id": lab_id,
        "lab_name": lab["name"],
        "user_name": user_name,
        "date": date,
        "time_slot": time_slot,
        "purpose": purpose,
        "status": "PENDING_CONFIRMATION",
    }
    MOCK_RESERVATIONS.append(booking)

    return {
        "success": True,
        "booking_id": booking_id,
        "lab_name": lab["name"],
        "date": date,
        "time_slot": time_slot,
        "status": "PENDING_CONFIRMATION",
        "message": f"预约已提交，需人工确认后方可生效。预约编号：{booking_id}",
    }
