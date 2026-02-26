# Solstein - AI-Powered Competitive Intelligence Platform

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI + Async
- **Package Manager**: uv / pip
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Data Processing**: Pandas + OpenPyXL (Excel export)
- **Testing**: pytest
- **Linting**: ruff + black + mypy
- **CLI**: Click

## Project Overview
Solstein is an AI-powered competitive intelligence platform designed for PE/VC professionals. Analyzes market data, company financials, competitive positioning, and generates strategic insights.

## Setup Commands
- Install: `uv sync` or `pip install -r requirements.txt`
- Dev: `python run_research.py` or `python -m uvicorn app:app --reload`
- Tests: `pytest`
- Type check: `mypy .`
- Format: `black . && ruff check --fix .`

## Code Style
- **Formatting**: Black (120 char line length)
- **Import order**: isort (stdlib → third-party → local)
- **Naming**:
  - Modules: snake_case (`research_analyzer.py`)
  - Classes: PascalCase (`CompetitiveAnalyzer`)
  - Functions: snake_case (`analyze_competitor`)
  - Constants: UPPER_SNAKE_CASE (`MAX_RETRY_ATTEMPTS`)
- **Type Hints**: Required for all functions
- **Docstrings**: Google style

## Core Modules
- **Research**: Data collection and analysis
- **API**: FastAPI endpoints for competitor/company analysis
- **Database**: SQLAlchemy models for market data
- **CLI**: Click commands for batch processing
- **Excel Export**: OpenPyXL for generating reports

## Database (PostgreSQL)
- Models: SQLAlchemy ORM classes
- Migrations: Alembic (when applicable)
- Connection: Async SQLAlchemy for async endpoints

## Testing Requirements
- **Unit Tests**: pytest for business logic
- **Test location**: `tests/` directory
- **Coverage**: Minimum 75% line coverage
- **Fixtures**: Use pytest fixtures for test data
- **Database**: Use test database (separate from production)

## Important Files & Directories
- **Main entry**: `run_research.py`
- **API**: `app/` or `api/` directory
- **Models**: `models/` (database schemas)
- **Services**: `services/` (business logic)
- **Utils**: `lib/` or `utils/` (helper functions)
- **Tests**: `tests/` directory
- **Configuration**: `pyproject.toml`, `settings.py`
- **Environment**: `.env` (gitignored), `.env.example` (committed)

## Do NOT Do
- ❌ Don't use bare `except:` statements
- ❌ Don't use mutable defaults in functions
- ❌ Don't hardcode secrets or config
- ❌ Don't use `print()` - use logging instead
- ❌ Don't skip type hints
- ❌ Don't commit `.env` files
- ❌ Don't use wildcard imports
- ❌ Don't leave TODO comments without issues

## Key Commands for Development
- `python run_research.py` - Run main research pipeline
- `pytest -v` - Run tests with verbose output
- `pytest --cov=. --cov-report=html` - Generate coverage report
- `mypy . --strict` - Strict type checking
- `black . && ruff check --fix .` - Format and lint
- `python -m pytest tests/ -k "pattern"` - Run specific tests

## Git Workflow
- Feature branches: `feature/scope-description`
- Bug fixes: `fix/scope-description`
- Commits: Conventional Commits format (`feat:`, `fix:`, `refactor:`, `test:`)

## OpenCode Integration
- Use `@build` agent for implementation
- Use `@plan` agent for research/analysis planning
- Use `@review` subagent for code quality checks
- Use `@coder` subagent for quick fixes/boilerplate
