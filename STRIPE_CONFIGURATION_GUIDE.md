# Stripe Payment Integration - Configuration Guide

## ⚠️ Issue Fixed

**Error:** `'NoneType' object has no attribute 'Session'`

**Cause:** STRIPE_SECRET_KEY was not properly configured in the .env file

**Solution:** Added validation checks and proper error messages to guide users to configure Stripe

---

## 🔧 What Was Fixed

### 1. **Stripe Service Initialization** (`backend/app/services/stripe_service.py`)

**Before:**
```python
stripe.api_key = settings.STRIPE_SECRET_KEY  # Could be empty or invalid
```

**After:**
```python
if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.startswith('sk_'):
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    logger.warning("STRIPE_SECRET_KEY is not configured or invalid")
    stripe.api_key = None
```

### 2. **API Method Validation** 

Added checks in `create_checkout_session()` and `handle_checkout_complete()` to verify Stripe is configured before making API calls:

```python
if not stripe.api_key:
    raise Exception(
        "Stripe is not configured. Please set STRIPE_SECRET_KEY in environment variables. "
        "Get your key from https://dashboard.stripe.com/apikeys"
    )
```

### 3. **Better Error Messages**

Now users see clear guidance instead of cryptic `'NoneType'` errors:
```
Stripe is not configured. Please set STRIPE_SECRET_KEY in environment variables.
Get your key from https://dashboard.stripe.com/apikeys
```

---

## 🔑 Setting Up Stripe Properly

### Step 1: Create a Stripe Account
1. Go to https://stripe.com
2. Sign up for a free account
3. Email verification

### Step 2: Get API Keys
1. Go to https://dashboard.stripe.com/apikeys
2. Make sure you're in **Test Mode** (toggle on top right)
3. Copy your **Secret Key** (starts with `sk_test_`)

**Example:**
```
sk_test_51RoXHVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Update .env File
Replace the invalid key with your actual Stripe secret key:

```bash
# BEFORE (Invalid)
STRIPE_SECRET_KEY=d0d7bcc5f947715e13319c3923df355c2ea4653419b1af7744e8e9d0deddf4a0

# AFTER (Valid test key)
STRIPE_SECRET_KEY=sk_test_51RoXHVCihtWtQlKuxxxxxxxxxxxxxx
```

### Step 4: Also Update Publishable Key

1. In Stripe dashboard, also copy your **Publishable Key** (starts with `pk_test_`)
2. Update in .env:

```bash
STRIPE_PUBLISHABLE_KEY=pk_test_51RoXHVCihtWtQlKuxxxxxxxxxxxxxx
```

### Step 5: Webhook Secret (Optional, for production)
For now, you can leave `STRIPE_WEBHOOK_SECRET` as is. It's needed for production webhooks.

---

## 📋 Environment Variables

All required Stripe variables in `.env`:

```bash
# Stripe Payment Gateway
STRIPE_SECRET_KEY=sk_test_51RoXHVxxxxxxxxxxxxxx          # ⚠️ REQUIRED
STRIPE_PUBLISHABLE_KEY=pk_test_51RoXHVxxxxxxxxxxxxxx     # ⚠️ REQUIRED
STRIPE_WEBHOOK_SECRET=whsec_test_xxx                     # Optional for dev

# Subscription Settings
TRIAL_PERIOD_DAYS=7
PREMIUM_MONTHLY_PRICE=999    # $9.99 in cents
PREMIUM_YEARLY_PRICE=6999    # $69.99 in cents
```

---

## ✅ Testing Stripe Integration

### Test Card Numbers (in Test Mode)

Use these card numbers to test:

**Successful Payment:**
```
4242 4242 4242 4242
Exp: Any future date
CVC: Any 3 digits
```

**Declined Payment:**
```
4000 0000 0000 0002
Exp: Any future date
CVC: Any 3 digits
```

**Requires Authentication:**
```
4000 2500 0000 3155
Exp: Any future date
CVC: Any 3 digits
```

### Test Payment Flow

1. Sign in to app
2. Go to /pricing page
3. Click "Subscribe Now" or "Try 7 Days Free"
4. You'll be redirected to Stripe checkout
5. Use test card `4242 4242 4242 4242`
6. Enter any future expiry and CVC
7. Complete the payment
8. You'll be redirected to success page

---

## 🚀 Deployment to Production

When deploying to production:

1. **Get Production Keys**
   - In Stripe dashboard, toggle OFF "Test Mode"
   - Copy production **Secret Key** (starts with `sk_live_`)
   - Copy production **Publishable Key** (starts with `pk_live_`)

2. **Update Environment Variables**
   ```bash
   STRIPE_SECRET_KEY=sk_live_51RoXHVxxxxxxxxxxxxxx
   STRIPE_PUBLISHABLE_KEY=pk_live_51RoXHVxxxxxxxxxxxxxx
   ```

3. **Set Up Webhook**
   - In Stripe dashboard: Settings → Webhooks
   - Add endpoint: `https://yourdomain.com/api/v1/webhooks/stripe`
   - Select events:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

