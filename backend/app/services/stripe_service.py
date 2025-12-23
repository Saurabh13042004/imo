"""Stripe payment service for handling subscriptions and payments."""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.subscription import Subscription, PaymentTransaction
from app.models.user import Profile

logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.startswith('sk_'):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.info(f"Stripe API key loaded. Key type: {'LIVE' if 'sk_live' in settings.STRIPE_SECRET_KEY else 'TEST'}")
else:
    logger.warning("STRIPE_SECRET_KEY is not configured or invalid. Stripe operations will fail.")
    logger.warning(f"STRIPE_SECRET_KEY value: {settings.STRIPE_SECRET_KEY}")
    stripe.api_key = None


class StripeService:
    """Service for managing Stripe payments and subscriptions."""

    @staticmethod
    async def create_checkout_session(
        user_id: str,
        email: str,
        plan_type: str,  # 'trial' or 'premium'
        billing_cycle: str,  # 'monthly' or 'yearly'
        session: AsyncSession,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """Create a Stripe checkout session for trial or premium subscription."""
        try:
            # Check if Stripe is configured
            if not stripe.api_key:
                raise Exception(
                    "Stripe is not configured. Please set STRIPE_SECRET_KEY in environment variables. "
                    "Get your key from https://dashboard.stripe.com/apikeys"
                )
            # Determine pricing
            if plan_type == 'trial':
                # Trial: Free for 7 days
                price_data = {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'IMO Premium - 7 Day Free Trial',
                        'description': 'Premium access for 7 days (Free)',
                    },
                    'unit_amount': 0,  # $0
                }
                line_items = [{
                    'price_data': price_data,
                    'quantity': 1,
                }]
            else:  # premium
                # Premium: Recurring subscription
                if billing_cycle == 'yearly':
                    price = settings.PREMIUM_YEARLY_PRICE
                    lookup_key = 'premium_yearly'
                else:  # monthly
                    price = settings.PREMIUM_MONTHLY_PRICE
                    lookup_key = 'premium_monthly'

                price_data = {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'IMO Premium - {billing_cycle.capitalize()}',
                        'description': 'Unlimited product searches and AI analysis',
                    },
                    'unit_amount': price,
                    'recurring': {
                        'interval': 'month' if billing_cycle == 'monthly' else 'year',
                        'interval_count': 1,
                    },
                }
                line_items = [{
                    'price_data': price_data,
                    'quantity': 1,
                }]

            # Create checkout session
            logger.info(f"Creating checkout session with stripe.api_key set: {bool(stripe.api_key)}")
            logger.info(f"stripe.checkout exists: {hasattr(stripe, 'checkout')}")
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=email,
                line_items=line_items,
                mode='subscription' if plan_type == 'premium' else 'payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'billing_cycle': billing_cycle,
                },
                allow_promotion_codes=True,
            )

            logger.info(f"Created Stripe checkout session {checkout_session.id} for user {user_id}")
            return {
                'session_id': checkout_session.id,
                'url': checkout_session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise Exception(f"Payment setup failed: {str(e)}")

    @staticmethod
    async def handle_checkout_complete(
        session_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """Handle successful checkout completion."""
        try:
            # Check if Stripe is configured
            if not stripe.api_key:
                raise Exception("Stripe is not configured")

            # Retrieve the checkout session
            checkout_session = stripe.checkout.Session.retrieve(session_id)

            if checkout_session.payment_status != 'paid':
                logger.warning(f"Checkout session {session_id} not paid")
                return False

            # Get metadata
            metadata = checkout_session.metadata
            plan_type = metadata.get('plan_type', 'trial')
            billing_cycle = metadata.get('billing_cycle', 'monthly')

            # Get or create Stripe customer
            customer_id = checkout_session.customer
            if not customer_id and checkout_session.customer_email:
                customers = stripe.Customer.list(email=checkout_session.customer_email)
                if customers.data:
                    customer_id = customers.data[0].id
                else:
                    customer = stripe.Customer.create(
                        email=checkout_session.customer_email,
                        metadata={'user_id': str(user_id)},
                    )
                    customer_id = customer.id

            # Get user
            result = await session.execute(
                select(Profile).where(Profile.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User {user_id} not found")
                return False

            # Get or create subscription
            result = await session.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = result.scalar_one_or_none()

            now = datetime.utcnow()

            if not subscription:
                subscription = Subscription(
                    user_id=user_id,
                    plan_type=plan_type,
                    billing_cycle=billing_cycle,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=checkout_session.subscription,
                    is_active=True,
                    subscription_start=now,
                )

                if plan_type == 'trial':
                    subscription.trial_start = now
                    subscription.trial_end = now + timedelta(days=settings.TRIAL_PERIOD_DAYS)
                    subscription.subscription_end = subscription.trial_end
                else:
                    subscription.subscription_end = now + timedelta(
                        days=365 if billing_cycle == 'yearly' else 30
                    )

                session.add(subscription)
            else:
                # Update existing subscription
                subscription.stripe_customer_id = customer_id
                subscription.stripe_subscription_id = checkout_session.subscription
                subscription.plan_type = plan_type
                subscription.billing_cycle = billing_cycle
                subscription.is_active = True
                subscription.subscription_start = now

                if plan_type == 'trial':
                    subscription.trial_start = now
                    subscription.trial_end = now + timedelta(days=settings.TRIAL_PERIOD_DAYS)
                    subscription.subscription_end = subscription.trial_end
                else:
                    subscription.subscription_end = now + timedelta(
                        days=365 if billing_cycle == 'yearly' else 30
                    )

            # Update user tier
            if plan_type == 'trial':
                user.subscription_tier = 'trial'
            else:
                user.subscription_tier = 'premium'

            # Record payment transaction
            amount = Decimal(checkout_session.amount_total or 0) / 100  # Convert from cents
            transaction = PaymentTransaction(
                user_id=user_id,
                subscription_id=subscription.id,
                transaction_id=checkout_session.payment_intent or checkout_session.id,
                amount=amount,
                currency=checkout_session.currency or 'usd',
                type='subscription',
                status='success',
                stripe_payment_intent_id=checkout_session.payment_intent,
                stripe_session_id=session_id,
            )
            session.add(transaction)

            await session.commit()
            logger.info(f"Successfully processed checkout for user {user_id}, plan: {plan_type}")
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error handling checkout complete: {e}")
            return False
        except Exception as e:
            logger.error(f"Error handling checkout complete: {e}")
            return False

    @staticmethod
    async def create_trial_subscription(
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        """Create a trial subscription directly (for demo/onboarding)."""
        try:
            # Get user
            result = await session.execute(
                select(Profile).where(Profile.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User {user_id} not found")
                return False

            # Check if already has active subscription
            result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.warning(f"User {user_id} already has active subscription")
                return False

            now = datetime.utcnow()
            trial_end = now + timedelta(days=settings.TRIAL_PERIOD_DAYS)

            subscription = Subscription(
                user_id=user_id,
                plan_type='trial',
                billing_cycle=None,
                is_active=True,
                subscription_start=now,
                subscription_end=trial_end,
                trial_start=now,
                trial_end=trial_end,
            )

            user.subscription_tier = 'trial'

            session.add(subscription)
            await session.commit()

            logger.info(f"Created trial subscription for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating trial subscription: {e}")
            return False

    @staticmethod
    async def handle_subscription_updated(
        stripe_subscription_id: str,
        session: AsyncSession,
    ) -> bool:
        """Handle Stripe subscription.updated webhook event."""
        try:
            if not stripe.api_key:
                logger.error("Stripe is not configured. Cannot retrieve subscription updates.")
                return False

            # Get subscription from Stripe
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)

            # Find subscription in database
            result = await session.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_subscription_id
                )
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.warning(f"Subscription {stripe_subscription_id} not found in database")
                return False

            # Update subscription
            if stripe_sub.status == 'active':
                subscription.is_active = True
                if stripe_sub.current_period_end:
                    subscription.subscription_end = datetime.fromtimestamp(
                        stripe_sub.current_period_end
                    )
            elif stripe_sub.status in ['canceled', 'past_due']:
                subscription.is_active = False

            await session.commit()
            logger.info(f"Updated subscription {stripe_subscription_id}")
            return True

        except Exception as e:
            logger.error(f"Error handling subscription updated: {e}")
            return False

    @staticmethod
    async def handle_subscription_deleted(
        stripe_subscription_id: str,
        session: AsyncSession,
    ) -> bool:
        """Handle Stripe subscription.deleted webhook event."""
        try:
            # Find subscription in database
            result = await session.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_subscription_id
                )
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.warning(f"Subscription {stripe_subscription_id} not found in database")
                return False

            # Deactivate subscription
            subscription.is_active = False
            subscription.subscription_end = datetime.utcnow()

            # Update user tier to free
            user = subscription.user
            user.subscription_tier = 'free'

            await session.commit()
            logger.info(f"Deleted subscription {stripe_subscription_id}")
            return True

        except Exception as e:
            logger.error(f"Error handling subscription deleted: {e}")
            return False

    @staticmethod
    async def get_user_subscription(
        user_id: str,
        session: AsyncSession,
    ) -> Optional[Dict[str, Any]]:
        """Get user's current subscription details."""
        try:
            result = await session.execute(
                select(Subscription).where(Subscription.user_id == user_id)
                .order_by(Subscription.created_at.desc())
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                return None

            now = datetime.utcnow()
            is_active = (
                subscription.is_active
                and subscription.subscription_end
                and subscription.subscription_end > now
            )

            return {
                'id': str(subscription.id),
                'plan_type': subscription.plan_type,
                'billing_cycle': subscription.billing_cycle,
                'is_active': is_active,
                'subscription_start': subscription.subscription_start.isoformat() if subscription.subscription_start else None,
                'subscription_end': subscription.subscription_end.isoformat() if subscription.subscription_end else None,
                'trial_start': subscription.trial_start.isoformat() if subscription.trial_start else None,
                'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None,
                'is_trial': subscription.plan_type == 'trial',
                'days_remaining': (
                    (subscription.subscription_end - now).days
                    if subscription.subscription_end and is_active
                    else 0
                ),
            }
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return None

    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        sig_header: str,
    ) -> Optional[Dict[str, Any]]:
        """Verify Stripe webhook signature and return event."""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
            return event
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return None
        except Exception as e:
            logger.error(f"Error verifying webhook: {e}")
            return None
