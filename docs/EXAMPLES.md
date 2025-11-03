# PayQI Code Examples

Real-world examples for common integration scenarios.

## Table of Contents

1. [E-commerce Checkout](#e-commerce-checkout)
2. [Subscription Payments](#subscription-payments)
3. [Donation Button](#donation-button)
4. [Marketplace Payments](#marketplace-payments)
5. [Invoicing](#invoicing)

## E-commerce Checkout

### Python (Flask)

```python
from flask import Flask, request, jsonify, render_template
from payqi import Client
import os

app = Flask(__name__)
payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

@app.route('/')
def index():
    return render_template('checkout.html')

@app.route('/api/checkout', methods=['POST'])
def create_checkout():
    data = request.json
    cart_items = data['items']
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Create payment
    payment = payqi.payments.create(
        amount=total,
        currency='XRP',
        description=f'Order with {len(cart_items)} items',
        metadata={
            'order_id': generate_order_id(),
            'items': cart_items
        }
    )
    
    return jsonify({
        'payment_id': payment.id,
        'xrp_address': payment.pay_address,
        'destination_tag': payment.destination_tag,
        'amount_xrp': payment.amount_xrp,
        'status': payment.status
    })

@app.route('/api/payment/<payment_id>/status')
def payment_status(payment_id):
    payment = payqi.payments.retrieve(payment_id)
    return jsonify({
        'status': payment.status,
        'completed': payment.status == 'completed'
    })

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    signature = request.headers.get('X-PayQI-Signature')
    
    try:
        event = payqi.webhooks.verify(request.data, signature)
    except ValueError:
        return 'Invalid signature', 400
    
    if event.type == 'payment.completed':
        payment = event.data
        order_id = payment.metadata['order_id']
        
        # Mark order as paid
        order = Order.get(order_id)
        order.status = 'paid'
        order.save()
        
        # Send confirmation email
        send_confirmation_email(order.customer_email, order)
    
    return 'OK', 200
```

### React Frontend

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function Checkout({ cart }) {
  const [payment, setPayment] = useState(null);
  const [status, setStatus] = useState('pending');

  const createPayment = async () => {
    const response = await axios.post('/api/checkout', {
      items: cart.items
    });
    
    setPayment(response.data);
    pollPaymentStatus(response.data.payment_id);
  };

  const pollPaymentStatus = async (paymentId) => {
    const interval = setInterval(async () => {
      const response = await axios.get(`/api/payment/${paymentId}/status`);
      
      if (response.data.completed) {
        setStatus('completed');
        clearInterval(interval);
        // Redirect to success page
        window.location.href = '/order-success';
      }
    }, 5000); // Poll every 5 seconds
  };

  return (
    <div>
      {!payment ? (
        <button onClick={createPayment}>Pay with XRP</button>
      ) : (
        <div>
          <h2>Pay with XRP</h2>
          <p>Amount: {payment.amount_xrp} XRP</p>
          <p>Address: {payment.xrp_address}</p>
          <p>Destination Tag: {payment.destination_tag}</p>
          <p>Status: {status}</p>
        </div>
      )}
    </div>
  );
}
```

## Subscription Payments

```python
from payqi import Client
import schedule
import time

payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

def process_subscriptions():
    """Process monthly subscriptions"""
    subscriptions = Subscription.objects.filter(
        status='active',
        next_billing_date=lte=datetime.now()
    )
    
    for subscription in subscriptions:
        try:
            # Create payment
            payment = payqi.payments.create(
                amount=subscription.amount,
                currency='XRP',
                description=f'Subscription for {subscription.user.email}',
                metadata={
                    'subscription_id': subscription.id,
                    'user_id': subscription.user.id
                }
            )
            
            # Update subscription
            subscription.last_payment_id = payment.id
            subscription.next_billing_date = datetime.now() + timedelta(days=30)
            subscription.save()
            
        except Exception as e:
            # Handle payment failure
            subscription.status = 'past_due'
            subscription.save()
            notify_user_of_failure(subscription.user)

# Run daily at midnight
schedule.every().day.at("00:00").do(process_subscriptions)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Donation Button

```python
from flask import Flask, request, jsonify
from payqi import Client

app = Flask(__name__)
payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

@app.route('/donate', methods=['POST'])
def donate():
    amount = float(request.json['amount'])
    donor_name = request.json.get('name', 'Anonymous')
    
    payment = payqi.payments.create(
        amount=amount,
        currency='XRP',
        description=f'Donation from {donor_name}',
        metadata={
            'type': 'donation',
            'donor_name': donor_name
        }
    )
    
    return jsonify({
        'payment_id': payment.id,
        'xrp_address': payment.pay_address,
        'destination_tag': payment.destination_tag,
        'amount_xrp': payment.amount_xrp
    })

@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    signature = request.headers.get('X-PayQI-Signature')
    event = payqi.webhooks.verify(request.data, signature)
    
    if event.type == 'payment.completed':
        payment = event.data
        donor_name = payment.metadata.get('donor_name', 'Anonymous')
        
        # Record donation
        Donation.create(
            amount=payment.amount,
            donor_name=donor_name,
            payment_id=payment.id,
            completed_at=datetime.now()
        )
        
        # Send thank you email
        send_thank_you_email(donor_name, payment.amount)
    
    return 'OK', 200
```

## Marketplace Payments

```python
# Split payment between platform and seller
from payqi import Client

payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

def process_marketplace_payment(order):
    total_amount = order.total
    platform_fee = total_amount * 0.10  # 10% platform fee
    seller_amount = total_amount - platform_fee
    
    # Create payment
    payment = payqi.payments.create(
        amount=total_amount,
        currency='XRP',
        description=f'Marketplace order #{order.id}',
        metadata={
            'order_id': order.id,
            'seller_id': order.seller_id,
            'platform_fee': platform_fee,
            'seller_amount': seller_amount
        }
    )
    
    return payment

# Webhook handler
@app.route('/webhooks/payqi', methods=['POST'])
def webhook():
    signature = request.headers.get('X-PayQI-Signature')
    event = payqi.webhooks.verify(request.data, signature)
    
    if event.type == 'payment.completed':
        payment = event.data
        order = Order.get(payment.metadata['order_id'])
        
        # Transfer to seller
        seller = Seller.get(payment.metadata['seller_id'])
        seller.balance += payment.metadata['seller_amount']
        seller.save()
        
        # Record platform fee
        PlatformRevenue.create(
            amount=payment.metadata['platform_fee'],
            order_id=order.id,
            payment_id=payment.id
        )
        
        # Mark order as paid
        order.status = 'paid'
        order.save()
```

## Invoicing

```python
from payqi import Client
from datetime import datetime, timedelta

payqi = Client(api_key=os.getenv('PAYQI_API_KEY'))

def create_invoice(customer, items, due_date=None):
    """Create an invoice"""
    total = sum(item['price'] * item['quantity'] for item in items)
    
    invoice = Invoice.create(
        customer=customer,
        items=items,
        total=total,
        due_date=due_date or (datetime.now() + timedelta(days=30)),
        status='pending'
    )
    
    # Create payment link
    payment = payqi.payments.create(
        amount=total,
        currency='XRP',
        description=f'Invoice #{invoice.number}',
        metadata={
            'invoice_id': invoice.id,
            'customer_id': customer.id
        }
    )
    
    invoice.payment_id = payment.id
    invoice.save()
    
    # Send invoice email with payment details
    send_invoice_email(customer, invoice, payment)
    
    return invoice, payment

def check_overdue_invoices():
    """Check for overdue invoices"""
    overdue = Invoice.objects.filter(
        status='pending',
        due_date__lt=datetime.now()
    )
    
    for invoice in overdue:
        # Send reminder
        send_payment_reminder(invoice.customer, invoice)
        
        # Update status
        invoice.status = 'overdue'
        invoice.save()
```

## Error Handling Best Practices

```python
from payqi import Client
from payqi.errors import APIError, RateLimitError, InvalidRequestError
import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1):
    """Decorator for retrying API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
                except (APIError, InvalidRequestError) as e:
                    # Don't retry on client errors
                    raise
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_with_backoff()
def create_payment_safe(client, amount, currency):
    return client.payments.create(amount=amount, currency=currency)
```

## Testing Examples

```python
import pytest
from payqi import Client
from unittest.mock import Mock, patch

@pytest.fixture
def mock_payqi_client():
    client = Mock(spec=Client)
    client.payments.create.return_value = Mock(
        id='pay_123',
        status='pending',
        pay_address='rTest123',
        destination_tag='123456'
    )
    return client

def test_create_payment(mock_payqi_client):
    payment = mock_payqi_client.payments.create(
        amount=10.00,
        currency='XRP'
    )
    assert payment.id == 'pay_123'
    assert payment.status == 'pending'
```

## More Examples

- [Full E-commerce Integration](https://github.com/payqi/examples/tree/main/ecommerce)
- [SaaS Subscription Example](https://github.com/payqi/examples/tree/main/saas)
- [Marketplace Integration](https://github.com/payqi/examples/tree/main/marketplace)
- [Mobile App Integration](https://github.com/payqi/examples/tree/main/mobile)
