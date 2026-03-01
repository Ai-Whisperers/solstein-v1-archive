# STORY-096: Multi-Stage Dockerfile for Production

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-026: Service Topology |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-093 (worker service), STORY-094 (beat service) — all three services must work from the same image |

## The Audit Verdict
> `Dockerfile` — single-stage build. All build dependencies (gcc, build-essential, pip cache) are present in the production image, inflating image size and attack surface.

## Problem Statement

A single-stage Dockerfile produces an image that ships its own build toolchain to production. Every compiler, header file, and pip wheel cache that was needed to compile `psycopg2`, `cryptography`, or other C extensions is baked into the final image. The image carries dead weight that serves no runtime purpose but increases attack surface, image size, and pull times.

Multi-stage builds are a solved problem since Docker 17.05 (2017). The builder stage compiles, the runtime stage copies only the artifacts. This is not cutting-edge technique — it's baseline Docker hygiene that was skipped during initial setup and never revisited.

The single-stage image also runs as root by default, which means a container escape vulnerability gives the attacker root access to the host. Running as a non-root user is another baseline practice that costs one line in the Dockerfile.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Larger images mean slower container pulls and longer recovery times during scaling events |
| **Operational** | Image storage costs scale linearly with bloated image size; CI/CD pipeline time wasted on unnecessary layers |
| **Data Integrity** | No direct impact |
| **Developer Experience** | Local builds are slower than necessary; image caching is less effective with a monolithic single stage |

## Affected Files

| File | Issue |
|------|-------|
| `Dockerfile` | Single-stage build — ships build tools (gcc, build-essential, pip cache) to production |
| `.dockerignore` | May be missing or incomplete — build context likely includes tests, docs, git history |

## Architectural Requirements
- Stage 1 (`builder`): installs build dependencies (gcc, build-essential, libpq-dev), compiles C extensions, creates a virtual environment with all packages installed
- Stage 2 (`runtime`): starts from a slim Python base image (e.g., `python:3.11-slim`), copies only the virtualenv from builder, copies only application source code
- Final image must contain NO pip, NO gcc, NO build-essential, NO pip cache, NO wheel files
- Image size target: ≤500MB (document current image size as baseline before the change)
- Non-root user in runtime stage: `USER solstein` with a dedicated UID/GID
- `.dockerignore` must be updated to exclude: `.git/`, `tests/`, `docs/`, `dashboard/`, `*.pyc`, `__pycache__/`, `.env`, `.venv/`, `*.md` (except LICENSE), `backlog/`
- The same Dockerfile must be used for `api`, `worker`, and `beat` services — differentiation is via command override in docker-compose, NOT via separate Dockerfiles
- `ENTRYPOINT` should use `exec` form (JSON array), not shell form, for proper signal handling
- `HEALTHCHECK` instruction should be included for the default (API) use case; worker and beat override via compose

## Acceptance Criteria
- [ ] Final image size is ≤500MB (measured via `docker images`)
- [ ] `gcc` and `pip` are NOT present in the runtime layer (`docker exec <container> which gcc` returns nothing)
- [ ] All three services (`api`, `worker`, `beat`) run correctly from the single multi-stage image
- [ ] Container runs as non-root user (verified via `docker exec <container> whoami`)
- [ ] CI build time is documented before and after the change
- [ ] `.dockerignore` excludes all non-runtime files

## Definition of Done
- **Tests Required**: `docker build` succeeds. All three service commands (`uvicorn`, `celery worker`, `celery beat`) work from the built image. Non-root user verification. Image size assertion.
- **Documentation Required**: Document image size before/after. Document the build stage architecture. Update CI/CD pipeline docs if build commands change.
- **Code Review Gate**: Reviewer runs `docker image inspect` to verify non-root user configuration. Reviewer runs `docker exec` to confirm absence of build tools. Reviewer verifies `.dockerignore` completeness.

## Notes
- Measure the current image size before starting. Include this in the PR description as the baseline. A typical single-stage Python image with scientific/data dependencies is 1.2-1.8GB; the multi-stage target of ≤500MB is achievable for this stack.
- The `python:3.11-slim` base is ~120MB. The virtualenv with all dependencies will be the bulk of the remaining size. If the image exceeds 500MB, investigate whether any large dependencies (e.g., `torch`, `tensorflow`) are being installed unnecessarily.
- Signal handling matters: if the entrypoint uses shell form (`CMD celery worker ...`), SIGTERM is sent to the shell, not to Celery. This means graceful shutdown doesn't work. Use exec form (`CMD ["celery", "-A", "solstein.celery_app", "worker"]`) or `exec` in a shell entrypoint script.
- The non-root user must own the application directory and any directories the application writes to (logs, temp files). Map these out before setting `USER`.
