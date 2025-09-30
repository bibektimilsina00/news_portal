# =============================================================================
# 📰 News Portal API - Complete Makefile
# =============================================================================
# This Makefile provides all the development, testing, and deployment commands
# for the News Portal API project.
#
# Usage:
#   make help          - Show this help message
#   make setup         - Initial project setup
#   make dev           - Start development server
#   make test          - Run all tests
#   make lint          - Run linters and formatters
#   make clean         - Clean up cache files and artifacts
# =============================================================================

# =============================================================================
# Configuration
# =============================================================================
.PHONY: help setup dev test lint clean build migrate db-shell shell format type-check docs security audit

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# =============================================================================
# Help
# =============================================================================
help: ## Show this help message
	@echo "$(BLUE)📰 News Portal API - Complete Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Setup & Installation
# =============================================================================
setup: ## Initial project setup (install dependencies, setup pre-commit, create .env)
	@echo "$(BLUE)🚀 Setting up News Portal API...$(NC)"
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	uv sync
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	uv run pre-commit install
	@echo "$(YELLOW)Setting up environment file...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Please update .env with your configuration$(NC)"; \
	else \
		echo "$(GREEN)✅ .env file already exists$(NC)"; \
	fi
	@echo "$(GREEN)🎉 Setup complete!$(NC)"

install: ## Install/update all dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	uv sync

# =============================================================================
# Development Server
# =============================================================================
dev: ## Start development server with hot reload
	@echo "$(BLUE)🚀 Starting development server...$(NC)"
	@echo "$(YELLOW)Server will be available at: http://127.0.0.1:8000$(NC)"
	@echo "$(YELLOW)API docs at: http://127.0.0.1:8000/docs$(NC)"
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Start development server with debug logging
	@echo "$(BLUE)🐛 Starting development server with debug logging...$(NC)"
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

prod: ## Start production server with gunicorn
	@echo "$(BLUE)🏭 Starting production server...$(NC)"
	uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# =============================================================================
# Database Operations
# =============================================================================
migrate: ## Run database migrations
	@echo "$(BLUE)🗄️ Running database migrations...$(NC)"
	uv run alembic upgrade head

migrate-create: ## Create a new database migration
	@echo "$(BLUE)📝 Creating new database migration...$(NC)"
	@read -p "Enter migration message: " message; \
	uv run alembic revision --autogenerate -m "$$message"

migrate-downgrade: ## Downgrade database by one revision
	@echo "$(BLUE)⬇️ Downgrading database...$(NC)"
	uv run alembic downgrade -1

migrate-current: ## Show current database revision
	@echo "$(BLUE)📍 Current database revision:$(NC)"
	uv run alembic current

migrate-history: ## Show migration history
	@echo "$(BLUE)📚 Migration history:$(NC)"
	uv run alembic history

db-shell: ## Open database shell (requires DATABASE_URL in .env)
	@echo "$(BLUE)🗄️ Opening database shell...$(NC)"
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "$(RED)❌ DATABASE_URL not set in environment$(NC)"; \
		exit 1; \
	fi; \
	uv run python -c "from app.core.db import engine; import sqlalchemy as sa; conn = engine.connect(); result = conn.execute(sa.text('SELECT version()')); print('PostgreSQL version:', result.fetchone()[0]); conn.close()"

# =============================================================================
# Testing
# =============================================================================
test: ## Run all tests
	@echo "$(BLUE)🧪 Running all tests...$(NC)"
	uv run pytest

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)📊 Running tests with coverage...$(NC)"
	uv run pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "$(YELLOW)Coverage report saved to htmlcov/index.html$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	uv run pytest tests/ -k "not test_api"

test-api: ## Run API tests only
	@echo "$(BLUE)🌐 Running API tests...$(NC)"
	uv run pytest tests/ -k "test_api"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)👀 Running tests in watch mode...$(NC)"
	uv run pytest --watch

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)📝 Running tests with verbose output...$(NC)"
	uv run pytest -v

