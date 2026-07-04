# Payment Integration Guide

## Overview
This guide covers setting up payment processing for the Donor Platform with support for:
- Razorpay (primary - recommended for India)
- Stripe
- PayPal
- Direct Bank Transfer

## Owner Information
- **Email**: vinod1914581@gmail.com
- **Name**: Pallapu Vinod
- **Organization**: Donor Platform

## Bank Account Details (Confidential)

```
Account Number: 42818590419
Account Holder: Pallapu Vinod
Account Type: Savings Account
IFSC Code: SBIN0021400
Bank Branch: VENKATARAMANA COLONY, KURNOOL
Bank: State Bank of India (SBI)
```

## Setting Up Razorpay (Recommended for India)

### 1. Create Razorpay Account
- Visit https://dashboard.razorpay.com
- Sign up or log in
- Complete verification process

### 2. Get API Keys
- Go to Settings → API Keys
- Copy "Key ID" and "Key Secret"
- Store them in `.env` file

### 3. Configure Environment
```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_SECRET_KEY=your_secret_key
ENABLE_RAZORPAY=true
```

### 4. Test Payment Flow
```bash
# Backend should be running
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "donor_name": "Test User",
    "donor_email": "test@example.com",
    "campaign_id": "campaign-1",
    "donor_id": "donor-1"
  }'
```

## Setting Up Stripe

### 1. Create Stripe Account
- Visit https://dashboard.stripe.com
- Sign up
- Verify business details

### 2. Get API Keys
- Go to Developers → API keys
- Copy "Publishable key" and "Secret key"

### 3. Configure
```env
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
ENABLE_STRIPE=true
```

## Setting Up PayPal

### 1. Create PayPal Business Account
- Visit https://developer.paypal.com
- Create business account
- Set up app credentials

### 2. Get API Credentials
- Go to App & Credentials
- Copy Client ID and Secret

### 3. Configure
```env
PAYPAL_CLIENT_ID=client_id
PAYPAL_SECRET=secret
ENABLE_PAYPAL=true
```

## Payment Flow

### 1. Initiate Payment
```
POST /api/v1/payments/initiate
{
  "amount": 1000,
  "donor_name": "John Doe",
  "donor_email": "john@example.com",
  "campaign_id": "campaign-123",
  "donor_id": "donor-456"
}
```

### 2. Frontend Displays Payment Form
- Show Razorpay checkout modal
- Or redirect to Stripe/PayPal

### 3. Verify Payment
```
POST /api/v1/payments/verify
{
  "razorpay_order_id": "order_id",
  "razorpay_payment_id": "payment_id",
  "razorpay_signature": "signature"
}
```

### 4. Webhook Confirmation
- Payment gateway sends webhook
- Backend confirms transaction
- Donor receives confirmation email

## Webhook Setup

### Razorpay Webhooks
1. Go to Settings → Webhooks
2. Add endpoint: `https://yourdomain.com/api/v1/payments/webhook`
3. Select events:
   - payment.authorized
   - payment.failed
   - payment.captured
   - refund.created

### Stripe Webhooks
1. Go to Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/v1/payments/webhook`
3. Select events:
   - payment_intent.succeeded
   - payment_intent.payment_failed

### PayPal Webhooks
1. Go to Apps & Credentials
2. Create webhook URL
3. Select events:
   - PAYMENT.SALE.COMPLETED
   - PAYMENT.SALE.DENIED
   - PAYMENT.SALE.REFUNDED

## Testing Payments

### Test Cards
**Razorpay (India)**
- Card Number: 4111111111111111
- Expiry: 12/25
- CVV: 123

**Stripe**
- Card Number: 4242 4242 4242 4242
- Expiry: 12/25
- CVC: 123

**PayPal**
- Use Sandbox accounts at developer.paypal.com

## Payment Receipt Generation

Receipts are automatically generated and sent to donors:

```
PAYMENT RECEIPT
===============

Transaction ID: TXN-2024-001234
Amount: ₹1,000.00
Payment Method: Razorpay
Account Holder: Pallapu Vinod
Account Type: Savings
Bank Branch: VENKATARAMANA COLONY, KURNOOL

Date: 2024-01-15 10:30:45
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production
4. **Validate signatures** on all webhooks
5. **Implement rate limiting** on payment endpoints
6. **Store encrypted** payment information
7. **Follow PCI compliance** guidelines
8. **Monitor transactions** for fraud

## Troubleshooting

### Payment Initiation Fails
- Check API keys are correct
- Verify amount is in correct currency
- Ensure gateway is enabled in .env

### Webhook Not Received
- Verify endpoint URL is correct
- Check firewall/security groups
- Enable webhook in payment gateway dashboard
- Check server logs for errors

### Refund Issues
- Ensure payment was completed
- Check refund amount doesn't exceed original
- Verify gateway supports refunds

## Support

- **Razorpay Support**: support@razorpay.com
- **Stripe Support**: support.stripe.com
- **PayPal Support**: paypal.com/support
- **Our Support**: support@donorplatform.com

## Related Files

- Configuration: `backend/app/config/payment.py`
- Service: `backend/app/services/payment.py`
- API Routes: `backend/app/api/payments.py`
- Environment: `.env.payment.example`
