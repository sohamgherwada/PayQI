# CI/CD Pipeline Documentation

This document describes the GitHub Actions CI/CD pipeline for PayQI.

## Workflow Overview

PayQI uses multiple GitHub Actions workflows to ensure code quality, security, and reliability:

### 1. Python Tests (`python-tests.yml`)
- Runs pytest on Python 3.11 and 3.12
- Includes PostgreSQL service for database tests
- Generates coverage reports
- Uploads coverage to Codecov

### 2. Ruby Tests (`ruby-tests.yml`)
- Runs RSpec on Ruby 3.2 and 3.3
- Runs RuboCop for code style checks

### 3. Integration Tests (`integration-tests.yml`)
- Tests the full API stack
- Uses Docker Compose to spin up services
- Runs end-to-end API tests

### 4. Code Quality (`code-quality.yml`)
- **Python**: Black, isort, Flake8, mypy
- **Ruby**: RuboCop

### 5. Security Scanning (`security.yml`)
- Dependency review for PRs
- Python: Safety and Bandit
- Ruby: Bundler Audit
- Docker: Trivy vulnerability scanner

### 6. Docker Build (`docker-build.yml`)
- Builds Docker images for backend and webhook-service
- Pushes to GitHub Container Registry
- Uses buildx for multi-platform support

### 7. Release (`release.yml`)
- Creates GitHub releases from tags
- Generates changelog automatically

## Badge URLs

Update these in your README.md with your actual GitHub username and repo name:

```markdown
[![Python Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/python-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/python-tests.yml)
[![Ruby Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ruby-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ruby-tests.yml)
```

## Dependabot

Dependabot is configured to:
- Check Python dependencies weekly
- Check Ruby dependencies weekly
- Check Docker images weekly
- Check GitHub Actions weekly

See [`.github/dependabot.yml`](.github/dependabot.yml)

## Pre-commit Hooks

Install pre-commit hooks for local development:

```bash
pip install pre-commit
pre-commit install
```

This will run checks before each commit:
- Code formatting (Black, isort)
- Linting (Flake8, RuboCop)
- Security checks
- YAML/JSON validation

## Local Testing

Before pushing, run:

```bash
make test      # Run all tests
make lint      # Check code quality
make format    # Auto-format code
```

## Troubleshooting CI

### Tests failing in CI but passing locally
- Check environment variables
- Ensure test database is properly configured
- Check service dependencies

### Docker build failures
- Check Dockerfile syntax
- Verify all dependencies are listed
- Check build logs in Actions

### Coverage upload failures
- Codecov token may be needed (optional)
- Check file paths in coverage reports

## Best Practices

1. ? Always run tests locally before pushing
2. ? Use `make format` to auto-format code
3. ? Check linting before committing
4. ? Keep test coverage above 80%
5. ? Fix security warnings immediately
6. ? Update dependencies regularly
