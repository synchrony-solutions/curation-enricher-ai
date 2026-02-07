.PHONY: help install install-dev test test-unit test-integration lint format type-check clean docker-up docker-down docker-logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --without dev

install-dev: ## Install all dependencies including dev tools
	poetry install --with dev
	poetry run pre-commit install

test: ## Run all tests
	poetry run pytest

test-unit: ## Run only unit tests
	poetry run pytest tests/unit/

test-integration: ## Run only integration tests (requires DataHub running)
	poetry run pytest tests/integration/

coverage: ## Run tests with coverage report
	poetry run pytest --cov=src/enricher --cov-report=html --cov-report=term

lint: ## Run linting checks
	poetry run ruff check src/ tests/
	poetry run black --check src/ tests/

format: ## Format code with black and ruff
	poetry run ruff check --fix src/ tests/
	poetry run black src/ tests/

type-check: ## Run type checking with mypy
	poetry run mypy src/

pre-commit: ## Run all pre-commit hooks
	poetry run pre-commit run --all-files

clean: ## Clean up build artifacts and cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf dist/ build/ htmlcov/

docker-up: ## Start DataHub services
	docker-compose up -d

docker-down: ## Stop DataHub services
	docker-compose down

docker-logs: ## View DataHub logs
	docker-compose logs -f

docker-clean: ## Stop and remove DataHub volumes
	docker-compose down -v

enrich: ## Run enricher on a dataset (use DATASET_URN=...)
	poetry run curation-enricher-ai enrich "$(DATASET_URN)"

test-connection: ## Test connection to DataHub and Claude API
	poetry run curation-enricher-ai test-connection

build: ## Build package distribution
	poetry build

publish-test: ## Publish to TestPyPI
	poetry publish -r testpypi

publish: ## Publish to PyPI
	poetry publish
