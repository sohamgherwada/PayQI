# Business Setup Guide

Step-by-step guide for businesses to get started with PayQI.

## Step 1: Create Account

1. Visit [payqi.com/signup](https://payqi.com/signup)
2. Enter your business email
3. Create a strong password
4. Verify your email address
5. Complete business profile

## Step 2: Verify Your Business

### Required Information

- Business name
- Business type (LLC, Corporation, etc.)
- Tax ID / EIN
- Business address
- Bank account information (for payouts)

### KYC Verification

1. Upload business registration documents
2. Upload government-issued ID
3. Provide proof of address
4. Wait for approval (typically 1-3 business days)

## Step 3: Get API Credentials

1. Log in to dashboard
2. Navigate to Settings ? API Keys
3. Click "Create API Key"
4. **Save your secret key** (you'll only see it once!)

?? **Security**: Store your API key securely. Never share it or commit it to version control.

## Step 4: Install SDK

Choose your programming language:

### Python
```bash
pip install payqi
```

### Node.js
```bash
npm install payqi
```

### Ruby
```bash
gem install payqi
```

## Step 5: Make Your First Payment

### Python Example

```python
from payqi import Client
import os

# Initialize with your API key
client = Client(api_key=os.getenv('PAYQI_API_KEY'))

# Create a payment
payment = client.payments.create(
    amount=10.00,
    currency='XRP',
    description='Test payment'
)

print(f"Payment ID: {payment.id}")
print(f"XRP Address: {payment.pay_address}")
print(f"Destination Tag: {payment.destination_tag}")
```

### What Happens Next?

1. Customer receives payment details (address + tag)
2. Customer sends XRP
3. Payment status updates to "completed"
4. You receive webhook notification

## Step 6: Set Up Webhooks

Webhooks notify you when payments complete.

1. Go to Dashboard ? Settings ? Webhooks
2. Click "Add Webhook Endpoint"
3. Enter your URL: `https://yourdomain.com/webhooks/payqi`
4. Select events (payment.completed, payment.failed, etc.)
5. Save your webhook secret

See [Webhook Integration Guide](docs/WEBHOOKS.md) for implementation details.

## Step 7: Test Your Integration

### Test Mode

Use test API keys for development:

- Test API key: `sk_test_...`
- Test API URL: `https://test-api.payqi.com`

Test payments don't process real cryptocurrency.

### Testing Checklist

- [ ] Create payment
- [ ] Check payment status
- [ ] Receive webhook notification
- [ ] Handle errors gracefully
- [ ] Test all supported currencies

## Step 8: Go Live

When ready for production:

1. ? Complete all testing
2. ? Review [Go Live Checklist](docs/GO_LIVE.md)
3. ? Switch to live API keys
4. ? Enable production webhooks
5. ? Monitor closely for first 24 hours

## Support Resources

- ?? [Full Documentation](docs/README.md)
- ?? [Quick Start Guide](docs/QUICK_START.md)
- ?? [Code Examples](docs/EXAMPLES.md)
- ?? [Security Guide](docs/SECURITY.md)
- ?? support@payqi.com

## Common Questions

### How long do payments take?

- XRP: Typically 3-5 seconds
- Bitcoin: 10-60 minutes
- Ethereum: 2-5 minutes

### What fees do you charge?

- XRP: 0% (direct integration)
- Other currencies: 2.9% + $0.30 per transaction

### How do I receive payouts?

Payouts are sent to your linked bank account:
- Daily automatic payouts
- Minimum payout: $100
- Processing time: 1-3 business days

### Can I accept multiple currencies?

Yes! PayQI supports:
- Bitcoin (BTC)
- Ethereum (ETH)
- XRP
- USDT
- USDC
- Litecoin (LTC)
- Dogecoin (DOGE)

### Is PayQI secure?

Yes! We follow industry best practices:
- PCI DSS compliant
- End-to-end encryption
- Regular security audits
- Webhook signature verification

## Need Help?

- Email: support@payqi.com
- Live Chat: Available in dashboard
- Documentation: [docs.payqi.com](https://docs.payqi.com)
- Status: [status.payqi.com](https://status.payqi.com)
