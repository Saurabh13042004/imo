"""Admin dashboard routes."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from decimal import Decimal

from app.models.user import Profile, UserRole
from app.models.subscription import Subscription, PaymentTransaction
from app.models.product import Product
from app.models.review import Review
from app.models.contact import Contact
from app.models.task import BackgroundAnalysisTask
from app.models.analytics import AnalyticsEvent, ErrorLog
from app.api.dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def _is_admin(user: Profile) -> bool:
    """Check if user is admin."""
    # Assuming admin check is based on role or subscription plan
    return user.subscription_tier == "admin" or user.access_level == "admin"


async def admin_required(
    current_user: Optional[Profile] = Depends(get_current_user),
) -> Profile:
    """Dependency to ensure user is admin."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    return current_user


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required)
):
    """Get admin dashboard statistics."""
    try:
        # Total users
        total_users_result = await db.execute(
            select(func.count(Profile.id))
        )
        total_users = total_users_result.scalar() or 0

        # Active subscriptions (premium + trial)
        active_subs_result = await db.execute(
            select(func.count(Subscription.id)).where(
                and_(
                    Subscription.is_active == True,
                    Subscription.plan_type.in_(["premium", "trial"])
                )
            )
        )
        total_subscriptions = active_subs_result.scalar() or 0

        # Active trials
        active_trials_result = await db.execute(
            select(func.count(Subscription.id)).where(
                and_(
                    Subscription.plan_type == "trial",
                    Subscription.is_active == True,
                    Subscription.trial_end > func.now()
                )
            )
        )
        active_trials = active_trials_result.scalar() or 0

        # Monthly revenue
        month_ago = datetime.utcnow() - timedelta(days=30)
        revenue_result = await db.execute(
            select(func.sum(PaymentTransaction.amount)).where(
                and_(
                    PaymentTransaction.created_at >= month_ago,
                    PaymentTransaction.status == "success"
                )
            )
        )
        monthly_revenue = float(revenue_result.scalar() or 0)

        # Total URLs (products)
        total_urls_result = await db.execute(
            select(func.count(Product.id))
        )
        total_urls = total_urls_result.scalar() or 0

        # API calls (from analytics events)
        api_calls_result = await db.execute(
            select(func.count(AnalyticsEvent.id))
        )
        api_calls = api_calls_result.scalar() or 0

        return {
            "totalUsers": total_users,
            "totalSubscriptions": total_subscriptions,
            "activeTrials": active_trials,
            "monthlyRevenue": monthly_revenue,
            "totalUrls": total_urls,
            "apiCalls": api_calls,
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
):
    """List all users with optional filtering."""
    try:
        query = select(Profile)

        if search:
            query = query.where(
                Profile.email.ilike(f"%{search}%") | 
                Profile.full_name.ilike(f"%{search}%")
            )

        if subscription_tier:
            query = query.where(Profile.subscription_tier == subscription_tier)

        # Get total count
        count_result = await db.execute(select(func.count(Profile.id)).select_from(Profile))
        total = count_result.scalar() or 0

        # Get paginated results
        result = await db.execute(
            query.order_by(desc(Profile.created_at)).offset(skip).limit(limit)
        )
        users = result.scalars().all()

        user_data = []
        for user in users:
            # Get subscription info
            sub_result = await db.execute(
                select(Subscription).where(
                    Subscription.user_id == user.id
                ).order_by(desc(Subscription.created_at))
            )
            latest_sub = sub_result.scalars().first()

            user_data.append({
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "subscriptionTier": user.subscription_tier,
                "joinDate": user.created_at.isoformat(),
                "lastActive": user.updated_at.isoformat(),
                "activeSubscription": latest_sub.plan_type if latest_sub else None,
            })

        return {
            "data": user_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/subscriptions")
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None),  # active, expired, trial
):
    """List all subscriptions."""
    try:
        query = select(Subscription)

        if status == "active":
            query = query.where(Subscription.is_active == True)
        elif status == "trial":
            query = query.where(Subscription.plan_type == "trial")
        elif status == "expired":
            query = query.where(
                and_(
                    Subscription.subscription_end < func.now(),
                    Subscription.is_active == False
                )
            )

        # Get total count
        count_result = await db.execute(select(func.count(Subscription.id)).select_from(Subscription))
        total = count_result.scalar() or 0

        result = await db.execute(
            query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit)
        )
        subscriptions = result.scalars().all()

        sub_data = []
        for sub in subscriptions:
            # Get user
            user_result = await db.execute(
                select(Profile).where(Profile.id == sub.user_id)
            )
            user = user_result.scalars().first()

            sub_data.append({
                "id": str(sub.id),
                "userId": str(sub.user_id),
                "userEmail": user.email if user else None,
                "planType": sub.plan_type,
                "billingCycle": sub.billing_cycle,
                "isActive": sub.is_active,
                "subscriptionStart": sub.subscription_start.isoformat() if sub.subscription_start else None,
                "subscriptionEnd": sub.subscription_end.isoformat() if sub.subscription_end else None,
                "trialStart": sub.trial_start.isoformat() if sub.trial_start else None,
                "trialEnd": sub.trial_end.isoformat() if sub.trial_end else None,
            })

        return {
            "data": sub_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscriptions"
        )


