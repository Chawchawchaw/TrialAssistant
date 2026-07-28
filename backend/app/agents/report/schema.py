"""Report Agent schema definitions."""

from typing import Optional

from pydantic import BaseModel, Field


class ReportQueryResult(BaseModel):
    """Result of a report query."""

    order_no: str = Field(description="Order number")
    report_id: Optional[str] = Field(default=None, description="Report ID if available")
    status: str = Field(description="Report status")
    file_url: Optional[str] = Field(default=None, description="Download URL")
    summary: Optional[str] = Field(default=None, description="Report summary")
