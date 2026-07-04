# Comprehensive Configuration Guide

## Quick Start

### 1. Copy and Configure Environment Variables
```bash
cp .env.example .env
nano .env  # or open in your editor
```

## Owner Configuration

Your organization details are already configured:

- **Email**: vinod1914581@gmail.com
- **Name**: Pallapu Vinod
- **Organization**: Donor Platform

Update in `.env`:
```env
OWNER_EMAIL=vinod1914581@gmail.com
OWNER_NAME=Pallapu Vinod
ORGANIZATION_NAME=Donor Platform
```

## Bank Account Setup

Your bank details are stored securely in `.env`:

```env
BANK_ACCOUNT_NUMBER=42818590419
BANK_ACCOUNT_HOLDER=Pallapu Vinod
BANK_ACCOUNT_TYPE=Savings Account
BANK_IFSC_CODE=SBIN0021400
BANK_BRANCH=VENKATARAMANA COLONY,KURNOOL
```

**Security Note**: Never commit the `.env` file to version control. Add `.env` to `.gitignore` (already done).

## Payment Gateway Configuration

### Razorpay (Primary)

1. **Create Account**
   - Visit: https://dashboard.razorpay.com
   - Sign up and complete verification

2. **Get API Keys**
   - Settings → API Keys
   - Copy Key ID and Key Secret

3. **Configure in `.env`**
   ```env
   RAZORPAY_KEY_ID=rzp_live_your_key_id
   RAZORPAY_SECRET_KEY=your_razorpay_secret_key
   ENABLE_RAZORPAY=true
   ```

4. **Setup Webhook** (for payment confirmations)
   - Go to Settings → Webhooks
   - Add: `https://yourdomain.com/api/v1/payments/webhook/razorpay`
   - Select: payment.authorized, payment.captured, refund.created

### Optional: Stripe Setup

1. Create account at https://dashboard.stripe.com
2. Get Publishable and Secret keys
3. Configure in `.env`:
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_live_your_key
   STRIPE_SECRET_KEY=sk_live_your_secret
   ENABLE_STRIPE=true
   ```

### Optional: PayPal Setup

1. Create account at https://developer.paypal.com
2. Get Client ID and Secret
3. Configure in `.env`:
   ```env
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_SECRET=your_secret
   ENABLE_PAYPAL=true
   ```

## Email Configuration

Set up Gmail or your email service:

### Gmail Setup
1. Enable 2-Step Verification
2. Generate App Password at myaccount.google.com/apppasswords
3. Configure in `.env`:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

## Database Setup

### PostgreSQL Local
```bash
# Create database
createdb donor_db

# Create user
createuser donor_user

# Set password
psql -c "ALTER USER donor_user WITH PASSWORD 'donor_password';"

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE donor_db TO donor_user;"
```

### PostgreSQL with Docker
```bash
docker run --name donor_db \
  -e POSTGRES_USER=donor_user \
  -e POSTGRES_PASSWORD=donor_password \
  -e POSTGRES_DB=donor_db \
  -p 5432:5432 \
  -d postgres:15-alpine
```

Configure in `.env`:
```env
DATABASE_URL=postgresql://donor_user:donor_password@localhost:5432/donor_db
```

## Redis Setup

### Redis Local
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis-server

# Verify
redis-cli ping  # Should return PONG
```

### Redis with Docker
```bash
docker run --name donor_redis \
  -p 6379:6379 \
  -d redis:7-alpine
```

Configure in `.env`:
```env
REDIS_URL=redis://localhost:6379
```

## Security Configuration

### Generate Secret Key
```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use online: https://generate-random.org/
```

Update in `.env`:
```env
SECRET_KEY=your-generated-secret-key-here
```

### API Keys
Generate unique keys for:
- Razorpay: From dashboard
- Stripe: From dashboard
- PayPal: From developer portal

## CORS Configuration

Configure allowed origins in `.env`:

```env
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Admin User Setup

Default admin credentials in `.env`:
```env
ADMIN_EMAIL=admin@donorplatform.com
ADMIN_PASSWORD=secure-password-change-this
```

**Important**: Change these in production!

## Deployment Configuration

### Development
```env
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
```

### Production
```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

Update database, secret key, and enable HTTPS:
```env
ALLOWED_ORIGINS=https://yourdomain.com
SECURE_SSL_REDIRECT=True
```

## Verification Checklist

After configuration, verify:

1. **Database Connection**
   ```bash
   psql -h localhost -U donor_user -d donor_db
   ```

2. **Redis Connection**
   ```bash
   redis-cli ping
   ```

3. **Email Configuration**
   - Test email sending from admin panel

4. **Payment Gateway**
   - Test transaction in sandbox mode
   - Verify webhook delivery

5. **Backend API**
   ```bash
   curl http://localhost:8000/health
   ```

6. **Frontend**
   ```bash
   npm run dev
   ```

## File Structure for Configuration

```
.env                          # Your configuration (DO NOT COMMIT)
.env.example                  # Template (COMMIT THIS)
.env.payment.example          # Payment configuration template
backend/app/config/payment.py # Owner details
PAYMENT_SETUP.md              # Payment setup guide
SETUP.md                      # General setup guide
```

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U donor_user -d donor_db

# Check DATABASE_URL format
echo $DATABASE_URL
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping

# Restart Redis
redis-cli shutdown
redis-server
```

### Payment Gateway Error
- Verify API keys are correct
- Check webhook URL is accessible
- Review payment gateway logs

### Email Not Sending
- Verify SMTP credentials
- Check email whitelist settings
- Review email logs

## Support & Resources

- **Razorpay Docs**: https://razorpay.com/docs/
- **Stripe Docs**: https://stripe.com/docs/
- **PayPal Docs**: https://developer.paypal.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

## Next Steps

1. ✅ Configure `.env` with your details
2. ✅ Set up PostgreSQL database
3. ✅ Set up Redis cache
4. ✅ Configure payment gateway (Razorpay)
5. ✅ Set up email service
6. ✅ Run migrations
7. ✅ Start backend: `uvicorn app.main:app --reload`
8. ✅ Start frontend: `npm run dev`
9. ✅ Test payment flow
10. ✅ Deploy to production
