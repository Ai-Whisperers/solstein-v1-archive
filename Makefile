# Solstein Command Center

.PHONY: install run dashboard test lint format docs-serve check-all mcp-check clean

# Variables
PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

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
