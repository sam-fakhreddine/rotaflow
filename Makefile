.PHONY: help build test lint format clean up down logs setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Run initial project setup
	pip install pre-commit black isort flake8 mypy
	pre-commit install

build: ## Build Docker containers
	docker-compose -f docker-compose.test.yml build

up: ## Start test environments
	docker-compose -f docker-compose.test.yml up -d

down: ## Stop test environments
	docker-compose -f docker-compose.test.yml down

logs: ## Show container logs
	docker-compose -f docker-compose.test.yml logs -f

test: ## Run tests (placeholder)
	@echo "Tests not implemented yet"

lint: ## Run linting
	flake8 app/
	mypy app/ --ignore-missing-imports

format: ## Format code
	black app/
	isort app/

precommit-install: ## Install pre-commit hooks
	pre-commit install

precommit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	docker-compose -f docker-compose.test.yml down --volumes --remove-orphans

dev: setup build up ## Setup development environment
	@echo "Development environment ready!"
	@echo "Test Customer 1: http://localhost:6247"
	@echo "Test Customer 2: http://localhost:6248"