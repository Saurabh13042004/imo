"""Payment and subscription routes."""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.stripe_service import StripeService
from app.models.user import Profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


class CreateCheckoutSessionRequest(BaseModel):
    """Request to create a checkout session."""
    plan_type: str  # 'trial' or 'premium'
    billing_cycle: Optional[str] = 'monthly'  # 'monthly' or 'yearly'
    success_url: str
    cancel_url: str


class CheckoutCallbackRequest(BaseModel):
    """Request to handle checkout callback."""
    session_id: str


class SubscriptionResponse(BaseModel):
    """User subscription response."""
    plan_type: str
    billing_cycle: Optional[str]
    is_active: bool
    subscription_start: Optional[str]
    subscription_end: Optional[str]
    trial_start: Optional[str]
    trial_end: Optional[str]
    is_trial: bool
    days_remaining: int


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for trial or premium subscription."""
    try:
        result = await StripeService.create_checkout_session(
            user_id=str(current_user.id),
            email=current_user.email,
            plan_type=request.plan_type,
            billing_cycle=request.billing_cycle,
            session=db,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {
            'success': True,
            'session_id': result['session_id'],
            'url': result['url'],
        }
    except Exception as e:
        import traceback
        logger.error(f"Error creating checkout session: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/checkout-complete")
async def checkout_complete(
    request: CheckoutCallbackRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Handle checkout completion."""
    try:
        success = await StripeService.handle_checkout_complete(
            session_id=request.session_id,
            user_id=str(current_user.id),
            session=db,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to process checkout")

        return {
            'success': True,
            'message': 'Subscription activated successfully',
        }
    except Exception as e:
        logger.error(f"Error in checkout complete: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/start-trial")
async def start_trial(
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a 7-day trial subscription."""
    try:
        success = await StripeService.create_trial_subscription(
            user_id=str(current_user.id),
            session=db,
        )
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Could not start trial. You may already have an active subscription.",
            )

        return {
            'success': True,
            'message': 'Trial subscription started. You have 7 days of premium access!',
        }
    except Exception as e:
        logger.error(f"Error starting trial: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription")
async def get_subscription(
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user subscription details."""
    try:
        subscription = await StripeService.get_user_subscription(
            user_id=str(current_user.id),
            session=db,
        )
        if not subscription:
            return {
                'plan_type': 'free',
                'is_active': False,
                'is_trial': False,
                'days_remaining': 0,
            }

        return subscription
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subscription")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhooks."""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")

        event = StripeService.verify_webhook_signature(payload, sig_header)

        if not event:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle specific events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata'].get('user_id')
            session_id = session['id']

            await StripeService.handle_checkout_complete(
                session_id=session_id,
                user_id=user_id,
                session=db,
            )

        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            await StripeService.handle_subscription_updated(
                stripe_subscription_id=subscription['id'],
                session=db,
            )

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            await StripeService.handle_subscription_deleted(
                stripe_subscription_id=subscription['id'],
                session=db,
            )

        return {'success': True, 'received': True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
