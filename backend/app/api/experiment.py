"""Experiment status API endpoints."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class ExperimentStatusResponse(BaseModel):
    """Experiment status response."""

    order_no: str = Field(description="Order number")
    status: str = Field(description="Current status")
    progress: int = Field(description="Completion percentage", ge=0, le=100)


@router.get("/experiment/status/{order_no}", response_model=ExperimentStatusResponse)
async def get_experiment_status(order_no: str) -> ExperimentStatusResponse:
    """Get the experiment/test status for a given order.

    Note: This is a placeholder. Phase 3 will implement full LIMS integration.

    Args:
        order_no: The order number to query.

    Returns:
        Experiment status information.
    """
    logger.info(f"Experiment API: status query for order {order_no}")

    # Placeholder response — will be replaced with LIMS query in Phase 3
    return ExperimentStatusResponse(
        order_no=order_no,
        status="PENDING",
        progress=0,
    )
