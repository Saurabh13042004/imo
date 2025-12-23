"""API initialization."""

from fastapi import APIRouter

from app.api.routes import search, products, reviews, utils, auth, profile

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(search.router)
api_router.include_router(products.router)
api_router.include_router(reviews.router)
api_router.include_router(utils.router)

__all__ = ["api_router"]