@router.get("/contacts")
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """List all contact form submissions."""
    try:
        result = await db.execute(
            select(Contact).order_by(desc(Contact.created_at)).offset(skip).limit(limit)
        )
        contacts = result.scalars().all()

        count_result = await db.execute(select(func.count(Contact.id)))
        total = count_result.scalar() or 0

        contact_data = [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "subject": c.subject,
                "message": c.message,
                "status": "pending",  # Default status for contacts
                "createdAt": c.created_at.isoformat(),
            }
            for c in contacts
        ]

        return {
            "data": contact_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contacts"
        )


@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    source: Optional[str] = Query(None),
):
    """List all products."""
    try:
        query = select(Product)

        if source:
            query = query.where(Product.source == source)

        # Get total count
        count_result = await db.execute(select(func.count(Product.id)).select_from(Product))
        total = count_result.scalar() or 0

        result = await db.execute(
            query.order_by(desc(Product.created_at)).offset(skip).limit(limit)
        )
        products = result.scalars().all()

        product_data = [
            {
                "id": str(p.id),
                "title": p.title,
                "source": p.source,
                "sourceId": p.source_id,
                "price": float(p.price) if p.price else None,
                "currency": p.currency,
                "rating": float(p.rating) if p.rating else None,
                "reviewCount": p.review_count,
                "imageUrl": p.image_url,
                "createdAt": p.created_at.isoformat(),
            }
            for p in products
        ]

        return {
            "data": product_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products"
        )


