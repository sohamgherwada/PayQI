# PayQI Ruby Services

Ruby microservices and tools for the PayQI payment gateway. Built with Ruby to demonstrate skills relevant to Shopify development.

## ?? Features

- **Webhook Processing Service** - Secure webhook handling with signature verification
- **Ruby API Client** - Clean Ruby client library for the PayQI API
- **CLI Tool** - Command-line interface for merchant operations (Shopify CLI style)

## ?? Services

### 1. Webhook Service (Sinatra)

A lightweight Ruby web service for processing payment webhooks from NOWPayments and XRP monitoring services.

**Features:**
- ? NOWPayments webhook signature verification
- ? XRP transaction validation
- ? Secure request handling
- ? Structured logging
- ? Error handling and retries

**Endpoints:**
- `GET /health` - Health check
- `POST /webhooks/nowpayments` - Process NOWPayments webhooks
- `POST /webhooks/xrp` - Process XRP payment notifications

### 2. Ruby API Client

A clean, Shopify-style Ruby client for interacting with the PayQI API.

```ruby
require 'payqi_client'

client = PayQI::Client.new(
  api_url: 'http://localhost:8000',
  access_token: 'your_token_here'
)

# Create a payment
payment = client.create_payment(
  amount: 10.00,
  currency: 'XRP',
  access_token: 'your_token'
)

# Get transactions
transactions = client.get_transactions(access_token: 'your_token')
```

### 3. CLI Tool (Thor-based)

A command-line tool for merchants to interact with PayQI, similar to Shopify CLI.

```bash
# Register new merchant
./cli/payqi_cli.rb register merchant@example.com password123

# Login
./cli/payqi_cli.rb login merchant@example.com password123

# Create payment
./cli/payqi_cli.rb payment 10.00 XRP

# Check payment status
./cli/payqi_cli.rb status 123

# List transactions
./cli/payqi_cli.rb transactions

# Get merchant info
./cli/payqi_cli.rb merchant
```

## ??? Setup

### Prerequisites

- Ruby 3.2+
- Bundler

### Installation

```bash
cd ruby_services
bundle install
```

### Environment Variables

Create a `.env` file:

```env
PYTHON_API_URL=http://localhost:8000
NOWPAYMENTS_IPN_SECRET=your_secret_here
WEBHOOK_PORT=4567
DEBUG=false
PAYQI_TOKEN=your_access_token  # For CLI usage
```

### Running Locally

**Webhook Service:**
```bash
bundle exec ruby webhook_service.rb
# or with Puma
bundle exec puma -p 4567 config.ru
```

**CLI Tool:**
```bash
chmod +x cli/payqi_cli.rb
./cli/payqi_cli.rb help
```

### Running with Docker

The Ruby services are included in the main `docker-compose.yml`. To run:

```bash
docker-compose up webhook-service
```

## ??? Architecture

This Ruby service architecture is inspired by Shopify's microservices approach:

1. **Webhook Service** - Handles incoming webhooks securely
2. **API Client Library** - Reusable Ruby gem for API interactions
3. **CLI Tool** - Developer-friendly command-line interface

### Why Ruby for This?

- **Shopify uses Ruby/Rails** - Demonstrates relevant skills
- **Great for webhooks** - Ruby excels at HTTP/webhook processing
- **CLI tools** - Shopify has excellent CLI tools (Shopify CLI)
- **Developer experience** - Clean, readable code
- **Ecosystem** - Excellent libraries (Sinatra, Faraday, Thor)

## ?? Security Features

- Webhook signature verification (HMAC-SHA512)
- Input validation and sanitization
- Secure request handling
- Rack protection middleware
- Request timeouts

## ?? Code Structure

```
ruby_services/
??? webhook_service.rb    # Main Sinatra webhook service
??? config.ru            # Rack configuration
??? lib/
?   ??? payqi_client.rb  # API client library
??? cli/
?   ??? payqi_cli.rb     # CLI tool (Thor-based)
??? Gemfile              # Dependencies
??? Dockerfile           # Docker configuration
??? README.md           # This file
```

## ?? Testing

```bash
# Run RSpec tests (when added)
bundle exec rspec

# Run RuboCop (linting)
bundle exec rubocop
```

## ?? Integration

The Ruby webhook service integrates with the Python FastAPI backend:

1. **NOWPayments** sends webhook ? Ruby service verifies signature ? Forwards to Python API
2. **XRP Monitor** sends transaction ? Ruby service validates ? Forwards to Python API
3. **CLI Tool** talks directly to Python API using Ruby client

## ?? Shopify-Relevant Skills Demonstrated

- ? **Ruby/Ruby on Rails ecosystem** - Sinatra, Thor, Rack
- ? **Webhook processing** - Critical at Shopify
- ? **API clients** - Similar to Shopify API gems
- ? **CLI tools** - Like Shopify CLI
- ? **Microservices architecture** - Ruby services alongside Python
- ? **Security best practices** - Signature verification, validation
- ? **Clean code** - Ruby conventions and style

## ?? Example Usage

### Using the CLI

```bash
# 1. Register a merchant
./cli/payqi_cli.rb register shop@example.com securepass123

# 2. Login and get token
./cli/payqi_cli.rb login shop@example.com securepass123
# (Token saved to .env automatically)

# 3. Create an XRP payment
./cli/payqi_cli.rb payment 25.50 XRP

# 4. Check status
./cli/payqi_cli.rb status 1

# 5. View all transactions
./cli/payqi_cli.rb transactions
```

### Using the Ruby Client

```ruby
require_relative 'lib/payqi_client'

client = PayQI::Client.new(api_url: 'http://localhost:8000')

# Login
result = client.login(email: 'shop@example.com', password: 'pass')
token = result['access_token']

# Create payment
payment = client.create_payment(
  amount: 10.00,
  currency: 'XRP',
  access_token: token
)

puts "Payment created: #{payment['payment_id']}"
puts "Pay address: #{payment['pay_address']}"
```

## ?? Production Considerations

- Add background job processing (Sidekiq)
- Implement Redis for caching
- Add monitoring and alerting
- Set up proper logging aggregation
- Use environment-specific configurations
- Add rate limiting
- Implement circuit breakers for API calls

## ?? Resources

- [Sinatra Documentation](http://sinatrarb.com/)
- [Shopify API Docs](https://shopify.dev/docs/api)
- [Ruby Style Guide](https://rubystyle.guide/)
- [Thor CLI Framework](https://github.com/rails/thor)
