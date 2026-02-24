# Phase 2-4 Detailed Specifications

## Overview
This document provides detailed implementation specifications for Phase 2 (Weeks 3-4), Phase 3 (Weeks 5-6), and Phase 4 (Weeks 7-8) of the Solstein Quality Improvement Plan.

---

# PHASE 2: Quality Gates & Advanced Testing (Weeks 3-4)

## Improvement #5: Mutation Testing with MutPy

### What It Does
Introduces mutation testing to verify test quality - not just code coverage but whether tests actually catch bugs.

### Why It Matters
- Coverage = quantity of tested code
- Mutation score = quality of tests
- 80% coverage with weak tests = false confidence
- 60% coverage with 75% mutation score = real quality

### Implementation

#### Dependencies
```bash
pip install mutpy
```

#### File: `config/mutation-config.json`
```json
{
  "version": "1.0",
  "target_score": 75,
  "operators": {
    "AOR": true,
    "BOR": true,
    "COI": true,
    "LOD": false,
    "ROR": true
  },
  "exclude_modules": ["tests/", "conftest.py"],
  "timeout": 5
}
```

#### File: `.github/workflows/mutation.yml`
```yaml
name: Mutation Testing

on:
  push:
    branches: [main, master, develop]
  pull_request:

jobs:
  mutation-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install mutpy
      
      - name: Run mutation tests
        run: |
          mutpy --target src/solstein \
            --tests tests/unit \
            --experimental \
            --timeout 5 \
            -m AOR,BOR,COI,ROR \
            -c config/mutation-config.json
```

#### Makefile Target
```makefile
# Mutation testing
mutation-test:
	pip install mutpy
	mutpy --target src/solstein --tests tests/unit --experimental
```

### Validation
- Mutation score >= 75% on main
- Feature branches optional (skip mutation)

---

## Improvement #6: 12-Stage CI/CD Pipeline

### What It Does
Expands from 5 stages to 12 comprehensive stages for thorough validation.

### Stage Breakdown

| # | Stage | Purpose | Timeout |
|---|-------|---------|---------|
| 1 | Lint | Code style check | 2 min |
| 2 | Type Check | Type validation | 3 min |
| 3 | Security Scan | Dependency vulnerabilities | 2 min |
| 4 | Unit Tests | Fast logic tests | 5 min |
| 5 | Integration Tests | API contract tests | 10 min |
| 6 | Coverage Check | Threshold enforcement | 2 min |
| 7 | Mutation Tests | Test quality (main only) | 15 min |
| 8 | E2E Tests | Full workflow tests | 15 min |
| 9 | Build | Docker image build | 10 min |
| 10 | Security Audit | Container scanning | 5 min |
| 11 | Deploy to Test | Deploy to staging | 10 min |
| 12 | Smoke Tests | Health check | 5 min |

### Implementation

#### Update `.github/workflows/ci.yml`

Add new jobs for each stage. Key changes:
- Parallelize independent stages
- Add dependency chains where needed
- Add timeout limits per job

---

## Improvement #7: SBOM Generation (CycloneDX)

### What It Does
Generates Software Bill of Materials for security compliance and dependency tracking.

### Implementation

#### Dependencies
```bash
pip install cyclonedx-bom
```

#### File: `.github/workflows/sbom.yml`
```yaml
name: SBOM Generation

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Generate SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py -i . -o bom.xml --format xml
      
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: bom.xml
```

---

## Improvement #8: Dynamic Quality Policies

### What It Does
Enforces branch-specific quality rules via configuration, not hardcoded logic.

### Implementation

#### File: `config/quality-policies.json`
```json
{
  "version": "1.0",
  "policies": {
    "main": {
      "coverage_min": 80,
      "mutation_score_min": 75,
      "lint_errors": 0,
      "security_vulnerabilities": 0,
      "docs_required": true
    },
    "develop": {
      "coverage_min": 75,
      "mutation_score_min": 70,
      "lint_errors": 5,
      "security_vulnerabilities": 0,
      "docs_required": false
    },
    "feature": {
      "coverage_min": 70,
      "mutation_score_min": 0,
      "lint_errors": 10,
      "security_vulnerabilities": 1,
      "docs_required": false
    }
  }
}
```

---

# PHASE 3: Automation & Documentation (Weeks 5-6)

## Improvement #9: Automated Remediation Scripts

### What It Does
Scripts that automatically fix common issues.

