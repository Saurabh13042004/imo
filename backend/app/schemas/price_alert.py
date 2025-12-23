"""Price alert schemas."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class CreatePriceAlertRequest(BaseModel):
    """Request to create a price alert."""
    product_id: str
    product_name: str
    product_url: str
    target_price: float = Field(..., gt=0, description="Target price must be greater than 0")
    current_price: Optional[float] = None
    currency: str = "usd"
    email: Optional[EmailStr] = None  # Optional if user is authenticated


class PriceAlertResponse(BaseModel):
    """Price alert response."""
    id: str
    product_id: str
    product_name: str
    product_url: str
    target_price: float
    current_price: Optional[float]
    currency: str
    email: str
    is_active: bool
    alert_sent: bool
    alert_sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class UpdatePriceAlertRequest(BaseModel):
    """Request to update a price alert."""
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class PriceAlertListResponse(BaseModel):
    """List of price alerts."""
    total: int
    alerts: list[PriceAlertResponse]
