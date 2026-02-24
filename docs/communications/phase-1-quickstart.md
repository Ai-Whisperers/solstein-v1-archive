# Developer Quick-Start Guide

## Phase 1 Quality Improvements

### Setup (One-time)

```bash
# Switch to feature branch
git checkout feat/phase-1-quality-improvements

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Daily Commands

| Command | What it does |
|---------|--------------|
| `make test` | Run test suite |
| `make check-all` | Lint + test |
| `make check-coverage` | Verify coverage meets threshold |
| `make scan-secrets` | Scan for leaked secrets |
| `pre-commit run` | Run all hooks on staged files |

### Coverage Requirements

| Branch Type | Minimum Coverage |
|-------------|-----------------|
| Feature | 70% |
| Develop | 75% |
| Main/Release | 80% |

### Creating a Release

```bash
# Create release tag
make tag-release VERSION=1.2.3

# Create test tag
make tag-test VERSION=1.2.3

# Create security patch
make tag-security VERSION=20260224
```

### Troubleshooting

**Pre-commit fails:**
```bash
# Skip all hooks (use sparingly)
git commit --no-verify -m "message"

# Run specific hook
pre-commit run bandit
```

**Coverage too low:**
```bash
# Check current coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing
```

**Secret detected:**
- Review the secret pattern found
- If false positive: add to exclusions in `config/secret-patterns.json`
- If real secret: rotate credentials immediately

### Files Changed

- `.pre-commit-config.yaml` - Hook configuration
- `.yamllint` - YAML linting
- `pyproject.toml` - Dev dependencies + commitizen
- `config/coverage-thresholds.json` - Coverage rules
- `config/secret-patterns.json` - Secret patterns
- `scripts/enforce_coverage.py` - Coverage enforcer
- `scripts/secret_scan.py` - Secret scanner
- `scripts/parse_version_from_tag.py` - Version parser
- `.github/workflows/ci.yml` - Updated CI
- `.github/workflows/release.yml` - New release workflow
- `Makefile` - New targets
