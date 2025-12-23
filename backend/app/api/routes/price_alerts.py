"""Price alert routes."""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, get_optional_user
from app.models.user import Profile
from app.models.subscription import PriceAlert
from app.schemas.price_alert import (
    CreatePriceAlertRequest,
    PriceAlertResponse,
    UpdatePriceAlertRequest,
    PriceAlertListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/price-alerts", tags=["price-alerts"])


@router.post("/create")
async def create_price_alert(
    request_data: CreatePriceAlertRequest,
    request: Request,
    current_user: Optional[Profile] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a price alert for a product."""
    try:
        # Validate email
        email = request_data.email or (current_user.email if current_user else None)
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required for non-authenticated users"
            )

        # Check if alert already exists
        result = await db.execute(
            select(PriceAlert).where(
                (PriceAlert.product_id == request_data.product_id) &
                (PriceAlert.email == email) &
                (PriceAlert.is_active == True)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Price alert already exists for this product"
            )

        # Create new alert
        alert = PriceAlert(
            user_id=current_user.id if current_user else None,
            product_id=request_data.product_id,
            product_name=request_data.product_name,
            product_url=request_data.product_url,
            target_price=request_data.target_price,
            current_price=request_data.current_price,
            currency=request_data.currency,
            email=email,
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        logger.info(f"Price alert created: {alert.id} for product {request_data.product_id}")

        return PriceAlertResponse.from_orm(alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating price alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create price alert")


@router.get("/list")
async def list_price_alerts(
    request: Request,
    current_user: Optional[Profile] = Depends(get_optional_user),
    email: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """List price alerts for current user or email."""
    try:
        # Determine which alerts to fetch
        if current_user:
            # For authenticated users, get their alerts
            result = await db.execute(
                select(PriceAlert).where(PriceAlert.user_id == current_user.id)
                .order_by(PriceAlert.created_at.desc())
            )
        elif email:
            # For non-authenticated users, fetch by email
            result = await db.execute(
                select(PriceAlert).where(PriceAlert.email == email)
                .order_by(PriceAlert.created_at.desc())
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either authentication or email parameter is required"
            )

        alerts = result.scalars().all()

        if active_only:
            alerts = [a for a in alerts if a.is_active]

        return PriceAlertListResponse(
            total=len(alerts),
            alerts=[PriceAlertResponse.from_orm(a) for a in alerts]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price alerts")


@router.get("/{alert_id}")
async def get_price_alert(
    alert_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific price alert."""
    try:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(status_code=404, detail="Price alert not found")

        # Check authorization
        if current_user and alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        return PriceAlertResponse.from_orm(alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price alert")


@router.put("/{alert_id}")
async def update_price_alert(
    alert_id: str,
    request_data: UpdatePriceAlertRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a price alert."""
    try:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(status_code=404, detail="Price alert not found")

        # Check authorization
        if alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        # Update fields
        if request_data.target_price is not None:
            alert.target_price = request_data.target_price
        if request_data.is_active is not None:
            alert.is_active = request_data.is_active

        await db.commit()
        await db.refresh(alert)

        return PriceAlertResponse.from_orm(alert)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating price alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to update price alert")


@router.delete("/{alert_id}")
async def delete_price_alert(
    alert_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a price alert."""
    try:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(status_code=404, detail="Price alert not found")

        # Check authorization
        if alert.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        await db.delete(alert)
        await db.commit()

        return {"message": "Price alert deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting price alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete price alert")
