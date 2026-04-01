# Solstein Command Center

.PHONY: install run dashboard test lint format docs-serve docs-strict docs-generate docs-generated-check docs-stale-check docs-quality-check docs-health-generate hooks-install check-all mcp-check clean test-critical test-contracts test-golden lint-critical type-critical type-strict lint-ast ast-test gate-critical gate-engineering lint-async-boundaries test-async-boundaries gate-async-boundaries test-schema-boundaries gate-schema-boundaries migrate migrate-dry-run migrate-rollback migrate-down check-migrations seed seed-test deploy help

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

# STORY-254: Verify test collection succeeds without DATABASE__URL
test-collect:
	@echo "Verifying hermetic test collection..."
	env -u DATABASE__URL -u DATABASE_URL $(BIN)/pytest tests/unit/test_collection_hermetic.py -v --tb=short
	@echo "Collection is hermetic."

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

docs-strict:
	$(BIN)/mkdocs build --strict -f mkdocs.strict.yml

docs-generate:
	$(BIN)/python scripts/docs/generate_all.py

docs-generated-check:
	$(BIN)/python scripts/docs/check_generated_docs.py

docs-stale-check:
	$(BIN)/python scripts/ci/check_stale_docs.py --path docs
	$(BIN)/python scripts/ci/check_stale_docs.py --path backlog

docs-quality-check:
	$(BIN)/python scripts/ci/check_docs_quality.py --path docs
	$(BIN)/python scripts/ci/check_docs_quality.py --path backlog

docs-health-generate:
	cd scripts/docs && $(BIN)/python generate_docs_health.py

hooks-install:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit .githooks/pre-push

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

lint-ast:
	npm run ast-grep -- --error --report-style=short src/solstein

ast-test:
	npm run ast-grep:test

lint-async-boundaries:
	$(BIN)/python scripts/ci/check_async_boundaries.py src/solstein

test-async-boundaries:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) COMPANIES_HOUSE_API_KEY=test-key NEWSAPI_KEY=test-news \
	$(BIN)/pytest tests/unit/test_async_boundary_gate.py tests/unit/test_async_boundary_regressions.py tests/unit/test_web_search_refresh.py tests/unit/test_news_signal_refresh.py -x

gate-async-boundaries: lint-async-boundaries test-async-boundaries
	@echo "Async boundary quality gates passed."

test-schema-boundaries:
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) \
	$(BIN)/pytest tests/unit/test_connector_fact_schema_gate.py -x

gate-schema-boundaries: test-schema-boundaries
	@echo "Connector fact schema boundary gates passed."

type-critical:
	$(BIN)/mypy src/solstein/infrastructure/connectors src/solstein/adapters/enrichment src/solstein/data/unified src/solstein/worker

type-strict:
	$(BIN)/basedpyright --warnings

gate-engineering: lint-ast ast-test type-strict docs-strict docs-generated-check docs-quality-check
	@echo "Engineering guardrails passed."

gate-critical: lint-critical lint-ast lint-async-boundaries type-critical type-strict test-critical test-contracts test-schema-boundaries
	@echo "Critical pipeline quality gates passed."

# =============================================================================
# Database Migrations (STORY-097)
# =============================================================================

# Run Alembic migrations to head (idempotent, with timeout and logging)
migrate:
	$(PYTHON) scripts/ci/run_migrations.py --timeout 300

# Show what migrations would be applied without running them
migrate-dry-run:
	$(PYTHON) scripts/ci/run_migrations.py --dry-run

# Roll back the last migration (use with caution)
migrate-rollback:
	alembic downgrade -1

# Show current migration status
migrate-status:
	alembic current
	alembic heads

# Roll back the last migration with confirmation (interactive safety)
# In CI, set CONFIRM=yes to skip the prompt
migrate-down:
	@if [ -z "$$CONFIRM" ] && [ -t 0 ]; then \
		echo "WARNING: This will revert the last Alembic migration."; \
		echo "Run 'alembic history --verbose | head -20' to review."; \
		printf "Type 'yes' to proceed: "; \
		read answer; \
		if [ "$$answer" != "yes" ]; then \
			echo "Aborted."; \
			exit 0; \
		fi; \
	elif [ "$$CONFIRM" != "yes" ]; then \
		echo "ERROR: migrate-down requires interactive TTY or CONFIRM=yes"; \
		exit 1; \
	fi
	alembic downgrade -1
	@echo "Migration rolled back. Run 'make migrate-status' to verify."

