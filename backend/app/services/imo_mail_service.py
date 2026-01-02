"""Service for sending IMO-branded emails to users."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.mail_service import send_templated_email
from app.config import settings

logger = logging.getLogger(__name__)


class IMOMailService:
    """Service for sending IMO-branded templated emails."""

    @staticmethod
    async def send_new_user_onboarding_email(
        db: AsyncSession,
        user_email: str,
        user_name: str,
        has_trial: bool = True,
        trial_days: int = 7
    ) -> bool:
        """
        Send welcome email to new user after signup.
        
        Args:
            db: Database session
            user_email: User's email address
            user_name: User's full name
            has_trial: Whether user has trial
            trial_days: Number of trial days
            
        Returns:
            bool: True if email sent successfully
        """
        context = {
            "user_name": user_name,
            "user_email": user_email,
            "has_trial": has_trial,
            "trial_days": trial_days,
            "signup_date": datetime.utcnow().strftime("%B %d, %Y"),
            "current_year": datetime.utcnow().year,
            "dashboard_url": settings.FRONTEND_URL,
            "pricing_url": f"{settings.FRONTEND_URL}/pricing",
        }
        
        try:
            success = await send_templated_email(
                db=db,
                template_name="imo_new_user_onboarding",
                recipients=[user_email],
                context=context
            )
            
            if success:
                logger.info(f"New user onboarding email sent to {user_email}")
            else:
                logger.error(f"Failed to send new user onboarding email to {user_email}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending new user onboarding email: {e}", exc_info=True)
            return False

    @staticmethod
    async def send_payment_success_email(
        db: AsyncSession,
        user_email: str,
        user_name: str,
        transaction_id: str,
        amount: str,
        plan_type: str = "Premium Unlimited",
        payment_date: Optional[str] = None,
        next_billing_date: Optional[str] = None
    ) -> bool:
        """
        Send payment success email to user after successful subscription.
        
        Args:
            db: Database session
            user_email: User's email address
            user_name: User's full name
            transaction_id: Payment transaction ID
            amount: Amount charged (e.g., "$9.99")
            plan_type: Type of plan purchased
            payment_date: Date of payment
            next_billing_date: Next billing date
            
        Returns:
            bool: True if email sent successfully
        """
        if not payment_date:
            payment_date = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p")
        
        if not next_billing_date:
            next_date = datetime.utcnow() + timedelta(days=30)
            next_billing_date = next_date.strftime("%B %d, %Y")
        
        context = {
            "user_name": user_name,
            "user_email": user_email,
            "transaction_id": transaction_id,
            "amount": amount,
            "plan_type": plan_type,
            "payment_date": payment_date,
            "next_billing_date": next_billing_date,
            "current_year": datetime.utcnow().year,
            "dashboard_url": settings.FRONTEND_URL,
        }
        
        try:
            success = await send_templated_email(
                db=db,
                template_name="imo_payment_success",
                recipients=[user_email],
                context=context
            )
            
            if success:
                logger.info(f"Payment success email sent to {user_email}")
            else:
                logger.error(f"Failed to send payment success email to {user_email}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending payment success email: {e}", exc_info=True)
            return False

    @staticmethod
    async def send_payment_cancelled_email(
        db: AsyncSession,
        user_email: str,
        user_name: str,
        transaction_id: str,
        amount: str = "$9.99",
        plan_type: str = "Premium Unlimited",
        cancellation_date: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Send payment cancelled email to user.
        
        Args:
            db: Database session
            user_email: User's email address
            user_name: User's full name
            transaction_id: Payment transaction ID
            amount: Amount that was attempted (e.g., "$9.99")
            plan_type: Type of plan that was attempted
            cancellation_date: Date payment was cancelled
            reason: Reason for cancellation (optional)
            
        Returns:
            bool: True if email sent successfully
        """
        if not cancellation_date:
            cancellation_date = datetime.utcnow().strftime("%B %d, %Y at %I:%M %p")
        
        context = {
            "user_name": user_name,
            "user_email": user_email,
            "transaction_id": transaction_id,
            "amount": amount,
            "plan_type": plan_type,
            "cancellation_date": cancellation_date,
            "reason": reason or "Not specified",
            "current_year": datetime.utcnow().year,
            "upgrade_url": f"{settings.FRONTEND_URL}/pricing",
            "pricing_url": f"{settings.FRONTEND_URL}/pricing",
        }
        
        try:
            success = await send_templated_email(
                db=db,
                template_name="imo_payment_cancelled",
                recipients=[user_email],
                context=context
            )
            
            if success:
                logger.info(f"Payment cancelled email sent to {user_email}")
            else:
                logger.error(f"Failed to send payment cancelled email to {user_email}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending payment cancelled email: {e}", exc_info=True)
            return False

    @staticmethod
    async def send_bulk_email(
        db: AsyncSession,
        template_name: str,
        recipient_emails: list[str],
        context_dict: dict
    ) -> bool:
        """
        Send bulk email using a template.
        
        Args:
            db: Database session
            template_name: Name of template to use
            recipient_emails: List of recipient email addresses
            context_dict: Dictionary of template variables
            
        Returns:
            bool: True if all emails sent successfully
        """
        try:
            success = await send_templated_email(
                db=db,
                template_name=template_name,
                recipients=recipient_emails,
                context=context_dict
            )
            
            if success:
                logger.info(f"Bulk email sent to {len(recipient_emails)} recipients using template: {template_name}")
            else:
                logger.error(f"Failed to send bulk email using template: {template_name}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending bulk email: {e}", exc_info=True)
            return False

    @staticmethod
    async def send_price_alert_email(
        db: AsyncSession,
        user_email: str,
        user_name: str,
        product_name: str,
        current_price: str,
        target_price: str,
        product_id: str = "N/A",
        savings_amount: Optional[str] = None
    ) -> bool:
        """
        Send price alert confirmation email when user creates a price alert.
        
        Args:
            db: Database session
            user_email: User's email address
            user_name: User's full name
            product_name: Name of the product
            current_price: Current product price (e.g., "$199.99")
            target_price: Target price the user wants to wait for
            product_id: Product ID (optional)
            savings_amount: Amount user will save (optional, e.g., "$50.00")
            
        Returns:
            bool: True if email sent successfully
        """
        context = {
            "user_name": user_name,
            "user_email": user_email,
            "product_name": product_name,
            "current_price": current_price,
            "target_price": target_price,
            "product_id": product_id,
            "savings_amount": savings_amount,
            "created_at": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"),
            "current_year": datetime.utcnow().year,
            "dashboard_url": settings.FRONTEND_URL,
        }
        
        try:
            success = await send_templated_email(
                db=db,
                template_name="imo_price_alert",
                recipients=[user_email],
                context=context
            )
            
            if success:
                logger.info(f"Price alert email sent to {user_email} for product: {product_name}")
            else:
                logger.error(f"Failed to send price alert email to {user_email}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending price alert email: {e}", exc_info=True)
            return False
    @staticmethod
    async def send_password_reset_email(
        db: AsyncSession,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email to user.
        
        Args:
            db: Database session
            user_email: User's email address
            user_name: User's full name
            reset_token: Password reset token
            
        Returns:
            bool: True if email sent successfully
        """
        # Build reset URL - user will click this link to reset password
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            "user_name": user_name,
            "user_email": user_email,
            "reset_link": reset_link,
            "reset_token": reset_token,
            "expiration_hours": 24,
            "current_year": datetime.utcnow().year,
            "dashboard_url": settings.FRONTEND_URL,
        }
        
        try:
            success = await send_templated_email(
                db=db,
                template_name="imo_password_reset",
                recipients=[user_email],
                context=context
            )
            
            if success:
                logger.info(f"Password reset email sent to {user_email}")
            else:
                logger.error(f"Failed to send password reset email to {user_email}")
                
            return success
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}", exc_info=True)
            return False