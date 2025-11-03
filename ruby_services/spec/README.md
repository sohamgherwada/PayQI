# PayQI Ruby Services Tests

RSpec test suite for Ruby webhook service and API client.

## Running Tests

### Quick Start

```bash
cd ruby_services
./run_tests.sh
```

### Manual Setup

```bash
# Install dependencies
bundle install

# Run all tests
bundle exec rspec

# Run with documentation format
bundle exec rspec --format documentation

# Run specific test file
bundle exec rspec spec/webhook_service_spec.rb

# Run specific test
bundle exec rspec spec/webhook_service_spec.rb:10
```

## Test Structure

```
spec/
??? spec_helper.rb           # RSpec configuration
??? webhook_service_spec.rb  # Webhook service tests
??? payqi_client_spec.rb     # API client tests
```

## Test Coverage

### Webhook Service Tests
- ? Health check endpoint
- ? NOWPayments webhook processing
- ? Webhook signature verification
- ? Invalid signature handling
- ? XRP webhook processing
- ? Transaction data validation
- ? Error handling

### API Client Tests
- ? Client initialization
- ? Merchant registration
- ? Login with token retrieval
- ? Payment creation
- ? Payment retrieval
- ? Transaction listing
- ? Error handling

## Test Environment

Tests run in test mode with mocked external dependencies:
- Faraday HTTP client is stubbed
- Environment variables are mocked
- External API calls are prevented

## Continuous Integration

```yaml
# Example GitHub Actions
- name: Run Ruby tests
  run: |
    cd ruby_services
    bundle install
    bundle exec rspec
```
