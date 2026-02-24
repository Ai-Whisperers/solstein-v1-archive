# CI/CD Guide

This page is the canonical CI/CD reference for Solstein.

## Active Pipelines

Solstein uses GitHub Actions as the active CI/CD system.

- Backend + frontend + e2e + Docker: `.github/workflows/ci.yml`
- Documentation build and deploy: `.github/workflows/docs.yml`

## Pipeline Overview

### CI (`.github/workflows/ci.yml`)

- `backend-test`
  - Python matrix: 3.10, 3.11, 3.12
  - Install: `pip install -e ".[dev]"`
  - Checks: `ruff`, `mypy`, `pytest` with coverage
- `frontend-test`
  - Node 20
  - Dashboard lint + tests in `dashboard/`
- `e2e-test`
  - Depends on backend + frontend jobs
  - Runs Playwright tests in `dashboard/`
- `docker`
  - Builds and pushes image on `main`/`master` pushes
- `mutation` (`.github/workflows/mutation.yml`)
  - Runs mutation testing to verify test suite effectiveness.
- `sbom` (`.github/workflows/sbom.yml`)
  - Generates Software Bill of Materials for security and compliance.
- `release` (`.github/workflows/release.yml`)
  - Handles versioning and automated releases.

### Docs (`.github/workflows/docs.yml`)

- Triggered by changes in `docs/**` or `mkdocs.yml`
- Builds MkDocs site
- Deploys to GitHub Pages

## Local Verification Commands

Run from repo root using the project virtualenv.

```bash
venv/bin/python -m pip install -e ".[dev]"
venv/bin/ruff check src/ tests/
venv/bin/ruff format --check src/ tests/
venv/bin/mypy src/
venv/bin/pytest tests/ -v --cov=solstein --cov-report=term-missing
venv/bin/mkdocs build
```

## Notes on Legacy/Archived CI Docs

The `cicd/` directory currently contains historical/legacy material (including Azure-focused documents). Keep it for reference, but treat this page and `.github/workflows/*` as the source of truth for active Solstein delivery.