# Verify no unapplied migrations exist (CI gate / pre-deploy check)
check-migrations:
	@$(PYTHON) -c "\
	import subprocess, sys; \
	current = subprocess.run(['alembic', 'current'], capture_output=True, text=True).stdout.strip(); \
	heads = subprocess.run(['alembic', 'heads'], capture_output=True, text=True).stdout.strip(); \
	print(f'Current: {current}'); \
	print(f'Head:    {heads}'); \
	if not current or not heads: \
		print('ERROR: Could not determine migration state'); sys.exit(1); \
	head_rev = heads.split()[0] if heads else ''; \
	current_rev = current.split()[0] if current else ''; \
	if head_rev != current_rev: \
		print(f'PENDING MIGRATIONS: database at {current_rev}, head is {head_rev}'); sys.exit(1); \
	print('OK: database is at head revision'); \
	"

# =============================================================================
# Seed Data (STORY-098)
# =============================================================================

# Seed development database with sample companies (idempotent)
seed:
	@echo "Seeding development database..."
	PYTHONPATH=src $(PYTHON) scripts/seed_db.py --count 100
	@echo "Seed complete."

# Seed test fixtures only (for CI and local test runs)
seed-test:
	@echo "Seeding test fixtures..."
	PYTHONPATH=src DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) \
		$(PYTHON) scripts/seed_db.py --count 10
	@echo "Test seed complete."

# =============================================================================
# Deploy Readiness (STORY-098)
# =============================================================================

# Full deploy-readiness check: lint, test, check-migrations
# Locally: validates everything CI would check before deploy
# In CI: delegates to the workflow (deploy-staging.yml / deploy-production.yml)
deploy:
	@echo "=== Deploy Readiness Check ==="
	@echo "--- Step 1/4: Lint ---"
	$(MAKE) lint-critical
	@echo "--- Step 2/4: Tests ---"
	DATABASE__URL=$(TEST_DATABASE_URL) SECURITY__SECRET_KEY=$(TEST_SECRET_KEY) GITHUB_TOKEN=$(TEST_GITHUB_TOKEN) \
		$(BIN)/pytest tests/unit -x --tb=short -q
	@echo "--- Step 3/4: Migrations ---"
	$(MAKE) check-migrations
	@echo "--- Step 4/4: Type Check ---"
	$(MAKE) type-critical
	@echo "=== All checks passed. Ready to deploy — push to staging branch. ==="

# =============================================================================
# Help (STORY-098)
# =============================================================================

# List all available targets with descriptions
help:
	@echo "Solstein Command Center"
	@echo "======================"
	@echo ""
	@echo "Development:"
	@echo "  make install          Install all dependencies (Python + JS)"
	@echo "  make run              Start API server (FastAPI with reload)"
	@echo "  make dashboard        Start dashboard (Next.js dev server)"
	@echo "  make dev              Start full dev environment (Docker Compose)"
	@echo "  make dev-setup        Initial Docker dev environment setup"
	@echo "  make dev-shell        Open shell in dev container"
	@echo "  make dev-logs         View dev container logs"
	@echo "  make dev-stop         Stop dev environment"
	@echo "  make dev-clean        Remove dev environment and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests with coverage"
	@echo "  make test-fast        Run tests excluding slow markers"
	@echo "  make test-critical    Run critical pipeline regression tests"
	@echo "  make test-contracts   Run data contract tests"
	@echo ""
	@echo "Quality:"
	@echo "  make lint             Run all linters (ruff + mypy + eslint)"
	@echo "  make lint-critical    Run critical path linters"
	@echo "  make format           Auto-format code (ruff)"
	@echo "  make type-critical    Type-check critical paths (mypy)"
	@echo "  make type-strict      Strict type-check (basedpyright)"
	@echo "  make gate-critical    Run all critical quality gates"
	@echo "  make gate-engineering Run engineering guardrails"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Run pending Alembic migrations"
	@echo "  make migrate-dry-run  Preview migrations without applying"
	@echo "  make migrate-rollback Roll back last migration (no prompt)"
	@echo "  make migrate-down     Roll back last migration (with confirmation)"
	@echo "  make migrate-status   Show current and head revisions"
	@echo "  make check-migrations Verify database is at head (CI gate)"
	@echo "  make seed             Seed dev database with 100 companies"
	@echo "  make seed-test        Seed test fixtures (10 companies)"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy           Run full deploy-readiness checks"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve       Serve docs locally (MkDocs)"
	@echo "  make docs-strict      Build docs in strict mode"
	@echo "  make docs-generate    Generate API docs"
	@echo "  make docs-quality-check  Run placeholder token + metadata validation gates"
	@echo ""
	@echo "Other:"
	@echo "  make clean            Remove all build artifacts"
	@echo "  make scan-secrets     Run secret scanning"
	@echo "  make check-coverage   Enforce coverage thresholds"
	@echo "  make help             Show this help message"

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
