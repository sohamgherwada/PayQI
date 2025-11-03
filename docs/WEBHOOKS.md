# Webhook Integration Guide

Complete guide to integrating PayQI webhooks for real-time payment notifications.

## Overview

Webhooks allow PayQI to notify your application when events happen, such as:
- Payment completed
- Payment failed
- Payment expired

## Setting Up Webhooks

### 1. Create Webhook Endpoint

Create a secure endpoint to receive webhooks:

**Python (Flask):**
```python
from flask import Flask, request
from payqi import verify_webhook_signature
import os

app = Flask(__name__)

@app.route('/webhooks/payqi', methods=['POST'])
def handle_webhook():
    payload = request.data
    signature = request.headers.get('X-PayQI-Signature')
    
    try:
        event = verify_webhook_signature(
            payload,
            signature,
            webhook_secret=os.getenv('PAYQI_WEBHOOK_SECRET')
        )
    except ValueError:
        return 'Invalid signature', 400
    
    # Process event
    process_webhook_event(event)
    
    return 'OK', 200
```

**Ruby (Sinatra):**
```ruby
require 'sinatra'
require 'payqi'

post '/webhooks/payqi' do
  payload = request.body.read
  signature = request.env['HTTP_X_PAYQI_SIGNATURE']
  
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
  
  process_webhook_event(event)
  status 200
  'OK'
end
```

**Node.js (Express):**
```javascript
const express = require('express');
const PayQI = require('payqi');

const app = express();
app.use(express.raw({ type: 'application/json' }));

app.post('/webhooks/payqi', (req, res) => {
  const signature = req.headers['x-payqi-signature'];
  
  try {
    const event = PayQI.webhooks.verify(
      req.body,
      signature,
      process.env.PAYQI_WEBHOOK_SECRET
    );
    
    processWebhookEvent(event);
    res.status(200).send('OK');
  } catch (err) {
    res.status(400).send('Invalid signature');
  }
});
```

### 2. Register Webhook URL

1. Go to Dashboard ? Settings ? Webhooks
2. Click "Add Webhook Endpoint"
3. Enter your URL: `https://yourdomain.com/webhooks/payqi`
4. Select events to subscribe to
5. Save your webhook secret

### 3. Test Webhook Locally

Use ngrok to test locally:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from ngrok.com

# Start your server
python app.py

# In another terminal, expose local server
ngrok http 5000

# Use the ngrok URL in webhook settings
# https://abc123.ngrok.io/webhooks/payqi
```

## Webhook Events

### Available Events

| Event | Description |
|-------|-------------|
| `payment.created` | Payment request created |
| `payment.pending` | Payment awaiting confirmation |
| `payment.completed` | Payment successfully received |
| `payment.failed` | Payment failed |
| `payment.expired` | Payment expired |

### Event Structure

```json
{
  "id": "evt_1234567890",
  "type": "payment.completed",
  "created": 1234567890,
  "data": {
    "id": "pay_abc123",
    "amount": 10.00,
    "currency": "XRP",
    "status": "completed",
    "pay_address": "rTest123...",
    "destination_tag": "123456",
    "tx_hash": "ABC123...",
    "metadata": {
      "order_id": "12345"
    }
  }
}
```

## Event Handling

### Complete Handler Example

```python
from payqi import verify_webhook_signature
from flask import Flask, request
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

def process_webhook_event(event):
    """Process webhook event"""
    
    event_type = event['type']
    payment = event['data']
    
    if event_type == 'payment.created':
        logger.info(f"Payment created: {payment['id']}")
        # Optional: Send notification to customer
        
    elif event_type == 'payment.pending':
        logger.info(f"Payment pending: {payment['id']}")
        # Update UI, show "awaiting payment"
        
    elif event_type == 'payment.completed':
        logger.info(f"Payment completed: {payment['id']}")
        handle_payment_completed(payment)
        
    elif event_type == 'payment.failed':
        logger.warning(f"Payment failed: {payment['id']}")
        handle_payment_failed(payment)
        
    elif event_type == 'payment.expired':
        logger.warning(f"Payment expired: {payment['id']}")
        handle_payment_expired(payment)

