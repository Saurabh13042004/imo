"""Initialize integrations."""

__all__ = [
    "AmazonClient",
    "WalmartClient",
    "GoogleShoppingClient",
    "YouTubeClient",
    "RedditClient",
    "ForumClient",
]

from app.integrations.amazon import AmazonClient
from app.integrations.walmart import WalmartClient
from app.integrations.google_shopping import GoogleShoppingClient
from app.integrations.youtube import YouTubeClient
from app.integrations.reddit import RedditClient
from app.integrations.forums import ForumClient
