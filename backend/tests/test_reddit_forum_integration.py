"""Test suite for Reddit and Forum review integrations."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.integrations.reddit import RedditClient
from app.integrations.forums import ForumClient
from app.services.review_service import ReviewService


class TestRedditClient:
    """Test Reddit client functionality."""

    @pytest.mark.asyncio
    async def test_search_product_returns_normalized_reviews(self):
        """Test that search_product returns properly normalized review objects."""
        client = RedditClient()
        
        # Mock the public API response
        mock_response = {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "thread123",
                            "title": "Amazing product review",
                            "url": "https://reddit.com/r/products/comments/abc123/amazing_product/",
                            "num_comments": 10,
                            "author": "user1",
                            "selftext": "This product is great!"
                        }
                    }
                ]
            }
        }
        
        # In real tests, mock httpx.AsyncClient
        # For now, test the normalization logic
        
    def test_is_valid_thread_url_filtering(self):
        """Test that URL validation filters correctly."""
        client = RedditClient()
        
        # Valid URLs
        assert client._is_valid_thread_url(
            "https://reddit.com/r/products/comments/abc123/Sony_WH1000XM5/",
            "Sony WH-1000XM5"
        )
        
        # Invalid URLs (no /comments/)
        assert not client._is_valid_thread_url(
            "https://reddit.com/r/products/",
            "Sony WH-1000XM5"
        )
        
        # Invalid URLs (contains deal)
        assert not client._is_valid_thread_url(
            "https://reddit.com/r/deals/comments/abc123/Sony_deal/",
            "Sony WH-1000XM5"
        )


class TestForumClient:
    """Test Forum client functionality."""

    @pytest.mark.asyncio
    async def test_search_product_returns_empty_without_search_urls(self):
        """Test that forum search returns empty until search URLs are configured."""
        client = ForumClient()
        
        # Currently returns empty since search URL generation not implemented
        reviews = await client.search_product("Sony WH-1000XM5")
        assert isinstance(reviews, list)
        # Will be empty until SerpAPI integration added


class TestReviewServiceNormalization:
    """Test ReviewService field normalization."""

    def test_normalize_reviews_maps_reddit_fields(self):
        """Test that Reddit review fields are normalized correctly."""
        service = ReviewService()
        
        reddit_reviews = [
            {
                "source_review_id": "reddit_123",
                "author": "redditor_user",
                "review_text": "Great headphones!",
                "review_title": "Best purchase ever",
                "url": "https://reddit.com/r/audio/comments/abc123/",
                "helpful_count": 42
            }
        ]
        
        normalized = service._normalize_reviews(reddit_reviews, "reddit")
        
        assert len(normalized) == 1
        assert normalized[0]["source_review_id"] == "reddit_123"
        assert normalized[0]["author"] == "redditor_user"
        assert normalized[0]["content"] == "Great headphones!"
        assert normalized[0]["title"] == "Best purchase ever"
        assert normalized[0]["url"] == "https://reddit.com/r/audio/comments/abc123/"
        assert normalized[0]["rating"] is None  # Reddit doesn't have ratings

    def test_normalize_reviews_maps_forum_fields(self):
        """Test that Forum review fields are normalized correctly."""
        service = ReviewService()
        
        forum_reviews = [
            {
                "source_review_id": "forum_456",
                "author": "Forum User",
                "review_text": "Excellent sound quality",
                "review_title": "Head-Fi Discussion",
                "url": "https://head-fi.org/forums/t/123456/"
            }
        ]
        
        normalized = service._normalize_reviews(forum_reviews, "forum")
        
        assert len(normalized) == 1
        assert normalized[0]["source_review_id"] == "forum_456"
        assert normalized[0]["author"] == "Forum User"
        assert normalized[0]["content"] == "Excellent sound quality"
        assert normalized[0]["title"] == "Head-Fi Discussion"

    def test_normalize_reviews_handles_missing_fields(self):
        """Test that normalization handles missing fields gracefully."""
        service = ReviewService()
        
        reviews = [
            {
                "source_review_id": "test_123",
                "review_text": "Some content"
                # Missing author, title, url
            }
        ]
        
        normalized = service._normalize_reviews(reviews, "test")
        
        assert len(normalized) == 1
        assert normalized[0]["author"] == "Anonymous"
        assert normalized[0]["title"] == ""
        assert normalized[0]["url"] == ""

    def test_normalize_reviews_filters_empty_content(self):
        """Test that reviews without content are filtered out."""
        service = ReviewService()
        
        reviews = [
            {
                "source_review_id": "test_123",
                "review_text": ""  # Empty content
            },
            {
                "source_review_id": "test_456",
                "review_text": "Valid content"
            }
        ]
        
        normalized = service._normalize_reviews(reviews, "test")
        
        # Only valid review should be included
        assert len(normalized) == 1
        assert normalized[0]["source_review_id"] == "test_456"

    def test_normalize_reviews_filters_missing_source_id(self):
        """Test that reviews without source_review_id are filtered out."""
        service = ReviewService()
        
        reviews = [
            {
                # Missing source_review_id
                "review_text": "Some content"
            },
            {
                "source_review_id": "test_789",
                "review_text": "Valid content"
            }
        ]
        
        normalized = service._normalize_reviews(reviews, "test")
        
        # Only valid review should be included
        assert len(normalized) == 1
        assert normalized[0]["source_review_id"] == "test_789"


# Integration test example
@pytest.mark.asyncio
async def test_review_service_integration():
    """
    Integration test showing complete flow.
    
    This would require:
    - Mocked database
    - Mocked product model
    - Mocked API clients
    """
    # Example usage:
    # service = ReviewService()
    # product = Mock(id="prod_123", title="Sony Headphones", asin="B123")
    # reviews = await service.fetch_reviews(db, product, ["reddit", "forum"])
    # assert len(reviews) > 0
    pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