# =============================================================================
# Code Quality & Linting
# =============================================================================
lint: ## Run all linters and formatters
	@echo "$(BLUE)🧹 Running linters and formatters...$(NC)"
	@echo "$(YELLOW)Running ruff...$(NC)"
	uv run ruff check . --fix
	@echo "$(YELLOW)Running black...$(NC)"
	uv run black .
	@echo "$(YELLOW)Running mypy...$(NC)"
	uv run mypy app
	@echo "$(GREEN)✅ All linting complete!$(NC)"

format: ## Format code with black and ruff
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	uv run black .
	uv run ruff check . --fix

type-check: ## Run mypy type checking
	@echo "$(BLUE)🔍 Running type checking...$(NC)"
	uv run mypy app

ruff: ## Run ruff linter
	@echo "$(BLUE)🧹 Running ruff...$(NC)"
	uv run ruff check .

ruff-fix: ## Run ruff with auto-fix
	@echo "$(BLUE)🔧 Running ruff with auto-fix...$(NC)"
	uv run ruff check . --fix

black: ## Run black code formatter
	@echo "$(BLUE)🎨 Running black...$(NC)"
	uv run black .

mypy: ## Run mypy type checker
	@echo "$(BLUE)🔍 Running mypy...$(NC)"
	uv run mypy app

pre-commit: ## Run pre-commit on all files
	@echo "$(BLUE)🔗 Running pre-commit...$(NC)"
	uv run pre-commit run --all-files

# =============================================================================
# Documentation
# =============================================================================
docs: ## Generate API documentation
	@echo "$(BLUE)📚 Generating API documentation...$(NC)"
	@echo "$(YELLOW)API docs available at: http://127.0.0.1:8000/docs$(NC)"
	@echo "$(YELLOW)OpenAPI JSON at: http://127.0.0.1:8000/openapi.json$(NC)"
	uv run python scripts/generate_openapi.py

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)📚 Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation available at: http://127.0.0.1:8000/docs$(NC)"
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# =============================================================================
# Security & Audit
# =============================================================================
security: ## Run security checks
	@echo "$(BLUE)🔒 Running security checks...$(NC)"
	@echo "$(YELLOW)Checking for vulnerable dependencies...$(NC)"
	uv run pip-audit
	@echo "$(YELLOW)Checking for secrets...$(NC)"
	@if command -v detect-secrets >/dev/null 2>&1; then \
		detect-secrets scan --all-files; \
	else \
		echo "$(YELLOW)⚠️  detect-secrets not installed. Install with: pip install detect-secrets$(NC)"; \
	fi

audit: ## Audit dependencies for vulnerabilities
	@echo "$(BLUE)🔍 Auditing dependencies...$(NC)"
	uv run pip-audit

# =============================================================================
# Build & Deployment
# =============================================================================
build: ## Build the application for production
	@echo "$(BLUE)🏗️ Building application...$(NC)"
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t news-portal-api .
	@echo "$(GREEN)✅ Build complete!$(NC)"

build-dev: ## Build development Docker image
	@echo "$(BLUE)🏗️ Building development image...$(NC)"
	docker build -f Dockerfile.dev -t news-portal-api:dev .
	@echo "$(GREEN)✅ Development build complete!$(NC)"

docker-up: ## Start all services with Docker Compose
	@echo "$(BLUE)🐳 Starting Docker services...$(NC)"
	docker-compose up -d

docker-down: ## Stop all Docker services
	@echo "$(BLUE)🐳 Stopping Docker services...$(NC)"
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "$(BLUE)📋 Showing Docker logs...$(NC)"
	docker-compose logs -f

# =============================================================================
# Utility Commands
# =============================================================================
clean: ## Clean up cache files and artifacts
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	@echo "$(YELLOW)Removing Python cache files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	@echo "$(YELLOW)Removing test cache...$(NC)"
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "$(YELLOW)Removing build artifacts...$(NC)"
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

shell: ## Open Python shell with app context
	@echo "$(BLUE)🐍 Opening Python shell...$(NC)"
	uv run python -c "from app.core.db import get_session; session = next(get_session()); print('✅ Database connection established'); session.close()"

shell-ipython: ## Open IPython shell with app context
	@echo "$(BLUE)🐍 Opening IPython shell...$(NC)"
	uv run ipython -c "from app.core.db import get_session; session = next(get_session()); print('✅ Database connection established')"

