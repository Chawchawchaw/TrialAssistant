"""Experiment Status Agent schema definitions."""

from typing import Optional

from pydantic import BaseModel, Field


class ExperimentStatusResult(BaseModel):
    """Result of an experiment status query."""

    order_no: str = Field(description="Order number")
    status: str = Field(description="Overall order status")
    current_stage: Optional[str] = Field(default=None, description="Current testing stage")
    progress: int = Field(description="Completion percentage", ge=0, le=100)
    expected_finish: Optional[str] = Field(default=None, description="Expected completion date")
