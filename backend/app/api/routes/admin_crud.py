"""Admin CRUD operations for users, transactions, and subscriptions."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import Profile
from app.models.subscription import Subscription, PaymentTransaction
from sqlalchemy import select, delete as sql_delete

router = APIRouter(prefix="/api/v1/admin/crud", tags=["admin-crud"])


# ==================== Authentication & Authorization ====================

async def admin_required(
    current_user: Optional[Profile] = Depends(get_current_user),
) -> Profile:
    """Dependency to ensure user is admin."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[ADMIN_REQUIRED] Checking admin access. Current user: {current_user}")
    
    if not current_user:
        logger.warning("[ADMIN_REQUIRED] No current user found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    # Check if user has admin access level
    if current_user.access_level != "admin":
        logger.warning(f"[ADMIN_REQUIRED] User {current_user.id} has access_level '{current_user.access_level}', not 'admin'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    logger.info(f"[ADMIN_REQUIRED] Admin check passed for user {current_user.id}")
    return current_user


# ==================== Schemas ====================

class UserUpdate(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    subscription_tier: Optional[str] = None  # free, trial, premium
    access_level: Optional[str] = None  # basic, admin
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: str
    full_name: str
    subscription_tier: str
    access_level: str
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    """Create transaction."""
    user_id: UUID
    subscription_id: Optional[UUID] = None
    transaction_id: str
    amount: float
    currency: str = "usd"
    type: str  # subscription, one_time, refund
    status: str = "pending"  # pending, success, failed, refunded
    stripe_payment_intent_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionUpdate(BaseModel):
    """Update transaction."""
    status: Optional[str] = None
    amount: Optional[float] = None
    metadata_json: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response model."""
    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID]
    transaction_id: str
    amount: float
    currency: str
    type: str
    status: str
    stripe_payment_intent_id: Optional[str]
    stripe_session_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    """Create subscription."""
    user_id: UUID
    plan_type: str  # free, trial, premium
    billing_cycle: Optional[str] = None  # monthly, yearly
    is_active: bool = False
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_product_id: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """Update subscription."""
    plan_type: Optional[str] = None
    billing_cycle: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_product_id: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Subscription response model."""
    id: UUID
    user_id: UUID
    plan_type: str
    billing_cycle: Optional[str]
    is_active: bool
    subscription_start: datetime
    subscription_end: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Users CRUD ====================

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> UserResponse:
    """Create a new user (admin only)."""
    if not user_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    # Check if user already exists
    result = await db.execute(
        select(Profile).where(Profile.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    new_user = Profile(
        email=user_data.email,
        full_name=user_data.full_name or "",
        subscription_tier=user_data.subscription_tier or "free",
        access_level=user_data.access_level or "basic",
        avatar_url=user_data.avatar_url,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> UserResponse:
    """Get user by ID."""
    result = await db.execute(
        select(Profile).where(Profile.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> UserResponse:
    """Update user by ID."""
    result = await db.execute(
        select(Profile).where(Profile.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.email:
        # Check if email is already taken
        email_result = await db.execute(
            select(Profile).where(
                Profile.email == user_data.email,
                Profile.id != user_id
            )
        )
        if email_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.subscription_tier is not None:
        user.subscription_tier = user_data.subscription_tier
    if user_data.access_level is not None:
        user.access_level = user_data.access_level
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> None:
    """Delete user by ID."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[DELETE USER] Attempting to delete user {user_id}")
    logger.info(f"[DELETE USER] Admin user: {_admin.id} ({_admin.email})")
    
    result = await db.execute(
        select(Profile).where(Profile.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"[DELETE USER] User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"[DELETE USER] Deleting user {user_id}")
    await db.delete(user)
    await db.commit()
    logger.info(f"[DELETE USER] User {user_id} deleted successfully")


# ==================== Transactions CRUD ====================

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> TransactionResponse:
    """Create a new transaction."""
    # Verify user exists
    user_result = await db.execute(
        select(Profile).where(Profile.id == transaction_data.user_id)
    )
    if not user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify subscription exists if provided
    if transaction_data.subscription_id:
        sub_result = await db.execute(
            select(Subscription).where(Subscription.id == transaction_data.subscription_id)
        )
        if not sub_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
    
    new_transaction = PaymentTransaction(
        user_id=transaction_data.user_id,
        subscription_id=transaction_data.subscription_id,
        transaction_id=transaction_data.transaction_id,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        type=transaction_data.type,
        status=transaction_data.status,
        stripe_payment_intent_id=transaction_data.stripe_payment_intent_id,
        stripe_session_id=transaction_data.stripe_session_id,
        metadata_json=transaction_data.metadata_json,
    )
    
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    
    return TransactionResponse.from_orm(new_transaction)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> TransactionResponse:
    """Get transaction by ID."""
    result = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.from_orm(transaction)


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> TransactionResponse:
    """Update transaction by ID."""
    result = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update fields
    if transaction_data.status is not None:
        transaction.status = transaction_data.status
    if transaction_data.amount is not None:
        transaction.amount = transaction_data.amount
    if transaction_data.metadata_json is not None:
        transaction.metadata_json = transaction_data.metadata_json
    
    transaction.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse.from_orm(transaction)


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> None:
    """Delete transaction by ID."""
    result = await db.execute(
        select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    await db.delete(transaction)
    await db.commit()


# ==================== Subscriptions CRUD ====================

@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> SubscriptionResponse:
    """Create a new subscription."""
    # Verify user exists
    user_result = await db.execute(
        select(Profile).where(Profile.id == subscription_data.user_id)
    )
    if not user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_subscription = Subscription(
        user_id=subscription_data.user_id,
        plan_type=subscription_data.plan_type,
        billing_cycle=subscription_data.billing_cycle,
        is_active=subscription_data.is_active,
        subscription_start=subscription_data.subscription_start or datetime.utcnow(),
        subscription_end=subscription_data.subscription_end,
        trial_start=subscription_data.trial_start,
        trial_end=subscription_data.trial_end,
        stripe_customer_id=subscription_data.stripe_customer_id,
        stripe_subscription_id=subscription_data.stripe_subscription_id,
        stripe_product_id=subscription_data.stripe_product_id,
    )
    
    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)
    
    return SubscriptionResponse.from_orm(new_subscription)


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> SubscriptionResponse:
    """Get subscription by ID."""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return SubscriptionResponse.from_orm(subscription)


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> SubscriptionResponse:
    """Update subscription by ID."""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Update fields
    if subscription_data.plan_type is not None:
        subscription.plan_type = subscription_data.plan_type
    if subscription_data.billing_cycle is not None:
        subscription.billing_cycle = subscription_data.billing_cycle
    if subscription_data.is_active is not None:
        subscription.is_active = subscription_data.is_active
    if subscription_data.subscription_start is not None:
        subscription.subscription_start = subscription_data.subscription_start
    if subscription_data.subscription_end is not None:
        subscription.subscription_end = subscription_data.subscription_end
    if subscription_data.trial_start is not None:
        subscription.trial_start = subscription_data.trial_start
    if subscription_data.trial_end is not None:
        subscription.trial_end = subscription_data.trial_end
    if subscription_data.stripe_customer_id is not None:
        subscription.stripe_customer_id = subscription_data.stripe_customer_id
    if subscription_data.stripe_subscription_id is not None:
        subscription.stripe_subscription_id = subscription_data.stripe_subscription_id
    if subscription_data.stripe_product_id is not None:
        subscription.stripe_product_id = subscription_data.stripe_product_id
    
    subscription.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(subscription)
    
    return SubscriptionResponse.from_orm(subscription)


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Profile = Depends(admin_required),
) -> None:
    """Delete subscription by ID."""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    await db.delete(subscription)
    await db.commit()