4. **Enable HTTPS**
   - All Stripe integrations require HTTPS
   - Configure SSL certificate on your domain

---

## 📊 Stripe Pricing Configuration

Currently set in .env:

**Monthly Plan:** $9.99 (999 cents)
**Yearly Plan:** $69.99 (6999 cents) = ~$5.83/month

To change pricing:

```bash
# Update these values (in cents)
PREMIUM_MONTHLY_PRICE=999      # $9.99
PREMIUM_YEARLY_PRICE=6999      # $69.99

# For example, to charge $19.99/month:
PREMIUM_MONTHLY_PRICE=1999

# For example, to charge $99/year:
PREMIUM_YEARLY_PRICE=9900
```

---

## 🐛 Troubleshooting

### Error: "Stripe is not configured"

**Cause:** `STRIPE_SECRET_KEY` is empty or invalid

**Solution:**
1. Check `.env` file has `STRIPE_SECRET_KEY=sk_test_xxx`
2. Verify key starts with `sk_test_` (for testing)
3. Verify key is not the invalid one: `d0d7bcc5f947715e13319c3923df355c2ea4653419b1af7744e8e9d0deddf4a0`
4. Restart the server after updating `.env`

### Error: "Invalid API Key Provided"

**Cause:** API key format is wrong

**Solution:**
1. Go to https://dashboard.stripe.com/apikeys
2. Copy the **Secret Key** (not Publishable Key)
3. Ensure it starts with `sk_test_` (for testing) or `sk_live_` (for production)
4. Paste into `.env`

### Error: "No such plan"

**Cause:** Pricing not configured correctly

**Solution:**
1. Check `PREMIUM_MONTHLY_PRICE` and `PREMIUM_YEARLY_PRICE` are set
2. Values should be in cents: 999 = $9.99
3. Restart server after changing prices

### Redirect Loop on Checkout

**Cause:** Success/cancel URLs are wrong

**Solution:**
1. Check frontend is running on correct port
2. Success URL default: `http://localhost:5173/dashboard?payment=success`
3. Cancel URL default: `http://localhost:5173/pricing?payment=cancelled`
4. Update URLs in environment if different

---

## 📖 API Endpoints

### Create Checkout Session
```
POST /api/v1/payments/create-checkout-session
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_type": "premium",
  "billing_cycle": "monthly",  // or "yearly"
  "success_url": "https://app.com/success",
  "cancel_url": "https://app.com/cancel"
}

Response:
{
  "success": true,
  "session_id": "cs_test_xxx",
  "url": "https://checkout.stripe.com/pay/cs_test_xxx"
}
```

### Start Trial
```
POST /api/v1/payments/start-trial
Authorization: Bearer <token>

{}

Response:
{
  "success": true,
  "message": "Trial subscription started..."
}
```

### Get Subscription
```
GET /api/v1/payments/subscription
Authorization: Bearer <token>

Response:
{
  "plan_type": "premium",
  "billing_cycle": "monthly",
  "is_active": true,
  "subscription_start": "2025-12-23T...",
  "subscription_end": "2026-01-23T...",
  "is_trial": false,
  "days_remaining": 31
}
```

---

## ✨ Features Implemented

| Feature | Status | Notes |
|---------|--------|-------|
| Checkout session creation | ✅ Complete | Creates Stripe session |
| Trial subscriptions | ✅ Complete | 7-day free trial |
| Premium plans | ✅ Complete | Monthly & yearly |
| Payment processing | ✅ Complete | Via Stripe |
| Webhook handling | ✅ Complete | For payment events |
| Subscription tracking | ✅ Complete | Stored in database |
| Success page | ✅ Complete | After payment |
| Cancel handling | ✅ Complete | If user cancels |

---

## 🔒 Security Notes

✅ **Never commit Stripe keys to git:**
- Use `.env` file (in `.gitignore`)
- Use environment variables for production
- Rotate keys if accidentally exposed

✅ **Use Test Mode during development:**
- Test mode doesn't charge real cards
- Use test card numbers provided above
- Switch to production only when ready

✅ **Validate webhooks:**
- Always verify webhook signatures
- Check `stripe_webhook_secret` matches

---

## 📚 Resources

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Test Cards:** https://stripe.com/docs/testing
- **API Reference:** https://stripe.com/docs/api

---

**Last Updated:** December 23, 2024
**Status:** ✅ Ready for Configuration
