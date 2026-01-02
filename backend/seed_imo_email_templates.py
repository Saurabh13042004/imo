"""Seeder script to populate IMO email templates into the database."""

import asyncio
import logging
from pathlib import Path
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.email_template import EmailTemplate
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Template definitions
TEMPLATES = [
    {
        "name": "imo_new_user_onboarding",
        "subject": "Welcome to IMO - AI That Reads Every Review! 🎯",
        "description": "Sent to new users after signup. Includes trial activation and feature overview.",
        "file": "imo_new_user_onboarding.html"
    },
    {
        "name": "imo_payment_success",
        "subject": "Payment Successful! Welcome to IMO Premium ✓",
        "description": "Sent after successful payment. Includes receipt and premium features list.",
        "file": "imo_payment_success.html"
    },
    {
        "name": "imo_payment_cancelled",
        "subject": "Payment Cancelled - No Charges ⚠️",
        "description": "Sent when payment is cancelled. Reassures user and offers retry option.",
        "file": "imo_payment_cancelled.html"
    },
    {
        "name": "imo_price_alert",
        "subject": "Price Alert Set! 🔔 We'll Monitor {{ product_name }} For You",
        "description": "Sent when user creates a price alert. Includes product, current price, and target price.",
        "file": "imo_price_alert.html"
    },
    {
        "name": "imo_password_reset",
        "subject": "Reset Your IMO Password",
        "description": "Sent when user requests password reset. Includes reset link valid for 24 hours.",
        "file": "imo_password_reset.html"
    }
]

# Plain text versions of templates
TEMPLATE_TEXT_VERSIONS = {
    "imo_new_user_onboarding": """Welcome to IMO!

Hello {{ user_name }}!

We're thrilled to have you join IMO! Your account is ready to help you make smarter shopping decisions in seconds, not hours.

{{ trial_days }}-DAY FREE TRIAL ACTIVATED
Unlock all premium features at no cost. After your trial ends, you can continue with our affordable Premium Unlimited plan at just $9.99/month.

IMO BY THE NUMBERS:
- 5,000+ Reviews Analyzed
- 276+ Video Sources
- 55+ Retailers

WHAT YOU CAN DO NOW:
Smart Search: Search any product and get AI-powered insights in seconds
IMO Score: One number that considers everything. No bias, no noise.
Review Summaries: Instantly see what thousands of buyers are saying
Video Reviews: Watch honest reviews from real people, not sponsored content

READY TO START?
Visit your dashboard at {{ dashboard_url }}

QUESTIONS?
Contact us at imhollc27@gmail.com or visit https://informedmarketopinions.com/contact

© 2025 IMO. All rights reserved. Made with ❤️ for smart shoppers.
https://informedmarketopinions.com""",
    
    "imo_payment_success": """Payment Successful - Welcome to IMO Premium!

Thank you, {{ user_name }}!

Your payment has been processed successfully. Your IMO Premium subscription is now active, and you have unlimited access to all our powerful features.

TRANSACTION DETAILS:
- Transaction ID: {{ transaction_id }}
- Plan: {{ plan_type }}
- Amount: {{ amount }}
- Billing Cycle: Monthly
- Next Billing Date: {{ next_billing_date }}
- Date: {{ payment_date }}

YOUR PREMIUM FEATURES:
✓ Trust Score (Filtered Fake Reviews)
✓ Comprehensive Review Summaries
✓ Cross-Platform Text, Video & Reel Reviews
✓ Unlimited Price Comparison
✓ Unlimited Price Drop Alerts
✓ AI-Powered Sentiment Analysis
✓ Cross-Site Inventory Analysis
✓ AI Chatbot + Review Interaction

WHAT'S NEXT?
1. Start exploring products with unlimited access
2. Set up price drop alerts on your favorite items
3. Use AI Sentiment Analysis to compare products
4. Chat with our AI chatbot about any product

Go to Dashboard: {{ dashboard_url }}

NOTE: Your subscription will automatically renew on {{ next_billing_date }}. You can cancel anytime from your account settings with no penalties.

Need Help?
Contact us at imhollc27@gmail.com or visit https://informedmarketopinions.com/contact

© 2025 IMO. All rights reserved. Made with ❤️ for smart shoppers.
https://informedmarketopinions.com""",
    
    "imo_payment_cancelled": """Payment Cancelled - No Charges

Hi {{ user_name }},

We noticed that your payment was cancelled. Don't worry—no charges have been made to your account, and your data is safe.

NO CHARGES MADE
Your payment was not processed.

PAYMENT DETAILS:
- Transaction ID: {{ transaction_id }}
- Plan Attempted: {{ plan_type }}
- Amount: {{ amount }}
- Cancelled On: {{ cancellation_date }}
{% if reason %}- Reason: {{ reason }}{% endif %}

WHAT HAPPENS NOW?
Your account will remain active with free tier features. You can:
1. Continue using IMO with basic product search
2. Try payment again with a different payment method

WHY CHOOSE IMO PREMIUM?
✓ Analyze 5,000+ reviews automatically
✓ Get one IMO Score instead of reading endless reviews
✓ Unlimited price drop alerts
✓ AI-powered sentiment analysis
✓ Starting at just $9.99/month

READY TO GIVE IT ANOTHER TRY?
Visit Pricing: {{ upgrade_url }}

If you encountered an issue or have questions, our support team is here to help.
Contact us at imhollc27@gmail.com or visit https://informedmarketopinions.com/contact

© 2025 IMO. All rights reserved. Made with ❤️ for smart shoppers.
https://informedmarketopinions.com""",
    
    "imo_price_alert": """Price Alert Active!

Hi {{ user_name }},

Your price alert has been successfully created! We'll monitor this product and notify you as soon as the price reaches your target.

PRODUCT: {{ product_name }}
CURRENT PRICE: {{ current_price }}
TARGET PRICE: {{ target_price }}
{% if savings_amount %}POTENTIAL SAVINGS: {{ savings_amount }}{% endif %}

HOW IT WORKS:
✓ We monitor prices across 55+ retailers
✓ When price drops to {{ target_price }} or lower, we'll send you an instant email
✓ You'll have direct links to purchase at the best price
✓ Manage or cancel alerts anytime

MANAGE YOUR ALERTS:
You can view, edit, or remove this alert anytime from your dashboard. Set up multiple price alerts to track different products!

Back to Dashboard: {{ dashboard_url }}

NOTE: Price alerts are updated every 6 hours. We'll send you an email notification as soon as the price drops to your target or below. You'll receive one email per price drop.

ALERT DETAILS:
Created: {{ created_at }}
Product ID: {{ product_id }}

Questions?
Contact us at imhollc27@gmail.com or visit https://informedmarketopinions.com/contact

© 2025 IMO. All rights reserved. Made with ❤️ for smart shoppers.
https://informedmarketopinions.com""",
    
    "imo_password_reset": """Reset Your IMO Password

Hi {{ user_name }},

We received a request to reset your password. Click the link below to create a new password.

RESET YOUR PASSWORD:
{{ reset_link }}

Or copy this link to your browser:
{{ reset_link }}

IMPORTANT:
- This link expires in {{ expiration_hours }} hours for security reasons
- If you didn't request this password reset, please ignore this email
- Your account remains secure until you reset your password
- This link can only be used once

NEED HELP?
If you have trouble resetting your password or didn't request this reset, contact us at imhollc27@gmail.com

© 2025 IMO. All rights reserved. Made with ❤️ for smart shoppers.
https://informedmarketopinions.com"""
}


