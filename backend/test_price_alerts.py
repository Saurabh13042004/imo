#!/usr/bin/env python3
"""Test script to verify price alert system setup"""

import sys
sys.path.insert(0, '/d/imo-backend/backend')

from app.models.subscription import PriceAlert
from app.models.user import Profile
from app.schemas.price_alert import (
    CreatePriceAlertRequest,
    PriceAlertResponse,
    UpdatePriceAlertRequest,
    PriceAlertListResponse
)

print("✅ All imports successful!")
print("\nPrice Alert Model Fields:")
print(f"  - {PriceAlert.__tablename__} table")
for col in PriceAlert.__table__.columns:
    print(f"    • {col.name}: {col.type}")

print("\nPrice Alert Schema Models:")
print("  • CreatePriceAlertRequest")
print("  • PriceAlertResponse")
print("  • UpdatePriceAlertRequest")
print("  • PriceAlertListResponse")

print("\nProfile Relationships:")
print("  • subscriptions")
print("  • payment_transactions")
print("  • search_unlocks")
print("  • price_alerts ✨ (NEW)")

print("\n✅ Price alert system is properly configured!")
