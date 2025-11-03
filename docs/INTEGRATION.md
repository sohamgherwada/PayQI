# PayQI Integration Guide

Complete guide for businesses to integrate PayQI payment gateway into their applications.

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Authentication](#api-authentication)
3. [Payment Integration](#payment-integration)
4. [Webhook Integration](#webhook-integration)
5. [SDKs and Libraries](#sdks-and-libraries)
6. [Security Best Practices](#security-best-practices)
7. [Error Handling](#error-handling)
8. [Testing](#testing)

## Quick Start

### 1. Get Your API Credentials

1. Sign up at [your-payqi-instance.com](https://your-payqi-instance.com)
2. Verify your email
3. Complete KYC verification (if required)
4. Get your API token from the dashboard

### 2. Install SDK (Choose your language)

**Python:**
```bash
pip install payqi
```

**Ruby:**
```bash
gem install payqi
```

**JavaScript/Node.js:**
```bash
npm install payqi
```

### 3. Make Your First Payment

**Python Example:**
```python
import payqi

# Initialize client
client = payqi.Client(api_key='your_api_key_here')

# Create a payment
payment = client.payments.create(
    amount=10.00,
    currency='XRP',
    description='Order #12345'
)

print(f"Payment created: {payment.id}")
print(f"Send XRP to: {payment.pay_address}")
print(f"Destination tag: {payment.destination_tag}")
```

**Ruby Example:**
```ruby
require 'payqi'

# Initialize client
client = PayQI::Client.new(api_key: 'your_api_key_here')

# Create a payment
payment = client.payments.create(
  amount: 10.00,
  currency: 'XRP',
  description: 'Order #12345'
)

puts "Payment created: #{payment.id}"
puts "Send XRP to: #{payment.pay_address}"
puts "Destination tag: #{payment.destination_tag}"
```

**JavaScript Example:**
```javascript
const PayQI = require('payqi');

// Initialize client
const client = new PayQI.Client('your_api_key_here');

// Create a payment
const payment = await client.payments.create({
  amount: 10.00,
  currency: 'XRP',
  description: 'Order #12345'
});

console.log(`Payment created: ${payment.id}`);
console.log(`Send XRP to: ${payment.pay_address}`);
console.log(`Destination tag: ${payment.destination_tag}`);
```

## API Authentication

PayQI uses API keys for authentication. Include your API key in all requests.

### API Key Security

?? **IMPORTANT**: Never expose your API keys in client-side code or public repositories.

**Best Practices:**
- Store API keys as environment variables
- Use different keys for development and production
- Rotate keys regularly
- Revoke compromised keys immediately

**Example - Environment Variables:**

```bash
# .env file (never commit this!)
PAYQI_API_KEY=sk_live_51abc123...
PAYQI_API_URL=https://api.payqi.com
```

```python
import os
from payqi import Client

client = Client(api_key=os.getenv('PAYQI_API_KEY'))
```

## Payment Integration

### Accepting XRP Payments

XRP payments use destination tags to track transactions.

```python
# Create XRP payment
payment = client.payments.create(
    amount=25.50,
    currency='XRP',
    description='Product purchase',
    metadata={'order_id': '12345'}
)

# Display to customer
print(f"""
Pay with XRP:
Amount: {payment.amount_xrp} XRP
Address: {payment.pay_address}
Destination Tag: {payment.destination_tag}
""")

# Poll for payment status
import time
while payment.status == 'pending':
    payment = client.payments.retrieve(payment.id)
    if payment.status == 'completed':
        print("Payment received!")
        break
    time.sleep(5)  # Check every 5 seconds
```

### Accepting Other Cryptocurrencies

```python
# Bitcoin payment
payment = client.payments.create(
    amount=50.00,
    currency='BTC',
    description='Service fee'
)

# Customer will be redirected to payment page
redirect_url = payment.checkout_url
# Redirect customer to redirect_url
```

### Payment Status Webhooks

Webhooks notify you when payment status changes. [See Webhook Integration](#webhook-integration).

## Webhook Integration

### Setting Up Webhooks

1. Go to your dashboard ? Settings ? Webhooks
2. Add webhook endpoint: `https://yourdomain.com/webhooks/payqi`
3. Save your webhook secret

### Verifying Webhook Signatures

**Python:**
```python
from payqi import verify_webhook_signature

@app.route('/webhooks/payqi', methods=['POST'])
def handle_webhook():
    payload = request.data
    signature = request.headers.get('X-PayQI-Signature')
    
    # Verify signature
    try:
        event = verify_webhook_signature(
            payload,
            signature,
            webhook_secret=os.getenv('PAYQI_WEBHOOK_SECRET')
        )
    except ValueError:
        return 'Invalid signature', 400
    
    # Handle event
    if event.type == 'payment.completed':
        payment = event.data
        # Update your database
        order = Order.get(payment.metadata['order_id'])
        order.mark_as_paid()
    
    return 'OK', 200
```

**Ruby:**
```ruby
require 'payqi'
require 'sinatra'

post '/webhooks/payqi' do
  payload = request.body.read
  signature = request.env['HTTP_X_PAYQI_SIGNATURE']
  
  # Verify signature
  begin
    event = PayQI::Webhook.verify(
      payload,
      signature,
      webhook_secret: ENV['PAYQI_WEBHOOK_SECRET']
    )
  rescue PayQI::SignatureVerificationError
    status 400
    return 'Invalid signature'
  end
  
  # Handle event
  if event.type == 'payment.completed'
    payment = event.data
    order = Order.find(payment.metadata['order_id'])
    order.update(status: 'paid')
  end
  
  status 200
  'OK'
end
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `payment.created` | New payment created |
| `payment.pending` | Payment awaiting confirmation |
| `payment.completed` | Payment successfully received |
| `payment.failed` | Payment failed |
| `payment.expired` | Payment expired |

## SDKs and Libraries

### Official SDKs

- **Python**: `pip install payqi`
- **Ruby**: `gem install payqi`
- **JavaScript/Node.js**: `npm install payqi`
- **PHP**: `composer require payqi/payqi-php`

### REST API

You can also use the REST API directly:

```bash
curl https://api.payqi.com/api/payments \
  -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.00,
    "currency": "XRP"
  }'
```

## Security Best Practices

### 1. Keep API Keys Secret

? **DO:**
- Store keys in environment variables
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly

? **DON'T:**
- Commit keys to version control
- Share keys in emails or chat
- Use the same key in multiple environments

### 2. Verify Webhook Signatures

Always verify webhook signatures to ensure requests come from PayQI:

```python
from payqi import verify_webhook_signature

def handle_webhook(request):
    signature = request.headers.get('X-PayQI-Signature')
    
    try:
        event = verify_webhook_signature(
            request.data,
            signature,
            webhook_secret=WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid signature - reject request
        return {'error': 'Invalid signature'}, 400
```

### 3. Use HTTPS

Always use HTTPS for API calls and webhooks:

- ? `https://api.payqi.com`
- ? `http://api.payqi.com` (insecure)

### 4. Implement Idempotency

Use idempotency keys to prevent duplicate payments:

```python
payment = client.payments.create(
    amount=10.00,
    currency='XRP',
    idempotency_key='unique-key-12345'
)
```

### 5. Validate Amounts

Always validate payment amounts server-side:

```python
# Client-side (for display only)
display_amount = calculate_total()

# Server-side (actual payment)
validated_amount = validate_amount(display_amount)
payment = client.payments.create(amount=validated_amount, ...)
```

### 6. Rate Limiting

Respect rate limits:
- 100 requests per minute per API key
- Implement exponential backoff for retries

```python
import time
from payqi.errors import RateLimitError

def create_payment_with_retry(client, *args, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.payments.create(*args, **kwargs)
        except RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    raise Exception("Rate limit exceeded")
```

## Error Handling

### Common Errors

| Error Code | Description | Solution |
|-----------|-------------|----------|
| `401` | Unauthorized | Check API key |
| `402` | Payment required | Verify account status |
| `404` | Not found | Check resource ID |
| `429` | Rate limit exceeded | Implement backoff |
| `500` | Server error | Retry with exponential backoff |

### Error Handling Example

```python
from payqi import Client
from payqi.errors import APIError, RateLimitError

client = Client(api_key=API_KEY)

try:
    payment = client.payments.create(
        amount=10.00,
        currency='XRP'
    )
except RateLimitError:
    # Wait and retry
    time.sleep(60)
    payment = client.payments.create(...)
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Error code: {e.code}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

### Test Mode

Use test mode for development:

```python
client = Client(
    api_key=TEST_API_KEY,
    api_url='https://test-api.payqi.com'
)
```

### Test Cards/Addresses

- **XRP Test Address**: Use testnet addresses
- **Test API Key**: Available in dashboard
- **Webhook Testing**: Use webhook testing tool

### Integration Testing

```python
import pytest
from payqi import Client

@pytest.fixture
def payqi_client():
    return Client(api_key=os.getenv('PAYQI_TEST_API_KEY'))

def test_create_payment(payqi_client):
    payment = payqi_client.payments.create(
        amount=10.00,
        currency='XRP'
    )
    assert payment.status == 'pending'
    assert payment.pay_address is not None
```

## Support

- **Documentation**: [docs.payqi.com](https://docs.payqi.com)
- **API Reference**: [api.payqi.com/docs](https://api.payqi.com/docs)
- **Support Email**: support@payqi.com
- **Status Page**: [status.payqi.com](https://status.payqi.com)

## Next Steps

1. [Read the API Reference](API_REFERENCE.md)
2. [Explore Code Examples](EXAMPLES.md)
3. [Set Up Webhooks](WEBHOOKS.md)
4. [Go Live Checklist](GO_LIVE.md)
