.PHONY: help install test lint format type-check security clean build

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install safety bandit

test: ## Run tests
	pytest -v --cov=chatapi_cli --cov=validators --cov-report=term-missing

test-html: ## Run tests with HTML coverage report
	pytest -v --cov=chatapi_cli --cov=validators --cov-report=html

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format: ## Format code with black
	black .

format-check: ## Check code formatting
	black --check --diff .

type-check: ## Run type checking with mypy
	mypy chatapi_cli.py validators.py --ignore-missing-imports

security: ## Run security checks
	safety check
	bandit -r . -f json

check-all: lint format-check type-check security test ## Run all checks

clean: ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	python -m build

install-local: ## Install package locally
	pip install -e .

run: ## Run the CLI tool
	python chatapi_cli.py

demo: ## Run demo with example
	python example.py

setup-dev: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make check-all' to verify everything is working."

ci: check-all ## Run all CI checks locally
	@echo "All checks passed! Ready for CI/CD."
