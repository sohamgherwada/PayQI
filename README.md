# PayQI - Stripe for Crypto

PayQI is a modern payment processing platform that enables merchants to accept cryptocurrency payments, including **XRP (XRP Ledger)** for daily products and services. Built with FastAPI and PostgreSQL, PayQI provides a simple API for merchants to integrate crypto payments into their applications.

## Features

- ?? **Secure Authentication**: JWT-based authentication for merchants
- ?? **Cryptocurrency Payments**: Accept payments in multiple cryptocurrencies including:
  - **XRP (XRP Ledger)** - Fast, low-cost transactions perfect for daily products and services
  - Bitcoin (BTC)
  - Ethereum (ETH)
  - Litecoin (LTC)
  - Bitcoin Cash (BCH)
  - Stablecoins (USDT, USDC)
  - And more via NOWPayments integration
- ?? **Transaction Management**: View and track all payment transactions
- ?? **RESTful API**: Clean, well-documented API endpoints
- ?? **Docker Support**: Easy deployment with Docker Compose
- ? **Fast & Scalable**: Built with FastAPI for high performance

## Why XRP?

XRP is ideal for daily products and services because:
- **Fast Transactions**: Settles in 3-5 seconds
- **Low Fees**: Typically less than $0.0002 per transaction
- **Scalable**: Can handle 1,500+ transactions per second
- **Eco-Friendly**: Energy-efficient consensus mechanism

## Prerequisites

- Docker and Docker Compose
- NOWPayments API account (for payment processing)
- PostgreSQL 15+ (or use the provided Docker setup)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd payqi
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+psycopg2://payqi:payqi@db:5432/payqi
   JWT_SECRET=your-secret-key-change-this-in-production
   JWT_EXPIRES_MINUTES=60
   NOWPAYMENTS_API_KEY=your-nowpayments-api-key
   NOWPAYMENTS_IPN_SECRET=your-ipn-secret
   BACKEND_CORS_ORIGINS=http://localhost:5173
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication

#### Register Merchant
```http
POST /api/register
Content-Type: application/json

{
  "email": "merchant@example.com",
  "password": "securepassword123"
}
```

#### Login
```http
POST /api/login
Content-Type: application/json

{
  "email": "merchant@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/me
Authorization: Bearer <access_token>
```

### Payments

#### Create Payment (including XRP)
```http
POST /api/payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 10.50,
  "currency": "xrp"
}
```

Response:
```json
{
  "payment_id": 1,
  "status": "pending",
  "provider_invoice_id": "invoice_123",
  "pay_address": "rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "checkout_url": "https://nowpayments.io/checkout/..."
}
```

**Supported currencies for daily payments:**
- `xrp` - XRP Ledger (recommended for daily products/services)
- `btc` - Bitcoin
- `eth` - Ethereum
- `ltc` - Litecoin
- `bch` - Bitcoin Cash
- `usdt` - Tether
- `usdc` - USD Coin
- `usd` - US Dollar
- `eur` - Euro

#### Get Payment Details
```http
GET /api/payments/{payment_id}
Authorization: Bearer <access_token>
```

#### Get All Transactions
```http
GET /api/transactions
Authorization: Bearer <access_token>
```

## Project Structure

```
.
??? backend/
?   ??? app/
?   ?   ??? routers/
?   ?   ?   ??? __init__.py
?   ?   ?   ??? auth.py          # Authentication endpoints
?   ?   ?   ??? payments.py      # Payment processing (includes XRP support)
?   ?   ?   ??? transactions.py  # Transaction history
?   ?   ??? config.py            # Application configuration
?   ?   ??? database.py          # Database setup
?   ?   ??? deps.py              # Dependency injection
?   ?   ??? main.py              # FastAPI application
?   ?   ??? models.py            # SQLAlchemy models
?   ?   ??? schemas.py           # Pydantic schemas
?   ?   ??? security.py          # Security utilities
?   ??? Dockerfile
?   ??? requirements.txt
??? docker-compose.yml
??? README.md
```

## Development

### Running Locally (without Docker)

1. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   - Install PostgreSQL locally or use Docker:
     ```bash
     docker run -d --name payqi-db -e POSTGRES_USER=payqi -e POSTGRES_PASSWORD=payqi -e POSTGRES_DB=payqi -p 5432:5432 postgres:15-alpine
     ```

3. **Update `.env` file**
   ```env
   DATABASE_URL=postgresql+psycopg2://payqi:payqi@localhost:5432/payqi
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## NOWPayments Setup

1. **Sign up** at [NOWPayments](https://nowpayments.io)
2. **Get your API key** from the dashboard
3. **Set up IPN (Instant Payment Notifications)** for webhook handling
4. **Add your API credentials** to the `.env` file

NOWPayments supports XRP and 200+ other cryptocurrencies, making it perfect for accepting daily product and service payments.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://payqi:payqi@db:5432/payqi` |
| `JWT_SECRET` | Secret key for JWT tokens | `change_me` |
| `JWT_EXPIRES_MINUTES` | JWT token expiration time | `60` |
| `NOWPAYMENTS_API_KEY` | NOWPayments API key | - |
| `NOWPAYMENTS_IPN_SECRET` | NOWPayments IPN secret | - |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:8000` |

## Payment Flow

1. **Merchant creates payment** via `/api/payments` with amount and currency (e.g., "xrp")
2. **Payment record created** in database with status "pending"
3. **Invoice created** with NOWPayments
4. **Payment address returned** to merchant
5. **Customer pays** using the provided address
6. **Status updates** via webhook (when implemented)
7. **Transaction recorded** in database

## XRP Payment Example

Here's a complete example of accepting an XRP payment:

```bash
# 1. Register a merchant
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "shop@example.com", "password": "securepass123"}'

# 2. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "shop@example.com", "password": "securepass123"}' \
  | jq -r '.access_token')

# 3. Create XRP payment
curl -X POST http://localhost:8000/api/payments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 25.50, "currency": "xrp"}'

# Response includes payment address for customer to send XRP to
```

## Security Considerations

- Use strong `JWT_SECRET` in production
- Enable HTTPS in production
- Implement rate limiting (already included)
- Validate all inputs
- Use environment variables for secrets
- Regularly update dependencies
- Implement webhook signature verification for IPN

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: Make sure to configure your NOWPayments account properly and test with small amounts before processing real payments in production.
