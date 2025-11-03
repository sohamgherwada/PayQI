# PayQI Quick Start Guide

Get up and running with PayQI in 5 minutes.

## Step 1: Sign Up

1. Visit [payqi.com](https://payqi.com)
2. Click "Sign Up"
3. Enter your email and create a password
4. Verify your email address

## Step 2: Get Your API Key

1. Log in to your dashboard
2. Navigate to Settings ? API Keys
3. Click "Create API Key"
4. Copy your secret key (starts with `sk_live_` or `sk_test_`)

?? **Important**: You'll only see the key once. Save it securely!

## Step 3: Install SDK

Choose your preferred language:

**Python:**
```bash
pip install payqi
```

**Node.js:**
```bash
npm install payqi
```

**Ruby:**
```bash
gem install payqi
```

## Step 4: Create Your First Payment

### Python Example

```python
from payqi import Client
import os

# Initialize client
client = Client(api_key=os.getenv('PAYQI_API_KEY'))

# Create a payment
payment = client.payments.create(
    amount=10.00,
    currency='XRP',
    description='Test payment'
)

print(f"Payment ID: {payment.id}")
print(f"Status: {payment.status}")
print(f"XRP Address: {payment.pay_address}")
print(f"Destination Tag: {payment.destination_tag}")
```

### Node.js Example

```javascript
const PayQI = require('payqi');

const client = new PayQI.Client(process.env.PAYQI_API_KEY);

const payment = await client.payments.create({
  amount: 10.00,
  currency: 'XRP',
  description: 'Test payment'
});

console.log(`Payment ID: ${payment.id}`);
console.log(`Status: ${payment.status}`);
console.log(`XRP Address: ${payment.pay_address}`);
console.log(`Destination Tag: ${payment.destination_tag}`);
```

### Ruby Example

```ruby
require 'payqi'

client = PayQI::Client.new(api_key: ENV['PAYQI_API_KEY'])

payment = client.payments.create(
  amount: 10.00,
  currency: 'XRP',
  description: 'Test payment'
)

puts "Payment ID: #{payment.id}"
puts "Status: #{payment.status}"
puts "XRP Address: #{payment.pay_address}"
puts "Destination Tag: #{payment.destination_tag}"
```

## Step 5: Handle Payment Status

### Option 1: Polling

```python
import time

while payment.status == 'pending':
    payment = client.payments.retrieve(payment.id)
    if payment.status == 'completed':
        print("Payment received!")
        # Update your database, send confirmation email, etc.
        break
    time.sleep(5)  # Check every 5 seconds
```

### Option 2: Webhooks (Recommended)

Set up a webhook endpoint to receive payment notifications automatically.

See [Webhook Integration Guide](WEBHOOKS.md) for details.

## Complete Example: E-commerce Checkout

```python
from payqi import Client
from flask import Flask, request, jsonify

app = Flask(__name__)
payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    order_id = data['order_id']
    amount = data['amount']
    
    # Create payment
    payment = payqi.payments.create(
        amount=amount,
        currency='XRP',
        description=f'Order #{order_id}',
        metadata={'order_id': order_id}
    )
    
    return jsonify({
        'payment_id': payment.id,
        'xrp_address': payment.pay_address,
        'destination_tag': payment.destination_tag,
        'amount_xrp': payment.amount_xrp,
        'status': payment.status
    })

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    # Verify webhook signature
    signature = request.headers.get('X-PayQI-Signature')
    event = payqi.webhooks.verify(request.data, signature)
    
    if event.type == 'payment.completed':
        order_id = event.data.metadata['order_id']
        # Mark order as paid
        mark_order_as_paid(order_id)
    
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
```

## Environment Setup

Create a `.env` file:

```bash
# Development
PAYQI_API_KEY=sk_test_51abc123...
PAYQI_API_URL=https://test-api.payqi.com
PAYQI_WEBHOOK_SECRET=whsec_...

# Production (when ready)
# PAYQI_API_KEY=sk_live_51xyz789...
# PAYQI_API_URL=https://api.payqi.com
```

## Testing

### Test Mode

Use test API keys for development:

```python
# Test API key (starts with sk_test_)
client = Client(api_key='sk_test_...')
```

### Test Payments

In test mode, you can:
- Create test payments without real cryptocurrency
- Simulate payment completion
- Test webhook integrations

## Security Checklist

- [ ] API key stored as environment variable
- [ ] Never commit API keys to version control
- [ ] Use HTTPS for all API calls
- [ ] Verify webhook signatures
- [ ] Validate amounts server-side
- [ ] Implement idempotency keys
- [ ] Set up rate limiting

## Next Steps

1. ? Read the [Full Integration Guide](INTEGRATION.md)
2. ? Set up [Webhooks](WEBHOOKS.md)
3. ? Review [Security Best Practices](SECURITY.md)
4. ? Test in [Test Mode](TESTING.md)
5. ? Go through [Go Live Checklist](GO_LIVE.md)

## Need Help?

- ?? [Full Documentation](https://docs.payqi.com)
- ?? [Support Email](mailto:support@payqi.com)
- ?? [Report Issues](https://github.com/payqi/issues)
- ?? [Community Forum](https://forum.payqi.com)
