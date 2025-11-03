# PayQI Testing Guide

Complete guide to testing the PayQI payment gateway.

## Quick Start

### Run All Tests

```bash
# Python tests
cd backend && ./run_tests.sh

# Ruby tests
cd ruby_services && ./run_tests.sh

# Integration tests (requires running API)
./test_api.sh
```

## Test Types

### 1. Unit Tests

Fast, isolated tests for individual components.

**Python:**
```bash
cd backend
pytest tests/test_auth.py::TestAuth::test_login_success -v
```

**Ruby:**
```bash
cd ruby_services
bundle exec rspec spec/payqi_client_spec.rb:10
```

### 2. Integration Tests

Test the full API stack with live endpoints.

```bash
# Start API
docker-compose up -d backend db

# Wait for API to be ready
sleep 5

# Run integration tests
./test_api.sh
```

### 3. Manual Testing

#### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Create payment (replace TOKEN)
curl -X POST http://localhost:8000/api/payments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"amount":10.00,"currency":"XRP"}'
```

#### Using Ruby CLI

```bash
cd ruby_services
bundle install

# Register
./cli/payqi_cli.rb register test@example.com password123

# Login
./cli/payqi_cli.rb login test@example.com password123

# Create payment
./cli/payqi_cli.rb payment 10.00 XRP
```

#### Using Python Client

```python
import requests

API_URL = "http://localhost:8000"

# Register
response = requests.post(f"{API_URL}/api/register", json={
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# Login
response = requests.post(f"{API_URL}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Create payment
response = requests.post(
    f"{API_URL}/api/payments",
    headers={"Authorization": f"Bearer {token}"},
    json={"amount": 10.00, "currency": "XRP"}
)
print(response.json())
```

## Test Database

Python tests use an in-memory SQLite database that is:
- ? Created fresh for each test
- ? Isolated from other tests
- ? Fast and requires no setup
- ? Automatically cleaned up

## Test Fixtures

### Python Fixtures

Available in `backend/tests/conftest.py`:

- `db` - Database session
- `client` - Test HTTP client
- `test_merchant` - Pre-created merchant
- `test_merchant_token` - JWT token
- `authenticated_client` - Client with auth headers
- `test_payment` - Pre-created payment

### Ruby Fixtures

RSpec uses `before` blocks and doubles for test setup:

```ruby
let(:secret) { 'test_secret_key' }
let(:payload) { { payment_id: '123' }.to_json }
```

## Mocking External Services

Tests mock external API calls to:
- ? Run faster
- ? Avoid API costs
- ? Test error scenarios
- ? Run offline

**Python:**
```python
@patch('app.routers.payments.create_nowpayments_invoice')
def test_payment(mock_invoice):
    mock_invoice.return_value = {"payment_id": "123"}
    # Test code...
```

**Ruby:**
```ruby
connection_double = double('connection')
allow(Faraday).to receive(:new).and_return(connection_double)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest

  ruby-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
      - run: |
          cd ruby_services
          bundle install
          bundle exec rspec
```

## Test Coverage Goals

- Authentication: 100%
- Payment creation: 95%+
- Transaction queries: 90%+
- Security utilities: 100%
- Error handling: 85%+

## Debugging Tests

### Python

```bash
# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Run with pdb debugger
pytest --pdb

# Run last failed tests
pytest --lf
```

### Ruby

```bash
# Run with verbose output
bundle exec rspec --format documentation

# Run with pry debugger (add binding.pry in test)
bundle exec rspec

# Run last failed tests
bundle exec rspec --only-failures
```

## Common Issues

### Database Connection Errors

**Problem:** Tests fail with database connection errors

**Solution:**
- Tests use in-memory SQLite, no connection needed
- Check that `conftest.py` is properly configured

### Import Errors

**Problem:** `ModuleNotFoundError` in tests

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend
pytest
```

### Token Expiration

**Problem:** Tests fail with 401 Unauthorized

**Solution:**
- Test tokens are created fresh in fixtures
- Check that JWT_SECRET is set in test environment

## Best Practices

1. ? Write tests before fixing bugs (TDD)
2. ? Keep tests fast (< 1 second per test)
3. ? Use descriptive test names
4. ? Test both success and failure cases
5. ? Mock external services
6. ? Clean up test data
7. ? Run tests before committing
