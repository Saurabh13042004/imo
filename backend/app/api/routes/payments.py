"""Payment and subscription routes."""
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.dependencies import get_db, get_current_user
from app.services.stripe_service import StripeService
from app.models.user import Profile
from app.models.subscription import PaymentTransaction

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


class PaymentTransactionResponse(BaseModel):
    """Payment transaction response."""
    id: str
    user_id: str
    subscription_id: Optional[str]
    transaction_id: str
    amount: str
    currency: str
    type: str  # subscription, one_time, refund
    status: str  # pending, success, failed, refunded
    stripe_payment_intent_id: Optional[str]
    stripe_session_id: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


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
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Could not start trial. You may already have an active subscription."
        logger.error(f"Error starting trial: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


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


class CreatePortalSessionRequest(BaseModel):
    """Request to create a billing portal session."""
    return_url: str


@router.post("/create-portal-session")
async def create_portal_session(
    request: CreatePortalSessionRequest,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe billing portal session."""
    try:
        result = await StripeService.create_billing_portal_session(
            user_id=str(current_user.id),
            session=db,
            return_url=request.return_url,
        )
        return {
            'success': True,
            'url': result['url'],
        }
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions")
async def get_payment_transactions(
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PaymentTransactionResponse]:
    """Get all payment transactions for the current user."""
    try:
        stmt = (
            select(PaymentTransaction)
            .where(PaymentTransaction.user_id == current_user.id)
            .order_by(desc(PaymentTransaction.created_at))
        )
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        return [
            PaymentTransactionResponse(
                id=str(t.id),
                user_id=str(t.user_id),
                subscription_id=str(t.subscription_id) if t.subscription_id else None,
                transaction_id=t.transaction_id,
                amount=str(t.amount),
                currency=t.currency,
                type=t.type,
                status=t.status,
                stripe_payment_intent_id=t.stripe_payment_intent_id,
                stripe_session_id=t.stripe_session_id,
                created_at=t.created_at.isoformat() if t.created_at else None,
                updated_at=t.updated_at.isoformat() if t.updated_at else None,
            )
            for t in transactions
        ]
    except Exception as e:
        logger.error(f"Error fetching payment transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")


@router.get("/transactions/{transaction_id}")
async def get_payment_transaction(
    transaction_id: str,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentTransactionResponse:
    """Get a specific payment transaction by ID."""
    try:
        stmt = (
            select(PaymentTransaction)
            .where(
                (PaymentTransaction.id == transaction_id) &
                (PaymentTransaction.user_id == current_user.id)
            )
        )
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return PaymentTransactionResponse(
            id=str(transaction.id),
            user_id=str(transaction.user_id),
            subscription_id=str(transaction.subscription_id) if transaction.subscription_id else None,
            transaction_id=transaction.transaction_id,
            amount=str(transaction.amount),
            currency=transaction.currency,
            type=transaction.type,
            status=transaction.status,
            stripe_payment_intent_id=transaction.stripe_payment_intent_id,
            stripe_session_id=transaction.stripe_session_id,
            created_at=transaction.created_at.isoformat() if transaction.created_at else None,
            updated_at=transaction.updated_at.isoformat() if transaction.updated_at else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction")


@router.get("/transaction-status")
async def check_transaction_status(
    payment_intent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    current_user: Profile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check real-time status of a payment transaction from Stripe.
    
    Useful for monitoring payment processing status.
    """
    try:
        if not payment_intent_id and not session_id:
            raise HTTPException(
                status_code=400,
                detail="Either payment_intent_id or session_id required"
            )
        
        # Get transaction details from Stripe
        details = await StripeService.get_transaction_details(
            payment_intent_id=payment_intent_id,
            session_id=session_id,
        )
        
        if not details:
            raise HTTPException(status_code=404, detail="Transaction not found in Stripe")
        
        # Update local transaction record if it exists
        if payment_intent_id:
            stmt = select(PaymentTransaction).where(
                (PaymentTransaction.stripe_payment_intent_id == payment_intent_id) &
                (PaymentTransaction.user_id == current_user.id)
            )
        else:
            stmt = select(PaymentTransaction).where(
                (PaymentTransaction.stripe_session_id == session_id) &
                (PaymentTransaction.user_id == current_user.id)
            )
        
        result = await db.execute(stmt)
        local_transaction = result.scalar_one_or_none()
        
        # Map Stripe status to our status
        status_mapping = {
            'paid': 'success',
            'unpaid': 'pending',
            'no_payment_required': 'success',
            'succeeded': 'success',
            'processing': 'pending',
            'requires_action': 'pending',
            'requires_payment_method': 'failed',
            'canceled': 'failed',
        }
        
        mapped_status = status_mapping.get(details.get('status'), 'pending')
        
        # Update local record if status changed
        if local_transaction and local_transaction.status != mapped_status:
            local_transaction.status = mapped_status
            await db.commit()
        
        return {
            'status': mapped_status,
            'stripe_status': details.get('status'),
            'amount': details.get('amount'),
            'currency': details.get('currency'),
            'created': details.get('created').isoformat() if details.get('created') else None,
            'error': details.get('last_payment_error'),
            'local_transaction': PaymentTransactionResponse(
                id=str(local_transaction.id) if local_transaction else None,
                user_id=str(local_transaction.user_id) if local_transaction else str(current_user.id),
                subscription_id=str(local_transaction.subscription_id) if local_transaction and local_transaction.subscription_id else None,
                transaction_id=local_transaction.transaction_id if local_transaction else (payment_intent_id or session_id),
                amount=str(local_transaction.amount) if local_transaction else str(details.get('amount', 0)),
                currency=local_transaction.currency if local_transaction else details.get('currency', 'USD'),
                type=local_transaction.type if local_transaction else 'subscription',
                status=local_transaction.status if local_transaction else mapped_status,
                stripe_payment_intent_id=local_transaction.stripe_payment_intent_id if local_transaction else payment_intent_id,
                stripe_session_id=local_transaction.stripe_session_id if local_transaction else session_id,
                created_at=local_transaction.created_at.isoformat() if local_transaction and local_transaction.created_at else None,
                updated_at=local_transaction.updated_at.isoformat() if local_transaction and local_transaction.updated_at else None,
            ) if local_transaction else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking transaction status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check transaction status")


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
            session_obj = event['data']['object']
            user_id = session_obj['metadata'].get('user_id')
            session_id = session_obj['id']

            await StripeService.handle_checkout_complete(
                session_id=session_id,
                user_id=user_id,
                session=db,
            )

        elif event['type'] == 'checkout.session.expired':
            # Track failed/expired checkout sessions
            session_obj = event['data']['object']
            user_id = session_obj['metadata'].get('user_id')
            session_id = session_obj['id']
            
            await StripeService.create_or_update_payment_transaction(
                user_id=user_id,
                subscription_id=None,
                transaction_id=session_id,
                amount=0,
                currency='usd',
                txn_type='subscription',
                status='failed',
                stripe_session_id=session_id,
                db_session=db,
            )
            await db.commit()

        elif event['type'] == 'charge.failed':
            # Payment charge failed
            charge = event['data']['object']
            user_id = charge['metadata'].get('user_id')
            transaction_id = charge['id']
            amount = charge['amount'] / 100  # Convert from cents
            
            if user_id:
                await StripeService.create_or_update_payment_transaction(
                    user_id=user_id,
                    subscription_id=charge['metadata'].get('subscription_id'),
                    transaction_id=transaction_id,
                    amount=amount,
                    currency=charge['currency'].upper(),
                    txn_type='subscription',
                    status='failed',
                    stripe_payment_intent_id=charge.get('payment_intent'),
                    db_session=db,
                )
                await db.commit()

        elif event['type'] == 'charge.refunded':
            # Payment refunded
            charge = event['data']['object']
            user_id = charge['metadata'].get('user_id')
            transaction_id = charge['id']
            amount = (charge['amount_refunded'] or charge['amount']) / 100
            
            if user_id:
                await StripeService.create_or_update_payment_transaction(
                    user_id=user_id,
                    subscription_id=charge['metadata'].get('subscription_id'),
                    transaction_id=transaction_id,
                    amount=amount,
                    currency=charge['currency'].upper(),
                    txn_type='refund',
                    status='refunded',
                    stripe_payment_intent_id=charge.get('payment_intent'),
                    db_session=db,
                )
                await db.commit()

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