deps: ## Show dependency tree
	@echo "$(BLUE)📦 Dependency tree:$(NC)"
	uv tree

deps-outdated: ## Check for outdated dependencies
	@echo "$(BLUE)📦 Checking for outdated dependencies...$(NC)"
	uv run pip list --outdated

# =============================================================================
# Module Management
# =============================================================================
create-module: ## Create a new module structure
	@echo "$(BLUE)📁 Creating new module...$(NC)"
	@read -p "Enter module name: " module_name; \
	if [ -z "$$module_name" ]; then \
		echo "$(RED)❌ Module name cannot be empty$(NC)"; \
		exit 1; \
	fi; \
	echo "$(YELLOW)Creating module: $$module_name$(NC)"; \
	./scripts/create_modules.sh "$$module_name"

# =============================================================================
# CI/CD Commands
# =============================================================================
ci: ## Run all CI checks (lint, test, type-check)
	@echo "$(BLUE)🔄 Running CI pipeline...$(NC)"
	$(MAKE) lint
	$(MAKE) test-cov
	$(MAKE) security
	@echo "$(GREEN)✅ CI pipeline complete!$(NC)"

# =============================================================================
# Development Workflow
# =============================================================================
workflow-setup: ## Complete development setup workflow
	@echo "$(BLUE)🚀 Complete development setup...$(NC)"
	$(MAKE) setup
	$(MAKE) migrate
	$(MAKE) test
	@echo "$(GREEN)🎉 Development environment ready!$(NC)"

workflow-daily: ## Daily development workflow
	@echo "$(BLUE)📅 Daily development workflow...$(NC)"
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) dev

# =============================================================================
# Information
# =============================================================================
info: ## Show project information
	@echo "$(BLUE)📰 News Portal API$(NC)"
	@echo ""
	@echo "$(YELLOW)Project Info:$(NC)"
	@echo "  Python Version: $(shell python --version)"
	@echo "  UV Version: $(shell uv --version)"
	@echo "  Current Branch: $(shell git branch --show-current)"
	@echo "  Last Commit: $(shell git log -1 --oneline)"
	@echo ""
	@echo "$(YELLOW)Environment:$(NC)"
	@echo "  Database: PostgreSQL"
	@echo "  Framework: FastAPI"
	@echo "  ORM: SQLModel/SQLAlchemy"
	@echo "  Package Manager: UV"
	@echo ""
	@echo "$(YELLOW)Available Services:$(NC)"
	@echo "  API Server: http://127.0.0.1:8000"
	@echo "  API Docs: http://127.0.0.1:8000/docs"
	@echo "  API OpenAPI: http://127.0.0.1:8000/openapi.json"

# =============================================================================
# Emergency Commands
# =============================================================================
reset-db: ## ⚠️  Reset database (WARNING: This will delete all data!)
	@echo "$(RED)⚠️  WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "$(YELLOW)Aborted.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(YELLOW)Resetting database...$(NC)"; \
	uv run alembic downgrade base; \
	uv run alembic upgrade head; \
	echo "$(GREEN)✅ Database reset complete!$(NC)"

nuke: ## ⚠️  Complete reset (WARNING: This will delete everything!)
	@echo "$(RED)🚨 DANGER: This will delete all data, cache, and dependencies!$(NC)"
	@read -p "Are you absolutely sure? Type 'NUKE' to continue: " confirm; \
	if [ "$$confirm" != "NUKE" ]; then \
		echo "$(YELLOW)Aborted.$(NC)"; \
		exit 1; \
	fi; \
	echo "$(YELLOW)Nuclear reset initiated...$(NC)"; \
	rm -rf .venv/; \
	rm -rf __pycache__/; \
	rm -rf .pytest_cache/; \
	rm -rf .mypy_cache/; \
	rm -rf .ruff_cache/; \
	rm -rf htmlcov/; \
	rm -rf .coverage; \
	rm -f .env; \
	echo "$(GREEN)✅ Nuclear reset complete! Run 'make setup' to start fresh.$(NC)"
