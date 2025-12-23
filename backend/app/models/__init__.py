"""Database models."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Existing models
from app.models.product import Product
from app.models.review import Review
from app.models.video import Video
from app.models.search_cache import SearchCache
from app.models.short_video_review import ShortVideoReview

# User and auth models
from app.models.user import Profile, UserRole

# Subscription and payment models
from app.models.subscription import Subscription, PaymentTransaction, SearchUnlock, DailySearchUsage, PriceAlert

# Analytics and logging models
from app.models.analytics import AnalyticsEvent, ErrorLog, UsageLog, UserInteraction, SubscriptionEvent

# Affiliate and tracking models
from app.models.affiliate import AffiliateClick

# Product meta models
from app.models.product_meta import PriceComparison, ProductLike

# Configuration models
from app.models.config import AppConfig

# Background task models
from app.models.task import BackgroundAnalysisTask

# User content models
from app.models.user_content import UserReview, Like, Comment, ProductReview

__all__ = [
    "Base",
    # Existing
    "Product",
    "Review",
    "Video",
    "SearchCache",
    "ShortVideoReview",
    # Users
    "Profile",
    "UserRole",
    # Subscriptions
    "Subscription",
    "PaymentTransaction",
    "SearchUnlock",
    "DailySearchUsage",
    "PriceAlert",
    # Analytics
    "AnalyticsEvent",
    "ErrorLog",
    "UsageLog",
    "UserInteraction",
    "SubscriptionEvent",
    # Affiliate
    "AffiliateClick",
    # Product Meta
    "PriceComparison",
    "ProductLike",
    # Config
    "AppConfig",
    # Tasks
    "BackgroundAnalysisTask",
    # User Content
    "UserReview",
    "Like",
    "Comment",
    "ProductReview",
]
