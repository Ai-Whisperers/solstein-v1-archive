# Developer Onboarding Guide

> **Getting started with Solstein development**
> > Last Updated: 2026-03-06

---

## Prerequisites

### Required Software

- **Python** 3.11 or higher
- **Git** 2.30 or higher
- **Docker** 20.10 or higher
- **Docker Compose** 1.29 or higher
- **kubectl** 1.28 or higher (for Kubernetes operations)
- **Helm** 3.12 or higher (for deployments)
- **Terraform** 1.5 or higher (for infrastructure)

### Recommended Software

- **VS Code** with extensions:
  - Python
  - Pylance
  - Docker
  - Kubernetes
  - YAML
- **Postman** or **Insomnia** for API testing
- **pgAdmin** or **DBeaver** for database management

### Accounts Required

- GitHub account (with access to solstein repo)
- AWS account (for infrastructure)
- Slack account (for team communication)

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/solstein.git
cd solstein
```

### 2. Set Up Python Environment

```bash
# Install uv (fast Python package installer)
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -e ".[dev]"
```

### 3. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
# Required variables:
# - DATABASE__URL
# - REDIS__URL
# - SECURITY__SECRET_KEY
# - GITHUB_TOKEN
```

### 4. Start Dependencies with Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps
```

### 5. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Seed database with test data (optional)
python scripts/seed_database.py
```

### 6. Run the Application

```bash
# Start the API server
uvicorn solstein.api.main:app --reload --host 0.0.0.0 --port 8000

# Or using the CLI
solstein api
```

### 7. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## Development Workflow

### Branch Naming Convention

```
feature/description        # New features
bugfix/description         # Bug fixes
hotfix/description         # Critical fixes
refactor/description       # Code refactoring
docs/description           # Documentation
test/description           # Test improvements
```

### Making Changes

1. **Create a branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes**

3. **Run pre-commit hooks:**
   ```bash
   pre-commit run --all-files
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   gh pr create
   ```

### Code Review Process

1. All PRs require at least 2 approvals
2. CI checks must pass
3. CODEOWNERS must approve for sensitive files
4. Link related issues in PR description

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_companies.py

# With coverage
pytest --cov=solstein --cov-report=html

# Integration tests
pytest tests/integration/ -v

# Parallel execution
pytest -n auto
```

### Writing Tests

```python
# tests/unit/test_example.py
import pytest
from solstein.domain.models import Company

class TestCompany:
    def test_company_creation(self):
        company = Company(name="Test Co", domain="test.com")
        assert company.name == "Test Co"
    
    def test_company_validation(self):
        with pytest.raises(ValueError):
            Company(name="", domain="invalid")
```

---

## Debugging

### Local Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### Docker Debugging

```bash
# View logs
docker-compose logs -f api

# Shell into container
docker-compose exec api bash

# Check database
docker-compose exec postgres psql -U postgres -d solstein
```

### Kubernetes Debugging

```bash
# Port forward
kubectl port-forward svc/solstein-api 8000:80 -n solstein

# View logs
kubectl logs -f deployment/solstein-api -n solstein

# Shell into pod
kubectl exec -it deployment/solstein-api -n solstein -- bash
```

---

## Common Tasks

### Database Operations

```bash
# Create migration
alembic revision --autogenerate -m "add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View history
alembic history
```

### Adding Dependencies

```bash
# Add runtime dependency
uv pip install package-name
# Then update pyproject.toml

# Add development dependency
uv pip install --dev package-name
```

### Running Background Tasks

```bash
# Start Celery worker
celery -A solstein.celery_config worker --loglevel=info

# Start Celery beat (scheduler)
celery -A solstein.celery_config beat --loglevel=info
```

---

## CI/CD for Developers

### Understanding the Pipeline

1. **Pre-commit hooks** run locally
2. **CI workflow** runs on every PR
3. **Integration tests** run on PR
4. **Staging deployment** on merge to develop
5. **Production deployment** on tag

### Monitoring Your Builds

```bash
# View recent workflow runs
gh run list

# View specific run
gh run view RUN_ID

# View logs
gh run view RUN_ID --log
```

### Troubleshooting Failed Builds

1. Check the workflow logs in GitHub Actions
2. Reproduce locally:
   ```bash
   # Run the same commands as CI
   ruff check src/ tests/
   mypy
   pytest tests/
   ```
3. Fix issues and push again

---

## Deployment

### Deploying to Staging

Staging deploys automatically on merge to `develop`.

To deploy manually:
```bash
gh workflow run deploy-staging.yml
```

### Deploying to Production

1. Create a tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. Monitor deployment:
   ```bash
   gh run watch
   ```

---

## Resources

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [CI/CD Guide](./CICD.md)
- [Operations Runbook](./RUNBOOK.md)
- [Architecture Decision Records](./adr/)

### Tools
- [GitHub Repository](https://github.com/your-org/solstein)
- [Staging Environment](https://staging.solstein.app)
- [Production Environment](https://solstein.app)
- [Grafana Dashboard](https://grafana.solstein.app)

### Communication
- **Slack:** #solstein-dev
- **Email:** dev@solstein.app
- **On-call:** PagerDuty rotation

---

## Getting Help

### Common Issues

**Issue:** `ModuleNotFoundError`
```bash
# Solution: Install dependencies
uv pip install -e ".[dev]"
```

**Issue:** Database connection refused
```bash
# Solution: Start Docker services
docker-compose up -d postgres redis
```

**Issue:** Port already in use
```bash
# Solution: Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Escalation Path

1. Check documentation (this guide)
2. Ask in #solstein-dev Slack channel
3. Create GitHub issue
4. Contact Platform Team

---

## Checklist

Before submitting your first PR:

- [ ] All tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Code is documented
- [ ] PR description is complete
- [ ] Linked to related issues
- [ ] Reviewed by at least 2 team members

---

*Welcome to the team! 🚀*

*This guide is maintained by the Platform Team. Last updated: 2026-03-06*
