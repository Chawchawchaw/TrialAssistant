"""Chitchat Agent schema definitions."""

from pydantic import BaseModel, Field


class ChitchatResponse(BaseModel):
    """Chitchat response schema."""

    reply: str = Field(description="Friendly reply to the user's non-business message")
