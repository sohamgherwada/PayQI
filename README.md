# PayQI - Stripe for Crypto

PayQI is a modern payment gateway API that enables merchants to accept cryptocurrency payments, including Bitcoin, Ethereum, XRP, and other major cryptocurrencies. Built with FastAPI, it provides a Stripe-like experience for crypto payments.

## Features

- ?? **Secure Authentication** - JWT-based authentication for merchants
- ?? **Multi-Currency Support** - Accept payments in BTC, ETH, XRP, USDT, USDC, LTC, DOGE, and more
- ?? **XRP Payments** - Direct XRP payment support with destination tags
- ?? **Transaction Management** - Track and manage all payment transactions
- ?? **Easy Integration** - RESTful API designed for easy integration
- ?? **Docker Ready** - Complete Docker setup for easy deployment

## Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- XRP (Ripple)
- Tether (USDT)
- USD Coin (USDC)
- Litecoin (LTC)
- Dogecoin (DOGE)

## Architecture

PayQI consists of:

- **Backend API** (Python/FastAPI) - REST API for handling payments, authentication, and transactions
- **Webhook Service** (Ruby/Sinatra) - Secure webhook processing for payment notifications
- **CLI Tool** (Ruby/Thor) - Command-line interface for merchants (Shopify CLI style)
- **Database** - PostgreSQL database for storing merchant and payment data
- **Payment Providers**:
  - **NOWPayments** - For BTC, ETH, USDT, USDC, LTC, DOGE
  - **Direct XRP** - Native XRP payment support via XRP Ledger

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Ruby 3.2+ (for Ruby services/CLI)
- PostgreSQL 15+ (if running database separately)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd payqi
   ```

2. **Create a `.env` file** in the root directory:
   ```env
   # Database
   DATABASE_URL=postgresql+psycopg2://payqi:payqi@db:5432/payqi

   # Security
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   JWT_EXPIRES_MINUTES=60

   # NOWPayments (for BTC, ETH, etc.)
   NOWPAYMENTS_API_KEY=your-nowpayments-api-key
   NOWPAYMENTS_IPN_SECRET=your-nowpayments-ipn-secret

   # XRP Configuration
   XRP_WALLET_ADDRESS=rYourXRPWalletAddressHere

   # CORS
   BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

   # Frontend
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - Python API Base URL: `http://localhost:8000`
   - Python API Documentation: `http://localhost:8000/docs`
   - Python API Health: `http://localhost:8000/health`
   - Ruby Webhook Service: `http://localhost:4567`
   - Webhook Service Health: `http://localhost:4567/health`

5. **Try the Ruby CLI** (optional)
   ```bash
   cd ruby_services
   bundle install
   chmod +x cli/payqi_cli.rb
   ./cli/payqi_cli.rb help
   ```

### Local Development

1. **Set up a virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (create `.env` file in `backend/` directory)

4. **Run the database** (using Docker)
   ```bash
   docker-compose up db -d
   ```

5. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

### Authentication

#### Register a Merchant
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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current Merchant
```http
GET /api/me
Authorization: Bearer <access_token>
```

### Payments

#### Create a Payment (XRP Example)
```http
POST /api/payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 10.00,
  "currency": "XRP"
}
```

Response:
```json
{
  "payment_id": 1,
  "status": "pending",
  "provider_invoice_id": "xrp_1_123456",
  "pay_address": "rYourXRPWalletAddressHere",
  "checkout_url": null
}
```

**For XRP payments:**
- The `pay_address` is your configured XRP wallet address
- The `provider_invoice_id` contains the destination tag in the format `xrp_{payment_id}_{destination_tag}`
- Customers should send XRP to the provided address with the destination tag specified in the `provider_invoice_id`
- The raw payload contains additional information including the XRP amount

#### Create a Payment (Other Cryptocurrencies)
```http
POST /api/payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 10.00,
  "currency": "BTC"
}
```

#### Get Payment Details
```http
GET /api/payments/{payment_id}
Authorization: Bearer <access_token>
```

#### Get All Transactions
```http
GET /api/transactions?skip=0&limit=100
Authorization: Bearer <access_token>
```

## XRP Payment Setup

### 1. Configure XRP Wallet

Set the `XRP_WALLET_ADDRESS` environment variable to your XRP wallet address:
```env
XRP_WALLET_ADDRESS=rYourXRPWalletAddressHere
```

**Important:** 
- This should be a dedicated wallet address for receiving payments
- Keep the wallet seed/private key secure and never commit it to version control
- In production, consider using a hardware wallet or secure key management service

### 2. How XRP Payments Work

1. **Merchant creates a payment** with currency "XRP"
2. **System generates a unique destination tag** based on merchant and payment IDs
3. **Customer receives:**
   - XRP wallet address (your configured address)
   - Destination tag (unique identifier for the payment)
   - Amount in XRP (converted from USD)
4. **Customer sends XRP** to the address with the destination tag
5. **System monitors** the XRP Ledger for transactions (TODO: implement transaction monitoring)

### 3. Monitoring XRP Transactions

To verify XRP payments, you can:
- Use the XRP Ledger API to check for transactions
- Implement a webhook or polling service to monitor payments
- Use libraries like `xrpl-py` for Python integration