def handle_payment_completed(payment):
    """Handle completed payment"""
    order_id = payment['metadata']['order_id']
    
    # Update order status
    order = Order.get(order_id)
    order.status = 'paid'
    order.payment_id = payment['id']
    order.tx_hash = payment.get('tx_hash')
    order.save()
    
    # Send confirmation email
    send_confirmation_email(order.customer_email, order)
    
    # Update inventory
    for item in order.items:
        decrease_inventory(item.product_id, item.quantity)
    
    # Fulfill order
    fulfill_order(order)

def handle_payment_failed(payment):
    """Handle failed payment"""
    order_id = payment['metadata']['order_id']
    order = Order.get(order_id)
    order.status = 'payment_failed'
    order.save()
    
    # Notify customer
    send_payment_failure_email(order.customer_email, order)

def handle_payment_expired(payment):
    """Handle expired payment"""
    order_id = payment['metadata']['order_id']
    order = Order.get(order_id)
    order.status = 'expired'
    order.save()
    
    # Release inventory
    release_inventory(order)

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    payload = request.data
    signature = request.headers.get('X-PayQI-Signature')
    
    try:
        event = verify_webhook_signature(
            payload,
            signature,
            webhook_secret=os.getenv('PAYQI_WEBHOOK_SECRET')
        )
        process_webhook_event(event)
        return 'OK', 200
    except ValueError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return 'Invalid signature', 400
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return 'Error', 500
```

## Security

### Signature Verification

Always verify webhook signatures:

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison
    return hmac.compare_digest(
        expected_signature,
        signature
    )
```

### Replay Attacks

Prevent replay attacks by checking timestamps:

```python
from datetime import datetime, timedelta

def verify_timestamp(timestamp_header, max_age=300):
    """Verify webhook timestamp (5 minute window)"""
    timestamp = int(timestamp_header)
    now = int(datetime.now().timestamp())
    
    if abs(now - timestamp) > max_age:
        return False
    return True

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    # Check timestamp
    timestamp = request.headers.get('X-PayQI-Timestamp')
    if not verify_timestamp(timestamp):
        return 'Request too old', 400
    
    # Verify signature
    # ...
```

### Idempotency

Handle duplicate events:

```python
processed_events = set()

def is_event_processed(event_id):
    """Check if event was already processed"""
    return event_id in processed_events

def mark_event_processed(event_id):
    """Mark event as processed"""
    processed_events.add(event_id)
    # In production, use Redis or database

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    event = verify_webhook_signature(...)
    
    # Check if already processed
    if is_event_processed(event['id']):
        return 'Already processed', 200
    
    # Process event
    process_webhook_event(event)
    
    # Mark as processed
    mark_event_processed(event['id'])
    
    return 'OK', 200
```

## Testing

### Webhook Testing Tool

Use the PayQI webhook testing tool:

```python
from payqi import Client

client = Client(api_key=TEST_API_KEY)

# Send test webhook
client.webhooks.test_send(
    endpoint_id='wh_123',
    event_type='payment.completed'
)
```

### Local Testing with ngrok

```bash
# Terminal 1: Start your server
python app.py

# Terminal 2: Expose with ngrok
ngrok http 5000

# Copy the ngrok URL
# https://abc123.ngrok.io

# Terminal 3: Test webhook
curl -X POST https://abc123.ngrok.io/webhooks/payqi \
  -H "Content-Type: application/json" \
  -H "X-PayQI-Signature: test_signature" \
  -d '{
    "type": "payment.completed",
    "data": {"id": "pay_test_123"}
  }'
```

## Best Practices

1. ? Always verify signatures
2. ? Check timestamps to prevent replay attacks
3. ? Implement idempotency
4. ? Return 200 OK immediately, process asynchronously
5. ? Log all webhook events
6. ? Handle errors gracefully
7. ? Use HTTPS only
8. ? Process events asynchronously for performance

## Troubleshooting

### Webhook Not Receiving Events

1. Check webhook URL is accessible
2. Verify signature verification code
3. Check server logs for errors
4. Test with webhook testing tool

### Duplicate Events

1. Implement idempotency checking
2. Store processed event IDs
3. Return 200 OK even for duplicates

### Signature Verification Failing

1. Verify webhook secret is correct
2. Check payload encoding (should be raw bytes)
3. Ensure signature header name matches

## Support

- [Webhook Documentation](https://docs.payqi.com/webhooks)
- [Webhook Testing Tool](https://dashboard.payqi.com/webhooks/test)
- [Support Email](mailto:support@payqi.com)