async def read_template_file(filename: str) -> str:
    """Read template HTML file."""
    template_path = Path(__file__).parent / "app" / "templates" / "email" / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


async def seed_email_templates():
    """Seed email templates into the database."""
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting email template seeding...")
            
            for template_config in TEMPLATES:
                name = template_config["name"]
                
                # Check if template already exists
                result = await session.execute(
                    select(EmailTemplate).where(EmailTemplate.name == name)
                )
                existing = result.scalars().first()
                
                if existing:
                    logger.info(f"Template '{name}' already exists. Updating...")
                    # Update existing template
                    try:
                        body_html = await read_template_file(template_config["file"])
                    except FileNotFoundError:
                        logger.warning(f"HTML file not found for {name}, skipping update")
                        continue
                    
                    existing.subject = template_config["subject"]
                    existing.body_html = body_html
                    existing.body_text = TEMPLATE_TEXT_VERSIONS.get(name, "")
                    existing.description = template_config["description"]
                    existing.is_active = True
                    
                    await session.merge(existing)
                    logger.info(f"✓ Updated template: {name}")
                else:
                    # Create new template
                    try:
                        body_html = await read_template_file(template_config["file"])
                    except FileNotFoundError:
                        logger.warning(f"HTML file not found for {name}, skipping creation")
                        continue
                    
                    new_template = EmailTemplate(
                        id=uuid.uuid4(),
                        name=name,
                        subject=template_config["subject"],
                        body_html=body_html,
                        body_text=TEMPLATE_TEXT_VERSIONS.get(name, ""),
                        description=template_config["description"],
                        is_active=True
                    )
                    
                    session.add(new_template)
                    logger.info(f"✓ Created template: {name}")
            
            await session.commit()
            logger.info("✅ Email templates seeded successfully!")
            
            # Print summary
            result = await session.execute(select(EmailTemplate))
            templates = result.scalars().all()
            logger.info(f"\nTotal templates in database: {len(templates)}")
            for template in templates:
                status = "✓ Active" if template.is_active else "✗ Inactive"
                logger.info(f"  - {template.name}: {status}")
            
        except Exception as e:
            logger.error(f"Error seeding templates: {e}", exc_info=True)
            await session.rollback()
            raise


async def main():
    """Main entry point."""
    try:
        await seed_email_templates()
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
