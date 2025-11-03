# Contributing to PayQI

Thank you for your interest in contributing to PayQI! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/payqi.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

See the main [README.md](README.md) for setup instructions.

## Code Style

### Python

- Follow PEP 8 style guide
- Use Black for formatting: `black backend/`
- Use isort for imports: `isort backend/`
- Maximum line length: 120 characters
- Type hints are encouraged

### Ruby

- Follow Ruby style guide
- Use RuboCop: `bundle exec rubocop`
- Maximum line length: 120 characters
- Use frozen string literals: `# frozen_string_literal: true`

## Testing

### Running Tests

```bash
# Python tests
cd backend && ./run_tests.sh

# Ruby tests
cd ruby_services && ./run_tests.sh

# Integration tests
./test_api.sh
```

### Writing Tests

- Write tests for all new features
- Maintain or improve test coverage
- Include both positive and negative test cases
- Mock external services

## Commit Messages

Follow conventional commits:

```
feat: add XRP payment support
fix: resolve authentication bug
docs: update API documentation
test: add integration tests
chore: update dependencies
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create a release tag
4. GitHub Actions will build and publish

## Questions?

Open an issue or contact maintainers.