@router.get("/reviews")
async def list_reviews(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """List all reviews."""
    try:
        result = await db.execute(
            select(Review).order_by(desc(Review.fetched_at)).offset(skip).limit(limit)
        )
        reviews = result.scalars().all()

        count_result = await db.execute(select(func.count(Review.id)))
        total = count_result.scalar() or 0

        review_data = []
        for review in reviews:
            # Get product
            product_result = await db.execute(
                select(Product).where(Product.id == review.product_id)
            )
            product = product_result.scalars().first()

            review_data.append({
                "id": str(review.id),
                "productTitle": product.title if product else None,
                "rating": float(review.rating) if review.rating else 0,
                "reviewTitle": review.review_title,
                "reviewText": review.review_text[:100] if review.review_text else None,
                "author": review.author,
                "source": review.source,
                "postedAt": review.posted_at.isoformat() if review.posted_at else None,
                "fetchedAt": review.fetched_at.isoformat() if review.fetched_at else None,
            })

        return {
            "data": review_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )


@router.get("/errors")
async def list_errors(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """List error logs."""
    try:
        result = await db.execute(
            select(ErrorLog).order_by(desc(ErrorLog.created_at)).offset(skip).limit(limit)
        )
        errors = result.scalars().all()

        count_result = await db.execute(select(func.count(ErrorLog.id)))
        total = count_result.scalar() or 0

        error_data = [
            {
                "id": str(e.id),
                "functionName": e.function_name,
                "errorType": e.error_type,
                "errorMessage": e.error_message,
                "createdAt": e.created_at.isoformat(),
            }
            for e in errors
        ]

        return {
            "data": error_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching error logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch error logs"
        )


@router.get("/tasks")
async def list_background_tasks(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None),  # running, completed, failed
):
    """List background analysis tasks."""
    try:
        query = select(BackgroundAnalysisTask)

        if status:
            query = query.where(BackgroundAnalysisTask.status == status)

        # Get total count
        count_result = await db.execute(
            select(func.count(BackgroundAnalysisTask.id)).select_from(BackgroundAnalysisTask)
        )
        total = count_result.scalar() or 0

        result = await db.execute(
            query.order_by(desc(BackgroundAnalysisTask.started_at)).offset(skip).limit(limit)
        )
        tasks = result.scalars().all()

        task_data = [
            {
                "id": str(t.id),
                "status": t.status,
                "productsAnalyzed": t.products_analyzed,
                "totalProducts": t.total_products,
                "startedAt": t.started_at.isoformat(),
                "completedAt": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ]

        return {
            "data": task_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching background tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch background tasks"
        )


@router.get("/payment-transactions")
async def list_payment_transactions(
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None),  # pending, success, failed, refunded
):
    """List all payment transactions."""
    try:
        query = select(PaymentTransaction)

        if status:
            query = query.where(PaymentTransaction.status == status)

        # Get total count
        count_result = await db.execute(
            select(func.count(PaymentTransaction.id)).select_from(PaymentTransaction)
        )
        total = count_result.scalar() or 0

        result = await db.execute(
            query.order_by(desc(PaymentTransaction.created_at)).offset(skip).limit(limit)
        )
        transactions = result.scalars().all()

        transaction_data = []
        for t in transactions:
            # Get user
            user_result = await db.execute(
                select(Profile).where(Profile.id == t.user_id)
            )
            user = user_result.scalars().first()

            transaction_data.append({
                "id": str(t.id),
                "userEmail": user.email if user else None,
                "amount": float(t.amount),
                "currency": t.currency,
                "type": t.type,
                "status": t.status,
                "createdAt": t.created_at.isoformat(),
            })

        return {
            "data": transaction_data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error fetching payment transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment transactions"
        )


@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
):
    """Update user role (admin, moderator, user)."""
    try:
        # Get user
        user_result = await db.execute(
            select(Profile).where(Profile.id == user_id)
        )
        user = user_result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user_roles entry exists
        role_result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        user_role = role_result.scalars().first()

        if user_role:
            user_role.role = role
        else:
            user_role = UserRole(
                user_id=user_id,
                role=role
            )
            db.add(user_role)

        await db.commit()

        return {"message": f"User role updated to {role}"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.post("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: str,
    plan_type: str,  # free, trial, premium
    db: AsyncSession = Depends(get_db),
    admin: Profile = Depends(admin_required),
):
    """Manually update user subscription (admin action)."""
    try:
        # Get user
        user_result = await db.execute(
            select(Profile).where(Profile.id == user_id)
        )
        user = user_result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user subscription tier
        user.subscription_tier = plan_type

        # Create or update subscription record
        sub_result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id
            ).order_by(desc(Subscription.created_at))
        )
        subscription = sub_result.scalars().first()

        if subscription:
            subscription.plan_type = plan_type
            if plan_type == "trial":
                subscription.is_active = True
            elif plan_type == "premium":
                subscription.is_active = True
        else:
            subscription = Subscription(
                user_id=user_id,
                plan_type=plan_type,
                is_active=plan_type != "free"
            )
            db.add(subscription)

        await db.commit()

        return {
            "message": f"User subscription updated to {plan_type}",
            "subscriptionTier": plan_type,
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user subscription"
        )
