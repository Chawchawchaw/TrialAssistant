"""Reservation Agent — handles lab resource queries and bookings."""

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.reservation.prompt import RESERVATION_HUMAN_PROMPT, RESERVATION_SYSTEM_PROMPT
from app.agents.reservation.tools import TOOL_REGISTRY
from app.core.agent_state import AgentState
from app.core.llm import get_llm

logger = logging.getLogger(__name__)


def reservation_agent_node(state: AgentState) -> dict:
    """Lab reservation node.

    Handles lab resource queries and booking creation.
    Booking creation requires human confirmation (HITL).

    Args:
        state: Current AgentState.

    Returns:
        Updated state with reservation results.
    """
    logger.info("Reservation Agent: processing request")

    last_message = state["messages"][-1].content if state["messages"] else ""

    # Determine intent: query labs or create booking
    action = _determine_action(last_message)

    if action == "create_booking":
        result = _handle_create_booking(last_message, state)
    else:
        result = _handle_query_labs(last_message)

    return result


def _determine_action(message: str) -> str:
    """Determine whether user wants to query labs or create a booking."""
    booking_keywords = ["预约", "预订", "订", "book", "reserve", "预定了"]
    query_keywords = ["查询", "查看", "有什么实验室", "有哪些", "可用", "空闲", "资源"]

    msg_lower = message.lower()

    for kw in booking_keywords:
        if kw in msg_lower:
            return "create_booking"

    for kw in query_keywords:
        if kw in msg_lower:
            return "query_labs"

    return "query_labs"


def _handle_query_labs(message: str) -> dict:
    """Handle lab resource query."""
    result = TOOL_REGISTRY["query_lab_resources"]["func"]()

    tool_results = {"lab_resources": result}
    final_answer = _format_lab_response(result)

    return {
        "tool_results": tool_results,
        "final_answer": final_answer,
    }


def _handle_create_booking(message: str, state: AgentState) -> dict:
    """Handle booking creation with LLM extracting booking details."""
    llm = get_llm()

    # First, get lab list for reference
    labs = TOOL_REGISTRY["query_lab_resources"]["func"]()

    system_msg = f"""从用户消息中提取预约信息。可预约的实验室如下：
{json.dumps([{"lab_id": l["lab_id"], "name": l["name"]} for l in labs], ensure_ascii=False)}

请按 JSON 格式输出：
{{"lab_id": "实验室ID", "date": "YYYY-MM-DD", "time_slot": "时间段", "purpose": "用途说明"}}

如果缺少必要信息，对应字段设为 null。
只输出 JSON，不要其他文字。
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_msg),
            HumanMessage(content=message),
        ])

        booking_info = json.loads(response.content.strip())
        lab_id = booking_info.get("lab_id")

        # Check if we have all required info
        missing = []
        if not lab_id:
            missing.append("实验室")
        if not booking_info.get("date"):
            missing.append("预约日期")
        if not booking_info.get("time_slot"):
            missing.append("时间段")
        if not booking_info.get("purpose"):
            missing.append("用途说明")

        if missing:
            lab_info = _format_lab_response(labs)
            return {
                "tool_results": {"lab_resources": labs},
                "final_answer": f"请补充以下信息：{'、'.join(missing)}\n\n{lab_info}",
            }

        # Create booking
        user_name = state.get("user_id", "未知用户")
        result = TOOL_REGISTRY["create_booking"]["func"](
            lab_id=lab_id,
            user_name=user_name,
            date=booking_info["date"],
            time_slot=booking_info["time_slot"],
            purpose=booking_info["purpose"],
        )

        tool_results = {"booking_result": result}
        final_answer = result.get("message", "预约已提交。")

        if result.get("success"):
            final_answer += "\n\n⚠️ **注意**：该预约需要人工确认后方可生效，请等待工作人员联系您确认。"

        return {
            "tool_results": tool_results,
            "final_answer": final_answer,
            "need_human": True,
        }

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Reservation Agent: failed to parse booking info: {e}")
        lab_info = _format_lab_response(labs)
        return {
            "tool_results": {"lab_resources": labs},
            "final_answer": f"未能识别预约信息，请按以下格式提供：\n\n"
                            f"我想预约[实验室名称]，日期[YYYY-MM-DD]，时间段[如09:00-12:00]，"
                            f"用途是[用途说明]。\n\n{lab_info}",
        }


def _format_lab_response(labs: list[dict]) -> str:
    """Format lab resources into readable response."""
    if not labs:
        return "暂无可用的实验室资源。"

    lines = ["🏪 **可用实验室资源**\n"]

    for lab in labs:
        lines.append(f"**{lab['name']}**（{lab.get('location', '-')}）")
        lines.append(f"  🆔 编号：{lab['lab_id']}")

        # Equipment
        equipments = lab.get("equipment", [])
        if equipments:
            for eq in equipments:
                status_icon = "✅" if eq["status"] == "AVAILABLE" else "🔴" if eq["status"] == "IN_USE" else "🔧"
                lines.append(f"  {status_icon} {eq['name']}（{eq.get('model', '')}）- {eq['status']}")

        # Available slots
        slots = lab.get("available_slots", [])
        if slots:
            lines.append(f"  📅 可预约时段：")
            for slot_group in slots:
                times = "、".join(slot_group.get("slots", []))
                lines.append(f"    {slot_group['date']}: {times}")

        lines.append("")

    if not lines:
        return "暂无可用的实验室资源。"

    return "\n".join(lines)
