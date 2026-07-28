"""Quotation API endpoints."""

import logging
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class QuotationItem(BaseModel):
    """A single quotation line item."""

    name: str = Field(description="Test item name")
    price: int = Field(description="Price in CNY")


class QuotationRequest(BaseModel):
    """Quotation request payload."""

    product: str = Field(description="Product name to be tested")
    tests: List[str] = Field(description="List of test items to quote")


class QuotationResponse(BaseModel):
    """Quotation response."""

    items: List[QuotationItem] = Field(description="List of quoted test items with prices")
    total_price: int = Field(description="Total price in CNY")


@router.post("/quotation", response_model=QuotationResponse)
async def create_quotation(request: QuotationRequest) -> QuotationResponse:
    """Create a quotation for the specified product and test items.

    Note: This is a placeholder. Phase 3 will implement full price query
    and calculation tool integration.

    Args:
        request: Quotation request with product and test items.

    Returns:
        Quotation with itemized prices and total.
    """
    logger.info(f"Quotation API: request for product '{request.product}' with tests {request.tests}")

    # Placeholder response — will be replaced with price query + calculate in Phase 3
    items = [QuotationItem(name=test, price=0) for test in request.tests]
    return QuotationResponse(items=items, total_price=0)
