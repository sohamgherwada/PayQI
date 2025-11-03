# PayQI Backend Tests

Comprehensive test suite for the PayQI FastAPI backend.

## Running Tests

### Quick Start

```bash
cd backend
./run_tests.sh
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::TestAuth::test_login_success

# Run with coverage
pytest --cov=app --cov-report=html
```

## Test Structure

```
tests/
??? __init__.py
??? conftest.py          # Test fixtures and configuration
??? test_auth.py         # Authentication tests
??? test_payments.py     # Payment creation tests
??? test_transactions.py # Transaction listing tests
??? test_security.py    # Security utility tests
??? test_health.py      # Health check tests
```

## Test Coverage

### Authentication Tests
- ? Merchant registration
- ? Login with valid credentials
- ? Login with invalid credentials
- ? Get current merchant info
- ? Authentication middleware

### Payment Tests
- ? Create XRP payment
- ? Create NOWPayments payment (mocked)
- ? Get payment details
- ? Payment authorization checks
- ? Invalid currency handling
- ? Amount validation

### Transaction Tests
- ? List transactions
- ? Pagination
- ? Merchant isolation (only own transactions)
- ? Empty results

### Security Tests
- ? Password hashing
- ? Password verification
- ? JWT token creation
- ? JWT token decoding
- ? Token expiration

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test. This ensures:
- Fast test execution
- Isolation between tests
- No database setup required

## Fixtures

Key fixtures available in `conftest.py`:

- `db` - Database session
- `client` - Test HTTP client
- `test_merchant` - Pre-created merchant
- `test_merchant_token` - JWT token for test merchant
- `authenticated_client` - HTTP client with authentication
- `test_payment` - Pre-created payment

## Mocking

External services are mocked in tests:
- NOWPayments API calls
- XRP wallet address generation
- Exchange rate fetching

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest
```
