"""Service for managing search limits for free users."""
import logging
from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import DailySearchUsage, Subscription
from app.models.user import Profile

logger = logging.getLogger(__name__)

# Search limits
GUEST_USER_SEARCH_LIMIT = 1  # 1 free search for non-registered users
GUEST_USER_RESULT_LIMIT = 10  # 10 products per search for guests
FREE_REGISTERED_USER_DAILY_LIMIT = 3  # 3 free searches per day for registered users
FREE_REGISTERED_USER_RESULT_LIMIT = 10  # 10 products per search for free registered users


class SearchLimitService:
    """Service for checking and updating search limits."""

    @staticmethod
    async def check_search_access(
        db: AsyncSession,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> tuple[bool, int, str]:
        """
        Check if user has search access.
        
        Returns:
            tuple: (has_access, remaining_searches, message)
        """
        try:
            # Check if user has active premium/trial subscription
            if user_id:
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.user_id == user_id,
                        Subscription.is_active == True,
                        Subscription.plan_type.in_(['premium', 'trial'])
                    )
                )
                subscription = result.scalar_one_or_none()
                
                if subscription:
                    return True, -1, "Unlimited searches (Premium/Trial)"

            # Get today's date
            today = date.today()

            # For registered users (with user_id)
            if user_id:
                # Check daily usage
                result = await db.execute(
                    select(DailySearchUsage).where(
                        DailySearchUsage.user_id == user_id,
                        DailySearchUsage.search_date == today
                    )
                )
                usage = result.scalar_one_or_none()

                if usage:
                    remaining = FREE_REGISTERED_USER_DAILY_LIMIT - usage.search_count
                    if remaining > 0:
                        return True, remaining, f"{remaining} searches remaining today"
                    else:
                        return False, 0, "Daily search limit reached (3/3). Upgrade to Premium for unlimited searches."
                else:
                    # No usage record yet, user has full limit
                    return True, FREE_REGISTERED_USER_DAILY_LIMIT, f"{FREE_REGISTERED_USER_DAILY_LIMIT} searches available today"

            # For guest users (with session_id)
            elif session_id:
                result = await db.execute(
                    select(DailySearchUsage).where(
                        DailySearchUsage.session_id == session_id,
                        DailySearchUsage.search_date == today
                    )
                )
                usage = result.scalar_one_or_none()

                if usage:
                    remaining = GUEST_USER_SEARCH_LIMIT - usage.search_count
                    if remaining > 0:
                        return True, remaining, "1 free search for guest users"
                    else:
                        return False, 0, "Search limit reached. Sign up for 3 free searches daily!"
                else:
                    # No usage record yet
                    return True, GUEST_USER_SEARCH_LIMIT, "1 free search for guest users"

            # No user_id or session_id provided - allow 1 free search for first-time guests
            # This handles cases where frontend hasn't generated a session ID yet
            logger.info("No user_id or session_id provided - allowing 1 free search for guest")
            return True, GUEST_USER_SEARCH_LIMIT, "1 free search for guest users"

        except Exception as e:
            logger.error(f"Error checking search access: {e}", exc_info=True)
            # On error, allow access (fail open)
            return True, -1, "Access granted (error bypass)"

    @staticmethod
    async def increment_search_count(
        db: AsyncSession,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Increment search count for user/session.
        
        Returns:
            bool: True if successful
        """
        try:
            today = date.today()

            if user_id:
                # Check for existing record
                result = await db.execute(
                    select(DailySearchUsage).where(
                        DailySearchUsage.user_id == user_id,
                        DailySearchUsage.search_date == today
                    )
                )
                usage = result.scalar_one_or_none()

                if usage:
                    # Increment existing record
                    usage.search_count += 1
                else:
                    # Create new record
                    usage = DailySearchUsage(
                        user_id=user_id,
                        session_id=None,
                        search_date=today,
                        search_count=1
                    )
                    db.add(usage)

            elif session_id:
                # Check for existing record
                result = await db.execute(
                    select(DailySearchUsage).where(
                        DailySearchUsage.session_id == session_id,
                        DailySearchUsage.search_date == today
                    )
                )
                usage = result.scalar_one_or_none()

                if usage:
                    # Increment existing record
                    usage.search_count += 1
                else:
                    # Create new record
                    usage = DailySearchUsage(
                        user_id=None,
                        session_id=session_id,
                        search_date=today,
                        search_count=1
                    )
                    db.add(usage)

            await db.commit()
            return True

        except Exception as e:
            logger.error(f"Error incrementing search count: {e}", exc_info=True)
            await db.rollback()
            return False

    @staticmethod
    def get_result_limit(
        is_premium: bool = False,
        is_registered: bool = False
    ) -> int:
        """
        Get the maximum number of results to return based on user type.
        
        Args:
            is_premium: Whether user has premium/trial subscription
            is_registered: Whether user is registered (has account)
            
        Returns:
            int: Maximum number of results to return (-1 for unlimited)
        """
        if is_premium:
            return -1  # Unlimited for premium users
        elif is_registered:
            return FREE_REGISTERED_USER_RESULT_LIMIT  # 10 results for free registered
        else:
            return GUEST_USER_RESULT_LIMIT  # 10 results for guests
