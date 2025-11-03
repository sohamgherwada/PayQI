.PHONY: help test test-python test-ruby test-integration lint format clean setup docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial setup
	pip install -r backend/requirements.txt
	cd ruby_services && bundle install

test: test-python test-ruby ## Run all tests
	@echo "? All tests passed!"

test-python: ## Run Python tests
	cd backend && ./run_tests.sh

test-ruby: ## Run Ruby tests
	cd ruby_services && ./run_tests.sh

test-integration: ## Run integration tests
	./test_api.sh

lint: lint-python lint-ruby ## Lint all code
	@echo "? Linting complete!"

lint-python: ## Lint Python code
	cd backend && black --check app/ tests/
	cd backend && isort --check-only app/ tests/
	cd backend && flake8 app/ tests/

lint-ruby: ## Lint Ruby code
	cd ruby_services && bundle exec rubocop

format: format-python format-ruby ## Format all code
	@echo "? Formatting complete!"

format-python: ## Format Python code
	cd backend && black app/ tests/
	cd backend && isort app/ tests/

format-ruby: ## Format Ruby code
	cd ruby_services && bundle exec rubocop -a

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf backend/.pytest_cache
	rm -rf backend/htmlcov
	rm -rf backend/.coverage

security-check: ## Run security checks
	cd backend && pip install safety bandit
	safety check -r backend/requirements.txt || true
	bandit -r backend/app/ || true
	cd ruby_services && bundle exec bundle-audit check || true