Example using XRP Ledger API:
```bash
curl https://xrplcluster.com/accounts/rYourXRPWalletAddressHere/transactions
```

### 4. Production Recommendations

For production XRP payment verification:
1. **Install xrpl-py** (optional but recommended):
   ```bash
   pip install xrpl-py
   ```

2. **Implement transaction monitoring** using XRP Ledger WebSocket API
3. **Set up automated payment verification** when transactions are detected
4. **Implement payment expiration** for pending payments

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql+psycopg2://payqi:payqi@db:5432/payqi` |
| `JWT_SECRET` | Secret key for JWT token signing | Yes | `change_me` |
| `JWT_EXPIRES_MINUTES` | JWT token expiration time | No | `60` |
| `NOWPAYMENTS_API_KEY` | NOWPayments API key | For non-XRP crypto | - |
| `NOWPAYMENTS_IPN_SECRET` | NOWPayments IPN secret | For webhooks | - |
| `XRP_WALLET_ADDRESS` | XRP wallet address for receiving payments | For XRP | - |
| `BACKEND_CORS_ORIGINS` | CORS allowed origins | No | `http://localhost:5173` |

## Project Structure

```
.
??? backend/                      # Python FastAPI backend
?   ??? app/
?   ?   ??? routers/             # API endpoints
?   ?   ?   ??? auth.py          # Authentication endpoints
?   ?   ?   ??? payments.py      # Payment creation and management
?   ?   ?   ??? transactions.py  # Transaction history
?   ?   ??? middleware/           # Security middleware
?   ?   ??? utils/               # Utilities (logging, cache)
?   ?   ??? config.py            # Configuration settings
?   ?   ??? database.py          # Database setup
?   ?   ??? deps.py              # Dependency injection
?   ?   ??? main.py              # FastAPI application
?   ?   ??? models.py            # SQLAlchemy models
?   ?   ??? schemas.py           # Pydantic schemas
?   ?   ??? security.py          # Security utilities
?   ??? Dockerfile
?   ??? requirements.txt
??? ruby_services/                # Ruby microservices
?   ??? webhook_service.rb       # Sinatra webhook processor
?   ??? config.ru                # Rack configuration
?   ??? lib/
?   ?   ??? payqi_client.rb      # Ruby API client library
?   ??? cli/
?   ?   ??? payqi_cli.rb         # CLI tool (Thor-based)
?   ??? Gemfile                  # Ruby dependencies
?   ??? Dockerfile               # Ruby service Dockerfile
?   ??? README.md                # Ruby services documentation
??? docker-compose.yml
??? README.md
```

## Ruby Services

PayQI includes Ruby microservices demonstrating Shopify-relevant skills:

- **Webhook Service** - Sinatra-based service for secure webhook processing
- **Ruby API Client** - Clean Ruby library for API interactions (similar to Shopify API gems)
- **CLI Tool** - Shopify CLI-style command-line interface

See [`ruby_services/README.md`](ruby_services/README.md) for detailed documentation.

### Quick Ruby CLI Usage

```bash
cd ruby_services
bundle install

# Register merchant
./cli/payqi_cli.rb register merchant@example.com password123

# Login (token saved to .env)
./cli/payqi_cli.rb login merchant@example.com password123

# Create XRP payment
./cli/payqi_cli.rb payment 10.00 XRP

# View all transactions
./cli/payqi_cli.rb transactions
```

## Development

### Running Tests

```bash
# TODO: Add tests
pytest
```

### Code Formatting

```bash
# TODO: Add formatting configuration
black .
isort .
```

## Security Considerations

- ?? Always use strong `JWT_SECRET` in production
- ?? Store sensitive keys in environment variables, never in code
- ??? Enable HTTPS in production
- ?? Implement rate limiting (already included)
- ? Validate and sanitize all user inputs
- ?? Use secure password hashing (bcrypt is already implemented)

## Production Deployment

### Before Going to Production

1. **Update JWT_SECRET** - Generate a secure random string
2. **Configure CORS** - Set `BACKEND_CORS_ORIGINS` to your frontend domain
3. **Set up SSL/TLS** - Use HTTPS for all API calls
4. **Configure XRP wallet** - Set up a dedicated XRP wallet and secure the private key
5. **Set up monitoring** - Implement transaction monitoring for XRP payments
6. **Enable webhooks** - Configure payment webhooks for production
7. **Set up backups** - Regular database backups
8. **Use secrets management** - Consider using AWS Secrets Manager, HashiCorp Vault, etc.

### Recommended Production Stack

- **Web Server**: Nginx or Traefik as reverse proxy
- **Application**: FastAPI with Gunicorn/Uvicorn workers
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for rate limiting and session management
- **Monitoring**: Prometheus + Grafana or similar
- **Logging**: Centralized logging solution

## API Rate Limiting

The API includes basic rate limiting (100 requests per minute per IP). This can be adjusted in `main.py`:

```python
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Specify your license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Roadmap

- [ ] Enhanced XRP transaction monitoring
- [ ] Support for more cryptocurrencies
- [ ] Webhook system for payment status updates
- [ ] Admin dashboard
- [ ] Mobile SDKs
- [ ] Recurring payments/subscriptions
- [ ] Multi-signature wallet support
