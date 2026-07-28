"""Summary Agent schema definitions."""

from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """The final summarized response to the user."""

    answer: str = Field(description="The final answer to present to the user")
