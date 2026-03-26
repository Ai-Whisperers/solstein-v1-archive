# Solstein Command Center

.PHONY: install run dashboard test lint format docs-serve check-all mcp-check clean test-critical test-contracts test-golden lint-critical type-critical gate-critical lint-async-boundaries test-async-boundaries gate-async-boundaries

# Variables
PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin
TEST_DATABASE_URL ?= postgresql://test:test@localhost:5432/testdb
TEST_SECRET_KEY ?= abcdefghijklmnopqrstuvwxyz123456
TEST_GITHUB_TOKEN ?= test-github-token-12345

# Default target
all: install

# Install dependencies for both Backend and Dashboard
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e .[dev]
	cd dashboard && npm install

# Run API locally (FastAPI + Aura Logging)
run:
	$(BIN)/uvicorn solstein.api.main:app --reload

# Run Dashboard locally (Next.js Sunstone Interface)
dashboard:
	cd dashboard && npm run dev

# Run all tests (Unit, Integration, Data Quality)
test:
	$(BIN)/pytest tests/unit tests/integration tests/data_quality --cov=src

# Combined Linting (Python + JS)
lint:
	$(BIN)/ruff check src tests
	$(BIN)/mypy src
	cd dashboard && npm run lint

# Combined Formatting
format:
	$(BIN)/ruff format src tests
	$(BIN)/ruff check --fix src tests

# Serve Documentation (Ancient Grimoire Style)
docs-serve:
	$(BIN)/mkdocs serve

# Unified Quality Pipeline (The Craft Layer)
check-all: lint test
	@echo "✨ Solstein | Repository Integrity Verified."

# OpenCode MCP health checks
mcp-check:
	./scripts/opencode-mcp-doctor.sh
	./scripts/opencode-mcp-smoke-test.sh

# Clean all build artifacts and temporary files
clean:
	rm -rf $(VENV)
	rm -rf dashboard/.next
	rm -rf dashboard/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# Coverage enforcement
check-coverage:
	python3 scripts/enforce_coverage.py

# Run tests + enforce coverage
test-with-enforcement: test check-coverage
	@echo "Tests passed with coverage enforcement"

# Tag-based versioning
tag-release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make tag-release VERSION=1.2.3"; \
		exit 1; \
	fi
	git tag -a release-$(VERSION) -m "Release version $(VERSION)"
	git push origin release-$(VERSION)

tag-test:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make tag-test VERSION=1.2.3"; \
		exit 1; \
	fi
	git tag -a test-$(VERSION)-rc1 -m "Test version $(VERSION) rc1"
	git push origin test-$(VERSION)-rc1

tag-coverage:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make tag-coverage VERSION=1.2.3"; \
		exit 1; \
	fi
	git tag -a coverage-$(VERSION) -m "Coverage report $(VERSION)"
	git push origin coverage-$(VERSION)

tag-security:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make tag-security VERSION=20260224"; \
		exit 1; \
	fi
	git tag -a security-$(VERSION) -m "Security patch $(VERSION)"
	git push origin security-$(VERSION)

show-version:
	python3 scripts/parse_version_from_tag.py

# Secret scanning
scan-secrets:
	python3 scripts/secret_scan.py

# Mutation testing (requires mutpy)
mutation-test:
	pip install mutpy
	mutpy --target solstein --tests tests/unit --experimental -m AOR,BOR,COI,ROR

# Generate SBOM (Software Bill of Materials)
generate-sbom:
	pip install cyclonedx-bom
	cyclonedx-py -i . -o bom.xml --format xml

.PHONY: dev dev-setup dev-shell dev-logs dev-stop dev-clean dev-tools test-fast

# =============================================================================
# Development Commands (EPIC-028)
# =============================================================================

# Start development environment with hot reload
dev:
	@echo "🚀 Starting Solstein development environment..."
	docker-compose -f docker-compose.dev.yml up --build

# Initial setup for development
dev-setup:
	@echo "🔧 Setting up Solstein development environment..."
	cp -n .env.example .env 2>/dev/null || echo ".env already exists"
	docker-compose -f docker-compose.dev.yml build
	@echo "✅ Setup complete! Run 'make dev' to start."

# Open shell in dev container
dev-shell:
	docker-compose -f docker-compose.dev.yml exec api bash

# View logs from all services
dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
dev-stop:
	docker-compose -f docker-compose.dev.yml down

# Clean development environment (removes volumes)
dev-clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml rm -f
	@echo "✅ Development environment cleaned"

# Start with optional tools (pgadmin, redis-commander)
dev-tools:
	@echo "🚀 Starting with development tools..."
	docker-compose -f docker-compose.dev.yml --profile tools up --build

# Run tests in development container
dev-test:
	docker-compose -f docker-compose.dev.yml exec api pytest -xvs

# Run fast tests only (no slow tests)
test-fast:
	$(BIN)/pytest -m "not slow" -x

# Critical pipeline-node regression gates
test-critical:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) \
	$(BIN)/pytest tests/unit/test_audit_regressions_march_2026.py tests/unit/test_worker_tasks_isolated.py -x

test-contracts:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) \
	$(BIN)/pytest tests/unit/data/ -x

test-golden:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) \
	$(BIN)/pytest tests/data_quality/ -x

lint-critical:
	$(BIN)/ruff check src/solstein/infrastructure/connectors src/solstein/adapters/enrichment src/solstein/data/unified src/solstein/worker tests

lint-async-boundaries:
	$(BIN)/python scripts/ci/check_async_boundaries.py src/solstein

test-async-boundaries:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) COMPANIES_HOUSE_API_KEY=test-key NEWSAPI_KEY=test-news \
	$(BIN)/pytest tests/unit/test_async_boundary_gate.py tests/unit/test_async_boundary_regressions.py tests/unit/test_web_search_refresh.py tests/unit/test_news_signal_refresh.py -x

gate-async-boundaries: lint-async-boundaries test-async-boundaries
	@echo "Async boundary quality gates passed."

type-critical:
	$(BIN)/mypy src/solstein/infrastructure/connectors src/solstein/adapters/enrichment src/solstein/data/unified src/solstein/worker

gate-critical: lint-critical lint-async-boundaries type-critical test-critical test-contracts
	@echo "Critical pipeline quality gates passed."

# Reset development database
dev-reset-db:
	docker-compose -f docker-compose.dev.yml exec api python -c "
		import asyncio;
		from solstein.infrastructure.database import init_db, close_db;
		asyncio.run(init_db())"

# Seed development database
dev-seed:
	docker-compose -f docker-compose.dev.yml exec api python -c "
		import asyncio;
		from scripts.seed_db import seed_companies;
		asyncio.run(seed_companies(count=100))"
