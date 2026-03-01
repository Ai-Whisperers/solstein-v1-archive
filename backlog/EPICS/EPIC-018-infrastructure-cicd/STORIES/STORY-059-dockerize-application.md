# STORY-059: Dockerize the Application with a Multi-Stage Build

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-007: Remove Hardcoded Credentials](../../EPIC-001-security-restoration/STORIES/STORY-007.md), [STORY-008: Startup Validation](../../EPIC-002-configuration-integrity/STORIES/STORY-008.md) |

---

## The Audit Verdict
> No Dockerfile exists. The application runs on bare metal or a virtual machine configured by undocumented manual steps. The deployment environment cannot be reproduced, audited, or versioned.

## Problem Statement
Without a Dockerfile, the application environment exists only on the machines where it was manually configured. A new deployment requires recreating those manual steps from memory or tribal knowledge. Production debugging requires access to the production server because the environment cannot be replicated. A hardware failure requires rebuilding the environment from scratch — assuming someone documented the configuration, which they did not.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reproducibility** | Production environment cannot be replicated for debugging — "works in production but not locally" is unsolvable |
| **Portability** | Deployment is tied to a specific operating system and configuration — migrating to a new host is a manual, error-prone process |
| **Security** | No container isolation between the application and the host — a compromised application has access to the entire host |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `Dockerfile` | Add | Create at repository root: multi-stage build |
| `docker-compose.yml` | Add | Create: full local development stack |
| `.dockerignore` | Add | Create: exclude unnecessary files from build context |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A multi-stage `Dockerfile` must be created: a build stage that installs dependencies and runs tests, and a production stage that contains only the runtime and application code
- **REQ-2**: The production image must not contain development dependencies, test files, or source code build artifacts
- **REQ-3**: All configuration must be injected via environment variables — no configuration files may be baked into the image
- **REQ-4**: The image must run as a non-root user
- **REQ-5**: Image size must be minimised — use a slim or alpine base image appropriate for Python 3.11
- **REQ-6**: A `docker-compose.yml` must define the full local development stack including PostgreSQL and Redis with appropriate health checks

## Acceptance Criteria
- [ ] `docker build .` succeeds from a clean repository
- [ ] The production image runs as a non-root user
- [ ] The production image does not contain test files or dev dependencies
- [ ] `docker-compose up` brings up the full local stack including database and Redis
- [ ] The containerised application responds to a health check request

## Definition of Done

**Tests Required:**
- [ ] Build the image in CI and verify it completes successfully
- [ ] Run the containerised application and verify the health endpoint responds
- [ ] Verify non-root user: `docker run --rm <image> whoami` returns non-root

**Documentation Required:**
- [ ] Docker setup documented in AGENTS.md
- [ ] docker-compose usage documented for local development

**Code Review Gate:**
- [ ] Reviewer confirms no configuration is baked into the image
- [ ] Reviewer confirms production stage does not include test files or dev dependencies
- [ ] Reviewer confirms non-root user

## Notes
This story depends on STORY-007 (no hardcoded credentials) because the Docker image must accept all credentials via environment variables. It depends on STORY-008 (startup validation) because the containerised application should validate its configuration at startup and fail clearly if required variables are missing. The docker-compose.yml should include health checks for PostgreSQL and Redis so that the application container waits for dependencies to be ready before starting.
