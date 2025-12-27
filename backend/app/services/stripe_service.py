"""Stripe payment service for handling subscriptions and payments."""
import logging
from datetime import datetime, timedelta, timezone
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
    async def get_transaction_details(
        payment_intent_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Fetch transaction details from Stripe.
        
        Returns transaction status, amount, and other details.
        """
        try:
            if not stripe.api_key:
                logger.warning("Stripe not configured")
                return None
            
            if payment_intent_id:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                return {
                    'id': intent.id,
                    'status': intent.status,  # 'succeeded', 'processing', 'requires_action', 'requires_payment_method', 'canceled'
                    'amount': intent.amount / 100,
                    'currency': intent.currency.upper(),
                    'created': datetime.fromtimestamp(intent.created, tz=timezone.utc),
                    'last_payment_error': intent.last_payment_error,
                }
            elif session_id:
                checkout_session = stripe.checkout.Session.retrieve(session_id)
                return {
                    'id': checkout_session.id,
                    'status': checkout_session.payment_status,  # 'paid', 'unpaid', 'no_payment_required'
                    'amount': checkout_session.amount_total / 100 if checkout_session.amount_total else 0,
                    'currency': checkout_session.currency.upper(),
                    'created': datetime.fromtimestamp(checkout_session.created, tz=timezone.utc),
                    'payment_intent_id': checkout_session.payment_intent,
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching transaction details: {e}")
            return None

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
            # Check if user already has an active subscription
            result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                ).order_by(Subscription.created_at.desc())
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                now = datetime.now(timezone.utc)
                if existing.subscription_end and existing.subscription_end > now:
                    logger.warning(f"User {user_id} already has active {existing.plan_type} subscription until {existing.subscription_end}")
                    raise Exception(f"You already have an active {existing.plan_type} subscription. Please cancel it first or wait for it to expire.")
            
            # Check if Stripe is configured
            if not stripe.api_key:
                raise Exception(
                    "Stripe is not configured. Please set STRIPE_SECRET_KEY in environment variables. "
                    "Get your key from https://dashboard.stripe.com/apikeys"
                )
            # Determine pricing
            # For trial: Create subscription with trial period, then charge monthly after trial
            if plan_type == 'trial':
                billing_cycle = 'monthly'  # After trial, convert to monthly
            
            # Set price based on billing cycle
            if billing_cycle == 'yearly':
                price = settings.PREMIUM_YEARLY_PRICE
                interval = 'year'
            else:  # monthly
                price = settings.PREMIUM_MONTHLY_PRICE
                interval = 'month'

            price_data = {
                'currency': 'usd',
                'product_data': {
                    'name': f'IMO Premium - {"Free Trial + " if plan_type == "trial" else ""}{billing_cycle.capitalize()}',
                    'description': f'{"7-day free trial, then " if plan_type == "trial" else ""}Unlimited product searches and AI analysis',
                },
                'unit_amount': price,
                'recurring': {
                    'interval': interval,
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
            
            checkout_params = {
                'payment_method_types': ['card'],
                'customer_email': email,
                'line_items': line_items,
                'mode': 'subscription',
                'success_url': success_url,
                'cancel_url': cancel_url,
                'metadata': {
                    'user_id': str(user_id),
                    'plan_type': plan_type,
                    'billing_cycle': billing_cycle,
                },
                'allow_promotion_codes': True,
            }
            
            # Add trial period if this is a trial signup
            if plan_type == 'trial':
                checkout_params['subscription_data'] = {
                    'trial_period_days': settings.TRIAL_PERIOD_DAYS,
                    'metadata': {
                        'is_trial': 'true',
                        'user_id': str(user_id),
                    }
                }
            
            checkout_session = stripe.checkout.Session.create(**checkout_params)

            logger.info(f"Created Stripe checkout session {checkout_session.id} for user {user_id}")
            return {
                'session_id': checkout_session.id,
                'url': checkout_session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise Exception(f"Payment setup failed: {str(e)}")

    @staticmethod
    async def create_or_update_payment_transaction(
        user_id: str,
        subscription_id: Optional[str],
        transaction_id: str,
        amount: Decimal,
        currency: str,
        txn_type: str,
        status: str,
        stripe_payment_intent_id: Optional[str] = None,
        stripe_session_id: Optional[str] = None,
        metadata_json: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> PaymentTransaction:
        """Create or update a payment transaction record. 
        
        Transaction lifecycle:
        - 'pending': When checkout session is created
        - 'success': When payment is successfully completed
        - 'failed': When payment fails
        - 'refunded': When refund is issued
        """
        try:
            if not db_session:
                raise ValueError("Database session required")
            
            # Check if transaction already exists
            result = await db_session.execute(
                select(PaymentTransaction).where(
                    PaymentTransaction.transaction_id == transaction_id
                )
            )
            existing_transaction = result.scalar_one_or_none()
            
            if existing_transaction:
                # Update existing transaction status
                existing_transaction.status = status
                existing_transaction.updated_at = datetime.now(timezone.utc)
                logger.info(f"Updated payment transaction {transaction_id} status to {status}")
                await db_session.flush()
                return existing_transaction
            else:
                # Create new transaction
                transaction = PaymentTransaction(
                    user_id=user_id,
                    subscription_id=subscription_id,
                    transaction_id=transaction_id,
                    amount=amount,
                    currency=currency,
                    type=txn_type,
                    status=status,
                    stripe_payment_intent_id=stripe_payment_intent_id,
                    stripe_session_id=stripe_session_id,
                    metadata_json=metadata_json,
                )
                db_session.add(transaction)
                logger.info(f"Created new payment transaction {transaction_id} with status {status}")
                await db_session.flush()
                return transaction
        except Exception as e:
            logger.error(f"Error creating/updating payment transaction: {e}")
            raise

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
            plan_type = metadata.get('plan_type', 'premium')
            billing_cycle = metadata.get('billing_cycle', 'monthly')
            
            # Check if subscription has trial from Stripe subscription object
            stripe_subscription = None
            if checkout_session.subscription:
                stripe_subscription = stripe.Subscription.retrieve(checkout_session.subscription)
                # If subscription has trial, update plan_type
                if stripe_subscription.trial_end:
                    plan_type = 'trial'
                    logger.info(f"Subscription has trial period until {stripe_subscription.trial_end}")

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

            now = datetime.now(timezone.utc)

            if not subscription:
                # Use Stripe subscription dates if available
                if stripe_subscription:
                    # For subscriptions, use start_date and billing_cycle_anchor
                    subscription_start = datetime.fromtimestamp(stripe_subscription.start_date, tz=timezone.utc)
                    
                    # If trial exists, subscription_end is trial_end, otherwise billing_cycle_anchor
                    if stripe_subscription.trial_end:
                        subscription_end = datetime.fromtimestamp(stripe_subscription.trial_end, tz=timezone.utc)
                    else:
                        subscription_end = datetime.fromtimestamp(stripe_subscription.billing_cycle_anchor, tz=timezone.utc)
                    
                    subscription = Subscription(
                        user_id=user_id,
                        plan_type=plan_type,
                        billing_cycle=billing_cycle,
                        stripe_customer_id=customer_id,
                        stripe_subscription_id=checkout_session.subscription,
                        is_active=True,
                        subscription_start=subscription_start,
                        subscription_end=subscription_end,
                    )
                    
                    # Set trial dates if trial exists
                    if stripe_subscription.trial_end:
                        subscription.trial_start = subscription_start
                        subscription.trial_end = datetime.fromtimestamp(stripe_subscription.trial_end, tz=timezone.utc)
                else:
                    # Fallback if no Stripe subscription data
                    subscription = Subscription(
                        user_id=user_id,
                        plan_type=plan_type,
                        billing_cycle=billing_cycle,
                        stripe_customer_id=customer_id,
                        stripe_subscription_id=checkout_session.subscription,
                        is_active=True,
                        subscription_start=now,
                        subscription_end=now + timedelta(days=365 if billing_cycle == 'yearly' else 30),
                    )

                session.add(subscription)
            else:
                # Update existing subscription
                subscription.stripe_customer_id = customer_id
                subscription.stripe_subscription_id = checkout_session.subscription
                subscription.plan_type = plan_type
                subscription.billing_cycle = billing_cycle
                subscription.is_active = True
                
                # Use Stripe subscription dates if available
                if stripe_subscription:
                    subscription.subscription_start = datetime.fromtimestamp(stripe_subscription.start_date, tz=timezone.utc)
                    
                    # If trial exists, subscription_end is trial_end, otherwise billing_cycle_anchor
                    if stripe_subscription.trial_end:
                        subscription.subscription_end = datetime.fromtimestamp(stripe_subscription.trial_end, tz=timezone.utc)
                    else:
                        subscription.subscription_end = datetime.fromtimestamp(stripe_subscription.billing_cycle_anchor, tz=timezone.utc)
                    
                    # Set trial dates if trial exists
                    if stripe_subscription.trial_end:
                        subscription.trial_start = subscription.subscription_start
                        subscription.trial_end = datetime.fromtimestamp(stripe_subscription.trial_end, tz=timezone.utc)
                else:
                    subscription.subscription_start = now
                    subscription.subscription_end = now + timedelta(days=365 if billing_cycle == 'yearly' else 30)

            # Update user tier
            if plan_type == 'trial':
                user.subscription_tier = 'trial'
            else:
                user.subscription_tier = 'premium'

            # Record payment transaction (idempotent - check if already exists)
            transaction_id = checkout_session.payment_intent or checkout_session.id
            amount = Decimal(checkout_session.amount_total or 0) / 100  # Convert from cents
            
            await StripeService.create_or_update_payment_transaction(
                user_id=user_id,
                subscription_id=subscription.id,
                transaction_id=transaction_id,
                amount=amount,
                currency=checkout_session.currency or 'usd',
                txn_type='subscription',
                status='success',
                stripe_payment_intent_id=checkout_session.payment_intent,
                stripe_session_id=session_id,
                db_session=session,
            )

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

            # Check if already has active subscription that hasn't expired
            result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                ).order_by(Subscription.created_at.desc())
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Check if subscription has actually expired
                now = datetime.now(timezone.utc)
                logger.info(f"Found existing subscription for user {user_id}: plan_type={existing.plan_type}, is_active={existing.is_active}, end={existing.subscription_end}, now={now}")
                if existing.subscription_end and existing.subscription_end > now:
                    logger.warning(f"User {user_id} already has active subscription until {existing.subscription_end}")
                    raise Exception("You already have an active subscription. Cancel it before starting a trial.")
                else:
                    # Subscription has expired, mark it as inactive
                    existing.is_active = False
                    await session.flush()
                    logger.info(f"Marked expired subscription for user {user_id} as inactive")

            now = datetime.now(timezone.utc)
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
            subscription.subscription_end = datetime.now(timezone.utc)

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
            logger.info(f"Fetching subscription for user_id: {user_id}")
            result = await session.execute(
                select(Subscription).where(Subscription.user_id == user_id)
                .order_by(Subscription.created_at.desc())
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.warning(f"No subscription found for user_id: {user_id}")
                return None

            logger.info(f"Found subscription: plan_type={subscription.plan_type}, is_active={subscription.is_active}, stripe_subscription_id={subscription.stripe_subscription_id}")

            now = datetime.now(timezone.utc)
            is_active = (
                subscription.is_active
                and subscription.subscription_end
                and subscription.subscription_end > now
            )

            subscription_data = {
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
                'cancel_at_period_end': False,
                'status': 'active' if is_active else 'inactive',
                'current_period_end': subscription.subscription_end.isoformat() if subscription.subscription_end else None,
                'payment_method': None,
            }

            # Fetch payment method from Stripe if subscription has a Stripe subscription ID
            if subscription.stripe_subscription_id and stripe.api_key:
                try:
                    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    subscription_data['cancel_at_period_end'] = stripe_sub.cancel_at_period_end
                    subscription_data['status'] = stripe_sub.status
                    
                    # Get trial dates from Stripe if missing in database
                    if stripe_sub.trial_start and not subscription.trial_start:
                        subscription_data['trial_start'] = datetime.fromtimestamp(stripe_sub.trial_start, tz=timezone.utc).isoformat()
                    
                    if stripe_sub.trial_end and not subscription.trial_end:
                        subscription_data['trial_end'] = datetime.fromtimestamp(stripe_sub.trial_end, tz=timezone.utc).isoformat()
                    
                    # Update current_period_end from Stripe
                    if stripe_sub.current_period_end:
                        subscription_data['current_period_end'] = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc).isoformat()
                    
                    # Get payment method details
                    if stripe_sub.default_payment_method:
                        payment_method = stripe.PaymentMethod.retrieve(stripe_sub.default_payment_method)
                        if payment_method.card:
                            subscription_data['payment_method'] = {
                                'brand': payment_method.card.brand,
                                'last4': payment_method.card.last4,
                                'exp_month': payment_method.card.exp_month,
                                'exp_year': payment_method.card.exp_year,
                            }
                except Exception as e:
                    logger.warning(f"Could not fetch Stripe subscription details: {e}")

            logger.info(f"Returning subscription_data: {subscription_data}")
            return subscription_data
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return None

    @staticmethod
    async def create_billing_portal_session(
        user_id: str,
        session: AsyncSession,
        return_url: str,
    ) -> Dict[str, Any]:
        """Create a Stripe billing portal session for managing subscription."""
        try:
            # Get user's subscription to find Stripe customer ID
            result = await session.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id
                ).order_by(Subscription.created_at.desc())
            )
            subscription = result.scalar_one_or_none()

            if not subscription or not subscription.stripe_customer_id:
                raise Exception("No active subscription found. Please subscribe first.")

            # Check if Stripe is configured
            if not stripe.api_key:
                raise Exception("Stripe is not configured properly.")

            # Create billing portal session
            portal_session = stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=return_url,
            )

            return {
                'url': portal_session.url,
                'session_id': portal_session.id,
            }
        except Exception as e:
            logger.error(f"Error creating billing portal session: {e}")
            raise

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
