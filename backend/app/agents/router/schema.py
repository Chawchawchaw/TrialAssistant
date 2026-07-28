"""Router Agent schema definitions."""

from typing import Optional

from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    """The result of intent classification."""

    intent: str = Field(description="The identified intent category")
    confidence: float = Field(description="Confidence score of the intent classification", ge=0, le=1)
    reasoning: Optional[str] = Field(default=None, description="Reasoning behind the intent classification")
