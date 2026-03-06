# EPIC-XXX: CI/CD Modernization and Optimization

> **Status:** Draft
> **Priority:** High
> **Effort:** 2-3 sprints
> **Owner:** Platform/Infra Team
> **Stakeholders:** All Engineering Teams

---

## 1. Executive Summary

The current CI/CD pipeline suffers from architectural debt, security anti-patterns, and efficiency bottlenecks that waste compute resources, provide false security confidence, and slow development velocity. This EPIC addresses all critical issues through a phased modernization approach.

**Current State Pain Points:**
- 7+ minutes of wasted compute time per PR due to job overhead duplication
- Security checks that never fail builds (`|| true` anti-pattern)
- Missing database services despite database-dependent tests
- Phantom script references (files don't exist)
- Extreme code duplication (no composite actions)
- Inconsistent Python versions across workflows
- Non-functional quality score calculation

**Target State:**
- Sub-5 minute total pipeline time through optimization
- Genuine security enforcement with actionable failures
- Reliable test execution with proper service dependencies
- Maintainable, DRY workflow definitions
- Consistent tooling and versioning

---

## 2. Goals and Success Metrics

### Primary Goals

| Goal | Current | Target | Metric |
|------|---------|--------|--------|
| Pipeline Duration | 12-15 min | <5 min | GitHub Actions runtime |
| Compute Waste | 7+ min overhead | <1 min | Setup time per workflow |
| Security Coverage | 0% (all pass) | 100% | Failed builds on issues |
| Test Reliability | Low (no DB) | High | Pass rate on main |
| Maintainability | Poor | Good | Lines of YAML |

### Secondary Goals

- [ ] Zero phantom script references
- [ ] Consistent Python version (3.12) across all jobs
- [ ] Composite actions for all reusable setup patterns
- [ ] Proper caching strategy for dependencies
- [ ] Semantic versioning for Docker images
- [ ] Multi-arch Docker builds (AMD64 + ARM64)

---

## 3. Phased Implementation Plan

### Phase 1: Critical Fixes (P0) - Week 1-2

**Objective:** Fix broken or dangerous functionality immediately.

#### Story 1.1: Fix Security Scan Job
**Priority:** P0
**Effort:** 2 points

**Current State:**
```yaml
- name: Run bandit
  run: bandit -r src/ -f json -o bandit-report.json || true
- name: Run safety check
  run: safety check --ignore=45158 || true
- name: Run secret scan script
  run: python scripts/secret_scan.py || true  # FILE DOESN'T EXIST
```

**Acceptance Criteria:**
- [ ] Remove all `|| true` patterns from security checks
- [ ] Create `scripts/ci/secret_scan.py` or remove the step
- [ ] Configure bandit to fail on medium+ severity findings
- [ ] Document security exception process (for intentional ignores)
- [ ] Add security findings to PR annotations via `github/codeql-action/upload-sarif`

**Implementation Notes:**
```yaml
# New approach
- name: Run bandit
  run: bandit -r src/ -f sarif -o bandit-report.sarif --severity-level medium

- name: Upload bandit results
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: bandit-report.sarif
```

---

#### Story 1.2: Add Missing Services to Test Job
**Priority:** P0
**Effort:** 3 points

**Current State:** Test job sets `DATABASE_URL` but has no services defined.

**Acceptance Criteria:**
- [ ] Add PostgreSQL 14 service container
- [ ] Add Redis 7 service container
- [ ] Configure health checks for both services
- [ ] Verify tests actually connect to database
- [ ] Document service versions in AGENTS.md

**Implementation:**
```yaml
test:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:14-alpine
      env:
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: solstein_test
      ports:
        - 5432:5432
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
    redis:
      image: redis:7-alpine
      ports:
        - 6379:6379
      options: >-
        --health-cmd "redis-cli ping"
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
  env:
    DATABASE_URL: postgresql://postgres:postgres@localhost:5432/solstein_test
    REDIS_URL: redis://localhost:6379/0
```

---

#### Story 1.3: Fix or Remove Phantom Scripts
**Priority:** P0
**Effort:** 2 points

**Current State:**
- `scripts/secret_scan.py` - referenced but doesn't exist
- `scripts/enforce_coverage.py` - referenced but doesn't exist

**Acceptance Criteria:**
- [ ] Audit all workflow files for script references
- [ ] Create missing scripts OR remove references
- [ ] Add CI check to validate script existence
- [ ] Document all CI scripts in README

**Option A - Create enforce_coverage.py:**
```python
#!/usr/bin/env python3
"""Enforce minimum code coverage threshold."""
import sys
import xml.etree.ElementTree as ET

MIN_COVERAGE = 80.0

def main():
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    coverage = float(root.attrib['line-rate']) * 100

    print(f"Coverage: {coverage:.2f}%")

    if coverage < MIN_COVERAGE:
        print(f"FAILED: Coverage {coverage:.2f}% is below minimum {MIN_COVERAGE}%")
        sys.exit(1)

    print(f"PASSED: Coverage meets minimum requirement")
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Option B - Remove coverage enforcement job** (if not needed)

---

### Phase 2: Performance Optimization (P1) - Week 3-4

#### Story 2.1: Create Composite Actions
**Priority:** P1
**Effort:** 3 points

**Current State:** 6 jobs × 4 setup steps = 24 repetitions of the same code.

**Acceptance Criteria:**
- [ ] Create `.github/workflows/composite/setup-python/action.yml`
- [ ] Create `.github/workflows/composite/setup-uv/action.yml`
- [ ] Create `.github/workflows/composite/install-deps/action.yml`
- [ ] Update all jobs to use composite actions
- [ ] Document composite actions in AGENTS.md

**Implementation:**

```yaml
# .github/workflows/composite/setup-python/action.yml
name: 'Setup Python Environment'
description: 'Setup Python with caching'
inputs:
  python-version:
    description: 'Python version'
    required: true
    default: '3.12'
runs:
  using: "composite"
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: 'pip'
```

```yaml
# .github/workflows/composite/install-deps/action.yml
name: 'Install Dependencies'
description: 'Install project dependencies with uv'
inputs:
  extras:
    description: 'Extra dependencies to install'
    required: false
    default: 'dev'
runs:
  using: "composite"
  steps:
    - name: Install uv
      run: pip install uv
      shell: bash
    - name: Install dependencies
      run: uv pip install --system -e ".[${{ inputs.extras }}]"
      shell: bash
```

**Usage:**
```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./.github/workflows/composite/setup-python
  - uses: ./.github/workflows/composite/install-deps
```

---

#### Story 2.2: Implement Dependency Caching
**Priority:** P1
**Effort:** 2 points

**Current State:** Dependencies installed from scratch on every job.

**Acceptance Criteria:**
- [ ] Add pip caching to setup-python action
- [ ] Add uv-specific caching if needed
- [ ] Cache pre-commit hooks
- [ ] Measure and document time savings

**Implementation:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: 'pip'
    cache-dependency-path: |
      pyproject.toml
      requirements*.txt
```

---

#### Story 2.3: Consolidate Quality Guardrails
**Priority:** P1
**Effort:** 3 points

**Current State:** 7 separate jobs, each with ~60s overhead.

**Acceptance Criteria:**
- [ ] Consolidate into single `code-quality` job
- [ ] Run all checks as sequential steps
- [ ] Generate combined report
- [ ] Maintain individual check failure behavior
- [ ] Remove broken `code-quality-score` job

**Implementation:**
```yaml
code-quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 2
    - uses: ./.github/workflows/composite/setup-python

    - name: Install tools
      run: pip install radon

    - name: Check code smells
      run: python scripts/ci/code_smell_detector.py
      continue-on-error: true

    - name: Check function sizes
      run: python scripts/ci/check_function_sizes.py --max-lines 100 --fail-on-violation

    - name: Check class sizes
      run: python scripts/ci/check_class_sizes.py --max-lines 300 --fail-on-violation

    - name: Check file sizes
      run: python scripts/ci/check_file_sizes.py --max-lines 500

    - name: Check complexity
      run: |
        echo "## Complexity Metrics" >> $GITHUB_STEP_SUMMARY
        radon cc src --average >> $GITHUB_STEP_SUMMARY
        radon mi src >> $GITHUB_STEP_SUMMARY
```

---

#### Story 2.4: Parallelize Independent Jobs
**Priority:** P1
**Effort:** 1 point

**Current State:** Tests wait for lint to complete unnecessarily.

**Acceptance Criteria:**
- [ ] Remove `needs: [lint-and-format]` from test job
- [ ] Run lint, type-check, test in parallel
- [ ] Keep docker-build dependent on test success
- [ ] Document job dependency graph

**New Dependency Graph:**
```
┌─────────┐  ┌───────────┐  ┌─────────┐
│  lint   │  │ type-check │  │  test   │
└────┬────┘  └─────┬──────┘  └────┬────┘
     │             │              │
     └─────────────┴──────────────┘
                   │
            ┌──────┴──────┐
            │ docker-build │
            └─────────────┘
```

---

### Phase 3: Consistency and Standards (P2) - Week 5-6

#### Story 3.1: Standardize Python Version
**Priority:** P2
**Effort:** 1 point

**Current State:** 3.12 in ci.yml, 3.11 in code-quality-guardrails.yml.

**Acceptance Criteria:**
- [ ] Define Python version in workflow env
- [ ] Update all jobs to use `${{ env.PYTHON_VERSION }}`
- [ ] Align with pyproject.toml `requires-python`
- [ ] Document version policy

**Implementation:**
```yaml
env:
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
```

---

#### Story 3.2: Clean Up Environment Variables
**Priority:** P2
**Effort:** 2 points

**Current State:** Duplicate env vars (flat and nested formats).

**Acceptance Criteria:**
- [ ] Audit which format the application actually uses
- [ ] Remove duplicate definitions
- [ ] Document configuration format in AGENTS.md
- [ ] Update .env.example if needed

**Decision Required:** Does the app use:
- `DATABASE_URL` (flat)
- `DATABASE__URL` (pydantic-settings nested)
- Both (with fallback)?

---

#### Story 3.3: Fix Path Filters
**Priority:** P2
**Effort:** 1 point

**Current State:** Inconsistent trigger patterns.

**Acceptance Criteria:**
- [ ] Add path filters to ci.yml OR remove from quality-guardrails.yml
- [ ] Ensure Dockerfile changes trigger CI
- [ ] Ensure workflow changes trigger CI
- [ ] Document trigger patterns

**Implementation:**
```yaml
on:
  push:
    branches: [main, master, develop]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'scripts/**'
      - 'pyproject.toml'
      - 'Dockerfile'
      - '.github/workflows/**'
  pull_request:
    branches: [main, master, develop]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'scripts/**'
      - 'pyproject.toml'
      - 'Dockerfile'
      - '.github/workflows/**'
```

---

#### Story 3.4: Fix Bare Except Check
**Priority:** P2
**Effort:** 2 points

**Current State:** Fragile regex-based check using git diff.

**Acceptance Criteria:**
- [ ] Replace regex with AST-based detection
- [ ] Use existing `code_smell_detector.py` functionality
- [ ] Handle edge cases (empty diffs, force pushes)
- [ ] Add tests for the check itself

**Implementation:**
```yaml
- name: Check for bare excepts
  run: |
    if [ "${{ github.event_name }}" == "pull_request" ]; then
      CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep '\.py$' || true)
    else
      CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD | grep '\.py$' || true)
    fi

    if [ -n "$CHANGED_FILES" ]; then
      python scripts/ci/code_smell_detector.py $CHANGED_FILES
    fi
```

---

### Phase 4: Docker and Deployment (P2) - Week 7-8

#### Story 4.1: Improve Docker Image Tagging
**Priority:** P2
**Effort:** 2 points

**Current State:** Only `latest` and SHA tags.

**Acceptance Criteria:**
- [ ] Add semantic version tags on releases
- [ ] Add branch name tags
- [ ] Document image retention policy
- [ ] Configure GitHub Container Registry retention

**Implementation:**
```yaml
- name: Docker meta
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=,suffix=,format=short

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

---

#### Story 4.2: Add Multi-Arch Docker Builds
**Priority:** P2
**Effort:** 3 points

**Current State:** Only AMD64 builds.

**Acceptance Criteria:**
- [ ] Enable QEMU for ARM64 emulation
- [ ] Build for linux/amd64 and linux/arm64
- [ ] Test ARM64 images locally
- [ ] Document platform support

**Implementation:**
```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
```

---

#### Story 4.3: Add Container Image Scanning
**Priority:** P2
**Effort:** 2 points

**Current State:** No vulnerability scanning of built images.

**Acceptance Criteria:**
- [ ] Add Trivy or Snyk container scan
- [ ] Fail builds on critical vulnerabilities
- [ ] Upload results to GitHub Security tab
- [ ] Document vulnerability response process

**Implementation:**
```yaml
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

---

### Phase 5: New Workflows (P3) - Week 9-10

#### Story 5.1: Add Dependabot Configuration
**Priority:** P3
**Effort:** 1 point

**Acceptance Criteria:**
- [ ] Create `.github/dependabot.yml`
- [ ] Configure pip dependency updates
- [ ] Configure GitHub Actions updates
- [ ] Set appropriate update frequency

**Implementation:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

#### Story 5.2: Add Release Workflow
**Priority:** P3
**Effort:** 3 points

**Acceptance Criteria:**
- [ ] Create `.github/workflows/release.yml`
- [ ] Trigger on version tags
- [ ] Build and push versioned Docker images
- [ ] Create GitHub release with changelog
- [ ] Deploy to staging environment

**Implementation:**
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true

      - name: Build and push versioned image
        # ... docker build with version tag
```

---

#### Story 5.3: Add Integration Test Workflow
**Priority:** P3
**Effort:** 5 points

**Acceptance Criteria:**
- [ ] Create separate workflow for integration tests
- [ ] Set up full service stack (PostgreSQL, Redis, etc.)
- [ ] Run against real dependencies
- [ ] Run on schedule (nightly) and on main branch
- [ ] Notify on failures

---

## 4. Dependencies and Blockers

### External Dependencies
- GitHub Actions runner availability
- GitHub Container Registry quota
- Docker Hub rate limits (if applicable)

### Internal Dependencies
- Database migration strategy (for test DB setup)
- Secrets management (for any new integrations)
- Team training on new workflows

### Blockers
None identified.

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking changes disrupt development | Medium | High | Phase 1 in feature branch, thorough testing |
| Caching issues cause stale builds | Low | Medium | Cache version keys, manual cache clearing docs |
| Security checks too strict | Medium | Medium | Document exception process, start with warnings |
| Test flakiness with real DB | Medium | High | Implement test retries, health checks |
| Team resistance to new patterns | Low | Medium | Documentation, pair programming sessions |

---

## 6. Documentation Requirements

### Updates to AGENTS.md
- [ ] Document composite actions
- [ ] Update CI/CD section
- [ ] Document Python version policy
- [ ] Document environment variable format
- [ ] Document workflow trigger patterns

### New Documentation
- [ ] `docs/ci-cd.md` - Comprehensive CI/CD guide
- [ ] `docs/security-scanning.md` - Security check reference
- [ ] `docs/troubleshooting-ci.md` - Common issues and fixes

### Runbooks
- [ ] How to handle security scan failures
- [ ] How to clear GitHub Actions cache
- [ ] How to manually trigger workflows
- [ ] How to add new CI checks

---

## 7. Success Criteria Checklist

### Phase 1 Completion
- [ ] Security scans fail builds on real issues
- [ ] Test job connects to real PostgreSQL and Redis
- [ ] No phantom script references exist

### Phase 2 Completion
- [ ] All jobs use composite actions
- [ ] Pipeline duration < 5 minutes
- [ ] Quality guardrails consolidated to single job

### Phase 3 Completion
- [ ] Python 3.12 used consistently
- [ ] No duplicate environment variables
- [ ] Consistent path filters across workflows

### Phase 4 Completion
- [ ] Docker images tagged with versions
- [ ] Multi-arch builds working
- [ ] Container scanning in place

### Phase 5 Completion
- [ ] Dependabot creating PRs
- [ ] Release workflow functional
- [ ] Integration tests running nightly

---

## 8. Appendix

### A. Current Workflow Lines of Code

| File | Lines | Purpose |
|------|-------|---------|
| ci.yml | 158 | Main CI pipeline |
| code-quality-guardrails.yml | 243 | Quality checks |
| **Total** | **401** | |

**Target:** <200 lines through consolidation and composite actions.

### B. Resource Utilization

**Current (per PR):**
- 13 job runs × ~3 minutes = 39 job-minutes
- 7 quality jobs × ~2 minutes = 14 job-minutes
- **Total: ~53 job-minutes per PR**

**Target:**
- 5 job runs × ~2 minutes = 10 job-minutes
- **Total: ~10 job-minutes per PR**

**Savings: ~80% reduction in compute time**

### C. References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Composite Actions Guide](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Security Hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Trivy Scanner](https://github.com/aquasecurity/trivy-action)

---

*Last Updated: 2026-03-06*
*Author: Sisyphus (AI Assistant)*
*Reviewers: Platform Team, Engineering Leads*
