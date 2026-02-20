.PHONY: install run test lint docker-build docker-run clean

# Variables
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

# Default target
all: install

# Install dependencies
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e .[dev]

# Run API locally
run:
	$(BIN)/uvicorn solstein.api.main:app --reload

# Run tests
test:
	$(BIN)/pytest

# Lint code
lint:
	$(BIN)/ruff check .
	$(BIN)/mypy .

# Build Docker image
docker-build:
	docker build -t solstein-api .

# Run Docker container
docker-run:
	docker run -p 8000:8000 solstein-api

# Clean build artifacts
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
