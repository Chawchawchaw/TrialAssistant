"""Quotation Agent schema definitions."""

from typing import List

from pydantic import BaseModel, Field


class QuotationItem(BaseModel):
    """A single quotation line item."""

    name: str = Field(description="Test item name")
    standard: str = Field(default="", description="Testing standard")
    price: int = Field(default=0, description="Price in CNY")
    duration: str = Field(default="", description="Estimated duration")


class QuotationResult(BaseModel):
    """Complete quotation result."""

    items: List[QuotationItem] = Field(description="List of quoted items")
    total_price: int = Field(description="Total price in CNY (calculated by tool, NOT by LLM)")
    item_count: int = Field(description="Number of items")
