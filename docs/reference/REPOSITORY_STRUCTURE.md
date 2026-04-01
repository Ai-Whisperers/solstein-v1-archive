# Repository Structure Standards

This document defines the canonical organization of the Solstein repository. All contributors
must follow these conventions. Any addition of root-level files or creation of new directories
requires justification and review.

---

## Root-Level Files (Allowed)

The repository root is reserved for files that **must** live at the top level for tool
discovery or ecosystem convention. No documentation, analysis, or strategic content belongs here.

| File / Pattern | Purpose |
|---|---|
| `README.md` | Project overview and quick-start pointer |
| `LICENSE` | Open-source license |
| `Makefile` | Developer task runner |
| `pyproject.toml` | Python packaging and tool configuration (ruff, mypy, pytest) |
| `pytest.ini` | Pytest configuration |
| `pyrightconfig.json` | Pyright / type checker config |
| `requirements.txt` | Pinned production dependencies |
| `requirements-lock.txt` | Locked dependency manifest |
| `package.json` / `package-lock.json` | Node tooling (pre-commit, JS helpers) |
| `docker-compose.yml` | Local development compose stack |
| `docker-compose.dev.yml` | Development-specific overrides |
| `Dockerfile` / `Dockerfile.dev` | Container build definitions |
| `alembic.ini` | Alembic migration configuration |
| `mkdocs.yml` / `mkdocs.strict.yml` | Documentation site config |
| `opencode.yml` / `opencode-enhanced.yml` | OpenCode agent configuration |
| `sgconfig.yml` | Sourcegraph / code intelligence config |
| `.env.example` | Template for local environment variables |
| `.gitignore` | Git ignore patterns |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |

**Adding a new root-level file requires:**
1. A comment in the PR explaining why it cannot live elsewhere
2. Reviewer approval from a codeowner

---

## Root-Level Directories

| Directory | Contents |
|---|---|
| `src/solstein/` | All application source code |
| `tests/` | Automated tests (mirrors `src/` structure) |
| `docs/` | All documentation (see [docs/ layout](#docs-layout)) |
| `planning/` | Epic and story planning, queue, roadmap |
| `scripts/` | CI scripts, dev utilities, one-off helpers |
| `alembic/` | Database migration files |
| `config/` | Environment-specific configuration files |
| `docker/` | Supplemental Docker assets (not docker-compose) |
| `k8s/` / `kubernetes-deployment.yaml` | Kubernetes manifests |
| `helm/` | Helm chart definitions |
| `terraform/` | Infrastructure-as-code (Terraform) |
| `supabase/` | Supabase project configuration and seed data |
| `.github/` | GitHub Actions, templates, Dependabot config |
| `tooling/` | Developer tooling scripts and helpers |
| `bin/` | Executable entry points |
| `audit/` | Audit output artifacts (generated, not committed) |
| `reports/` | Generated quality reports (not committed) |
| `logs/` | Local log files (gitignored) |
| `site/` | MkDocs build output (gitignored) |
| `data/` | Local sample / fixture data (gitignored in prod) |
| `backlog/` | Deprecated story backlog (archive only) |

---

## `docs/` Layout

All written documentation lives under `docs/`. Subdirectories are organized by audience and
lifecycle stage.

```
docs/
├── README.md                    # Index of all docs subdirectories
├── guides/                      # Canonical how-to guides (setup, deployment, etc.)
├── reference/                   # API reference, schema docs, quick-reference cards
├── architecture/                # System design and ADR records
├── adr/                         # Architecture Decision Records
├── strategy/                    # Strategic documents (calls, roadmaps, pitches)
│   └── calls/                   # Dated call notes: YYYY-MM-DD-<party>.md
├── standards/                   # Coding and process standards
├── internal/                    # Internal operational guides (agent deployment, etc.)
├── archive/                     # Historical documents (read-only, not maintained)
│   └── analysis/                # One-off analysis artifacts
├── deletions/                   # Deletion audit logs (one file per story)
├── security/                    # Security policies and incident response
├── runbooks/                    # Operational runbooks
├── operations/                  # Operational procedures
├── deployment/                  # Deployment guides and rollback plans
├── api/                         # API documentation
├── data/                        # Data model documentation
├── developers/                  # Developer onboarding and contributing guides
├── observability/               # Monitoring and alerting documentation
└── epics/                       # Epic documentation (active and completed)
```

### Naming Conventions

- Use **kebab-case** for all file and directory names: `setup-guide.md`, `api-providers.md`
- Prefix dated documents with `YYYY-MM-DD-`: `2026-02-27-michiel-kuiper.md`
- Use **UPPERCASE** only for index files like `README.md` and legacy files that predate this standard
- Avoid spaces in filenames — use hyphens

### Document Lifecycle

| Stage | Location | Action |
|---|---|---|
| Active | `docs/<category>/` | Maintained and reviewed |
| Superseded | `docs/archive/` | Preserved, redirect added to replacement |
| Deleted | `docs/deletions/STORY-NNN-<description>.md` | Deletion logged with rationale |

---

## `planning/` Layout

```
planning/
├── QUEUE.md         # Canonical story queue (single source of truth for status)
├── ROADMAP.md       # High-level roadmap
├── epics/           # One file per epic with story breakdowns
├── stories/         # Individual story files (if used)
└── archive/         # Completed epic documentation
```

**Queue hygiene rules:**
- `QUEUE.md` is updated only on `develop` branch (never in feature branches)
- Status transitions: `READY` → `IN_PROGRESS` → `DONE`
- Each DONE story must reference its PR number or commit hash

---

## What Does NOT Belong at the Root

The following must **never** be added to the repository root:

- Analysis documents (`*_ANALYSIS.md`, `*_CRITIQUE.md`)
- Architecture documents (use `docs/architecture/`)
- Setup guides (use `docs/guides/`)
- Strategic documents (use `docs/strategy/`)
- Database files (`*.db`, `*.sqlite3`) — add to `.gitignore`
- Log files (`*.log`) — add to `.gitignore`
- One-off scripts (`setup-improvements.sh`) — move to `scripts/` or `tooling/`
- Test result files (`test-results-*.log`) — add to `.gitignore`
- Generated JSON indexes (`context-index.json`) — add to `.gitignore`

---

## Approval Process for Exceptions

If a file genuinely cannot be placed according to these standards:

1. Open a PR with the file at its proposed location
2. Add a comment in the PR explaining the constraint (e.g., "tool X requires this at root")
3. Tag a codeowner for review
4. If approved, add an entry to this document under the appropriate table

---

## Enforcement

This document is referenced in the PR template checklist. Reviewers should verify placement
before approving any PR that adds new files or directories.

A CI check (`scripts/ci/check_root_files.py`) may be added in a future story to automatically
flag unrecognized root-level additions.

---

*Last updated: 2026-03-26 — STORY-168*
