"""API initialization."""

from fastapi import APIRouter

from app.api.routes import search, products, reviews, utils, auth, profile, payments, price_alerts, chatbot, contact, admin, health, admin_crud

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(payments.router)
api_router.include_router(price_alerts.router)
api_router.include_router(search.router)
api_router.include_router(products.router)
api_router.include_router(reviews.router)
api_router.include_router(utils.router)
api_router.include_router(chatbot.router)
api_router.include_router(contact.router)
api_router.include_router(admin.router)
api_router.include_router(health.router)
api_router.include_router(admin_crud.router)

__all__ = ["api_router"]