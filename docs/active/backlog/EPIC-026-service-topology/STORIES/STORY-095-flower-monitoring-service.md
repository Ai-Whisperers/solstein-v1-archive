# STORY-095: Add Flower Monitoring Service to docker-compose

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Medium |
| **Epic** | EPIC-026: Service Topology |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-093 (worker must exist for Flower to monitor) |

## The Audit Verdict
> No Flower or Celery monitoring service exists anywhere in the codebase. Worker state, task history, queue depths, and failure rates are invisible without SSH access to Redis.

## Problem Statement

The worker system is a black box. There is no operational visibility into queue depths, active tasks, task failure rates, worker concurrency, or Beat schedule state. When the research pipeline stops producing data, the only diagnostic tool is reading raw Redis keys via `redis-cli` — assuming you have SSH access to the host, which you shouldn't in a properly secured production environment.

Flower provides a web UI and REST API for all of this out of the box. It shows which workers are connected, what they're processing, how deep the queues are, and what's been failing. Not having it is an operational choice that trades hours of debugging time for the cost of adding one compose service and a Docker image pull.

The absence of monitoring compounds every other reliability issue in EPIC-025. Failed tasks go to the DLQ (STORY-088), but who checks the DLQ? Workers crash and tasks re-queue (STORY-089), but who notices the crash? Flower doesn't fix these issues — but it makes them visible, which is the prerequisite to fixing them.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Failures are invisible until downstream effects are noticed (stale data, missing reports) |
| **Operational** | Zero visibility into worker health, queue depth, task throughput, or failure rates |
| **Data Integrity** | No early warning for accumulating failures before they reach data-corruption thresholds |
| **Developer Experience** | Production debugging requires Redis key archaeology and log file grep sessions |

## Affected Files

| File | Issue |
|------|-------|
| `docker-compose.yml` | No monitoring service for the Celery worker system |

## Architectural Requirements
- A `flower` service in docker-compose using the `mher/flower` image (or latest stable equivalent)
- Connects to the same Redis broker as workers via `CELERY_BROKER_URL` environment variable
- Basic auth configured via environment variables `FLOWER_USER` and `FLOWER_PASSWORD` — these must NOT be hardcoded
- Exposed on port 5555 (configurable via environment variable `FLOWER_PORT`)
- `depends_on`: `redis`, `worker`
- Restart policy: `unless-stopped`
- Flower must NOT be exposed publicly — production deployment must place it behind API gateway, VPN, or internal-only network
- Flower persistent state (task history database) stored in a named volume so task history survives Flower container restarts
- `worker_send_task_events = True` must be set in celery_config to enable Flower's real-time task monitoring

## Acceptance Criteria
- [ ] `docker compose up` starts Flower and it displays worker state at `http://localhost:5555`
- [ ] Flower shows all 4 queues (default, scoring, export, enrichment) with depth metrics
- [ ] Flower shows task success/failure history with error details
- [ ] Basic auth prevents unauthenticated access (HTTP 401 without credentials)
- [ ] Flower is excluded from public-facing ingress configuration (documented, not just implied)

## Definition of Done
- **Tests Required**: Integration test: `docker compose up`, verify Flower responds on configured port with auth. Verify worker appears in Flower's worker list.
- **Documentation Required**: Document Flower access for operators. Document that Flower must be VPN/internal-only in production.
- **Code Review Gate**: Reviewer verifies auth is enabled and credentials are from environment variables, not hardcoded. Reviewer confirms `worker_send_task_events` is enabled.

## Notes
- Flower is a monitoring tool, not an alerting tool. It provides the visibility layer; alerting should be built on top via Prometheus metrics export (Flower supports this) or the DLQ alerting from STORY-088.
- The `mher/flower` image is the community-maintained Docker image. Pin to a specific version tag in the compose file — do not use `latest` in production.
- Flower's persistent database (`--db` flag) should be pointed at a volume-mounted path so task history is not lost on container recreation. Without this, restarting Flower wipes all historical task data.
- In production, consider running Flower with `--auto_refresh=False` to reduce Redis polling load, and let operators refresh manually.
