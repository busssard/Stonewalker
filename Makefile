.PHONY: help test test-fast test-slow install clean translations compile-translations lint format quality-check security-scan

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -r translation_requirements.txt

test: ## Run all tests with translation compilation
	python run_tests.py

test-fast: ## Run only fast tests (unit tests)
	python run_tests.py -m "not slow" -m "not integration"

test-slow: ## Run only slow tests (integration tests)
	python run_tests.py -m "slow or integration"

test-cov: ## Run tests with coverage report
	python run_tests.py --cov=source --cov-report=html --cov-report=term

translations: ## Extract translations to CSV
	python po_to_excel.py source/content/locale translations.csv

compile-translations: ## Compile translations manually
	cd source && python manage.py compile_translations

clean: ## Clean up generated files
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.mo" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/

setup: install ## Setup the project (install dependencies and compile translations)
	$(MAKE) compile-translations

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run ruff linter (check only, no fixes)
	ruff check source/ --config source/pyproject.toml

format: ## Check code formatting (no changes, diff only)
	ruff format --check --diff source/ --config source/pyproject.toml

quality-check: lint format ## Run all quality checks (lint + format)
	@echo "All quality checks passed."

security-scan: ## Run bandit security scanner
	bandit -r source/ -c source/pyproject.toml --exit-zero
