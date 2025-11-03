# PayQI Security Guide

Comprehensive security practices for integrating PayQI safely.

## Table of Contents

1. [API Key Management](#api-key-management)
2. [Webhook Security](#webhook-security)
3. [Data Protection](#data-protection)
4. [Network Security](#network-security)
5. [Compliance](#compliance)
6. [Incident Response](#incident-response)

## API Key Management

### Key Types

**Test Keys** (`sk_test_...`)
- Use for development and testing
- No real payments processed
- Can be regenerated anytime

**Live Keys** (`sk_live_...`)
- Use for production
- Process real payments
- Rotate regularly

### Best Practices

? **DO:**

```python
# Store in environment variables
import os
api_key = os.getenv('PAYQI_API_KEY')

# Use secret management services
# AWS Secrets Manager
import boto3
secrets = boto3.client('secretsmanager')
api_key = secrets.get_secret_value(SecretId='payqi-api-key')['SecretString']

# HashiCorp Vault
import hvac
client = hvac.Client(url='https://vault.example.com')
api_key = client.secrets.kv.v2.read_secret_version(path='payqi')['data']['data']['api_key']
```

? **DON'T:**

```python
# Never hardcode keys
api_key = 'sk_live_51abc123...'  # ? BAD!

# Never commit to version control
# .env file with keys should be in .gitignore
PAYQI_API_KEY=sk_live_...  # ? BAD if committed

# Never share in logs
logger.info(f"API Key: {api_key}")  # ? BAD!
```

### Key Rotation

Rotate keys regularly:

```python
# 1. Create new key
new_key = create_new_api_key()

# 2. Update application
os.environ['PAYQI_API_KEY'] = new_key

# 3. Wait 24 hours for webhooks to update
time.sleep(86400)

# 4. Revoke old key
revoke_api_key(old_key)
```

## Webhook Security

### Signature Verification

Always verify webhook signatures:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)
```

### Webhook Endpoint Security

```python
from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/webhooks/payqi', methods=['POST'])
def handle_webhook():
    # 1. Verify signature
    signature = request.headers.get('X-PayQI-Signature')
    if not verify_webhook_signature(
        request.data,
        signature,
        WEBHOOK_SECRET
    ):
        abort(400)
    
    # 2. Verify timestamp (prevent replay attacks)
    timestamp = request.headers.get('X-PayQI-Timestamp')
    if is_timestamp_old(timestamp, max_age=300):  # 5 minutes
        abort(400)
    
    # 3. Process event
    event = json.loads(request.data)
    process_event(event)
    
    return 'OK', 200
```

### Idempotency

Handle duplicate webhooks:

```python
# Store processed event IDs
processed_events = set()

def handle_webhook_event(event):
    event_id = event['id']
    
    # Check if already processed
    if event_id in processed_events:
        return  # Already handled
    
    # Process event
    process_payment(event['data'])
    
    # Mark as processed
    processed_events.add(event_id)
```

## Data Protection

### PCI Compliance

PayQI handles all payment data. You never touch credit card numbers or private keys.

? **Safe to Store:**
- Payment IDs
- Transaction amounts
- Payment status
- Customer emails (with permission)

? **Never Store:**
- Private keys
- Seed phrases
- API keys
- Wallet credentials

### Customer Data

```python
# ? Good: Store minimal data
customer = {
    'email': 'customer@example.com',
    'payment_id': payment.id
}

# ? Bad: Don't store sensitive data
customer = {
    'email': 'customer@example.com',
    'private_key': '...',  # NEVER!
    'seed_phrase': '...'   # NEVER!
}
```

### Encryption at Rest

```python
# Encrypt sensitive data before storing
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted_data = cipher.encrypt(b"sensitive data")

# Decrypt when needed
decrypted_data = cipher.decrypt(encrypted_data)
```

## Network Security

### HTTPS Only

Always use HTTPS:

```python
# ? Production
api_url = 'https://api.payqi.com'

# ? Never in production
api_url = 'http://api.payqi.com'  # Insecure!
```

### Certificate Pinning

For extra security, pin certificates:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_verify_locations('payqi_cert.pem')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', SSLAdapter())
```

### Rate Limiting

Implement client-side rate limiting:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=100):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(100)
def create_payment(client, amount, currency):
    return client.payments.create(amount=amount, currency=currency)
```

## Compliance

### GDPR

If you're in the EU or serving EU customers:

? **Do:**
- Get explicit consent for data collection
- Allow customers to delete their data
- Encrypt personal data
- Document data processing

```python
# Record consent
customer.consent_given = True
customer.consent_date = datetime.now()
customer.save()

# Allow deletion
def delete_customer_data(customer_id):
    Customer.objects.filter(id=customer_id).delete()
    Payment.objects.filter(customer_id=customer_id).delete()
```

### PCI DSS

PayQI is PCI compliant. You don't need PCI certification if you:
- Don't store credit card numbers
- Don't process payments directly
- Use PayQI's secure payment forms

### KYC/AML

Follow local regulations:
- Verify customer identity
- Monitor transactions
- Report suspicious activity

## Incident Response

### Key Compromise

If your API key is compromised:

1. **Immediately revoke the key**
   ```python
   client.keys.revoke(key_id)
   ```

2. **Generate new key**
   ```python
   new_key = client.keys.create()
   ```

3. **Update all services**
   - Update environment variables
   - Redeploy applications
   - Update CI/CD secrets

4. **Review logs**
   - Check for unauthorized access
   - Review recent transactions
   - Notify affected customers

### Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] Webhook signatures verified
- [ ] HTTPS used for all API calls
- [ ] Rate limiting implemented
- [ ] Error messages don't leak secrets
- [ ] Logs don't contain sensitive data
- [ ] Regular security audits
- [ ] Incident response plan ready

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Payment Card Industry Data Security Standard](https://www.pcisecuritystandards.org/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

## Report Security Issues

Found a security vulnerability? Please email:
- **security@payqi.com**
- Don't open public GitHub issues for security bugs

We'll respond within 24 hours and work with you to resolve the issue.
