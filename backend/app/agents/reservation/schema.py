"""Reservation Agent schema definitions."""

from typing import List, Optional

from pydantic import BaseModel, Field


class LabResource(BaseModel):
    """Laboratory resource information."""

    lab_id: str = Field(description="Laboratory ID")
    name: str = Field(description="Laboratory name")
    location: str = Field(description="Location")
    equipment: List[dict] = Field(default=[], description="Available equipment")
    available_slots: List[dict] = Field(default=[], description="Available time slots")


class BookingResult(BaseModel):
    """Result of a booking creation."""

    success: bool = Field(description="Whether booking was successful")
    booking_id: Optional[str] = Field(default=None, description="Booking ID if successful")
    message: str = Field(description="Result message")