### Scripts to Create

#### `scripts/auto-fix-lint.py`
```python
#!/usr/bin/env python3
"""Auto-fix common lint issues."""
import subprocess
import sys

def main():
    subprocess.run(["ruff", "check", "--fix", "src/"])
    subprocess.run(["ruff", "format", "src/"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### `scripts/auto-fix-imports.py`
```python
#!/usr/bin/env python3
"""Auto-sort imports."""
import subprocess
import sys

def main():
    subprocess.run(["ruff", "check", "--fix", "--select", "I", "src/"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Improvement #10: Documentation Enforcement

### What It Does
Ensures public APIs have docstrings and documentation is kept up-to-date.

### Implementation

#### Update `.pre-commit-config.yaml`
Add:
```yaml
- repo: https://github.com/crate-ci/typos
  rev: v1.16.23
  hooks:
    - id: typos

- repo: local
  hooks:
    - id: docstring-check
      name: Check docstrings
      entry: python3 scripts/check-docstrings.py
      language: system
      files: src/
      pass_filenames: false
```

---

## Improvement #11: Agent Identity Protocol

### What It Does
Implements agent identification in commits for AI-assisted development transparency.

### Implementation

#### File: `.github/workflows/agent-identity.yml`
```yaml
name: Agent Identity

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  detect-agents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Detect agent commits
        run: |
          python3 scripts/detect-agents.py
        
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '🤖 AI-assisted changes detected. Please review carefully.'
            })
```

---

## Improvement #12: GitHub Actions Enhancement

### What It Does
Improves GitHub Actions with better caching, parallelization, and reporting.

### Implementation

#### Update `.github/workflows/ci.yml`
- Add dependency caching
- Add parallel job execution
- Add detailed test reporting

---

# PHASE 4: Operations & Maintenance (Weeks 7-8)

## Improvement #13: Configuration Wizard

### What It Does
Interactive CLI to configure quality gates for new projects.

### Implementation

#### File: `scripts/config-wizard.py`
```python
#!/usr/bin/env python3
"""Interactive configuration wizard."""
import json
import sys

def main():
    print("Solstein Quality Configuration Wizard")
    print("=" * 40)
    
    config = {}
    config['coverage_target'] = input("Target coverage % [80]: ") or 80
    config['mutation_target'] = input("Target mutation score % [75]: ") or 75
    
    with open('config/quality.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\nConfiguration saved!")

if __name__ == "__main__":
    main()
```

---

## Improvement #14: Cost Monitoring

### What It Does
Tracks CI/CD costs and provides optimization recommendations.

### Implementation

#### File: `.github/workflows/cost-tracking.yml`
```yaml
name: Cost Tracking

on:
  workflow_run:
    workflows: [CI/CD Pipeline]
    types: [completed]

jobs:
  track-cost:
    runs-on: ubuntu-latest
    steps:
      - name: Calculate workflow cost
        uses: github-cost/estimate-action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Store cost metrics
        run: |
          python3 scripts/store-cost-metrics.py
```

---

## Improvement #15: Performance Benchmarking

### What It Does
Tracks test execution time and CI pipeline duration over time.

### Implementation

#### File: `.github/workflows/benchmark.yml`
```yaml
name: Performance Benchmarking

on:
  push:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run benchmark
        run: |
          python3 scripts/benchmark.py --output benchmark.json
      
      - name: Store benchmark
        uses: benchmark-action/upload-benchmark@v1
        with:
          tool: pytest
          data: benchmark.json
```

---

# Timeline Summary

| Phase | Weeks | Improvements | Effort |
|-------|-------|--------------|--------|
| Phase 1 | 1-2 | 4 improvements | 20-32 hrs |
| Phase 2 | 3-4 | 4 improvements | 21-28 hrs |
| Phase 3 | 5-6 | 4 improvements | 18-24 hrs |
| Phase 4 | 7-8 | 3 improvements | 12-17 hrs |
| **Total** | **8** | **15 improvements** | **71-101 hrs** |

---

# Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Coverage | 57% | 80%+ |
| Quality Gates | 5 | 16 |
| Pre-commit Hooks | 8 | 15+ |
| Mutation Score | N/A | 75%+ |
| SBOM Compliance | No | Yes |
| Secret Patterns | 3 | 14 |
| CI/CD Stages | 5 | 12 |
| Pipeline Time | ~8 min | ~15 min |
