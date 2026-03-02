# 🚀 Getting Started with Solstein

**Your guide to navigating the competitive intelligence platform — from zero to scored companies in five minutes.**

---

## Table of Contents

- [Welcome](#welcome)
- [Five-Minute Quickstart](#five-minute-quickstart)
- [Recommended Reading Order](#recommended-reading-order)
- [Key Concepts](#key-concepts)
- [Common Tasks](#common-tasks)
- [Next Steps](#next-steps)

---

## Welcome

Solstein is an AI-powered competitive intelligence platform built for PE/VC professionals. It replaces the traditional 90-day, EUR 500K consulting engagement with automated market intelligence delivered in days. Feed it a market universe of companies, and Solstein scores, classifies, and ranks them across growth, financial health, and competitive position — producing an interactive **Attractiveness Board** where every score is traceable to its underlying signal. No black boxes, no "trust the algorithm."

> For the full business context, see the [Executive Brief](../PITCH/executive-brief.md) or the [Origin Story](../LORE/origin.md).

---

## Five-Minute Quickstart

**Goal**: Get the API running locally and verify it responds.

**Prerequisites**: Python 3.10+, Redis 5.0+ (see [Developer Guide](developer.md#redis-dependency) for Redis setup options).

### 1. Clone and install

```bash
git clone <repo-url> && cd solstein
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

### 2. Start Redis (if not already running)

```bash
# Docker (recommended)
docker run -d -p 6379:6379 redis:7-alpine

# Verify
redis-cli ping   # Expected: PONG
```

### 3. Start the API

```bash
PYTHONPATH=src uvicorn solstein.api.main:app --reload
```

### 4. Verify it's alive

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T10:00:00Z"
}
```

### 5. Open interactive docs

Navigate to **http://localhost:8000/docs** in your browser to explore all endpoints via Swagger UI.

> **Optional**: Start a Celery worker in a separate terminal for background tasks:
> ```bash
> celery -A solstein.worker worker --loglevel=info
> ```

**Estimated time**: ~5 minutes (including Redis setup).

---

## Recommended Reading Order

Pick the path that matches your role. Each path builds knowledge progressively.

### 🔌 API Users — "I want to integrate with Solstein"

| Order | Document | What You'll Learn | Time |
|-------|----------|-------------------|------|
| 1 | **[Getting Started](getting-started.md)** (this page) | Overview, quickstart, key concepts | 5 min |
| 2 | **[API Reference](../api/reference.md)** | All endpoints, request/response schemas, error codes | 15 min |
| 3 | **[Rate Limiting Guide](rate-limiting.md)** | Request limits, client identification, 429 handling | 5 min |
| 4 | **[Health Checks Guide](health-checks.md)** | Liveness/readiness probes for monitoring | 5 min |

### 👨‍💻 Developers — "I want to contribute or extend Solstein"

| Order | Document | What You'll Learn | Time |
|-------|----------|-------------------|------|
| 1 | **[Getting Started](getting-started.md)** (this page) | Overview, quickstart, key concepts | 5 min |
| 2 | **[Developer Guide](developer.md)** | Full setup, testing, architecture, contribution workflow | 20 min |
| 3 | **[Async Patterns Guide](async-patterns.md)** | Celery tasks, async/await, task chaining | 15 min |
| 4 | **[Connector Enrichment Guide](connector-enrichment.md)** | Data sources, enrichment pipeline, adding connectors | 10 min |
| 5 | **[Extending Solstein](extending-solstein.md)** | Add scoring dimensions, exporters, data sources | 15 min |
| 6 | **[Architecture Decisions](../architecture/decisions.md)** | Why FastAPI, Celery, JSON files, 6-layer testing | 10 min |

### 👨‍✈️ Operators — "I need to deploy and monitor Solstein"

| Order | Document | What You'll Learn | Time |
|-------|----------|-------------------|------|
| 1 | **[Getting Started](getting-started.md)** (this page) | Overview, quickstart, key concepts | 5 min |
| 2 | **[Operator Guide](operator.md)** | Deployment, Docker, environment variables, monitoring | 20 min |
| 3 | **[Health Checks Guide](health-checks.md)** | Kubernetes probes, health endpoints, alerting | 5 min |
| 4 | **[Database Guide](database.md)** | PostgreSQL/Supabase setup, migrations, backups | 15 min |
| 5 | **[Troubleshooting Guide](troubleshooting.md)** | Diagnostic flowcharts for common issues | 10 min |

### 👨‍💼 Business Stakeholders — "I want to understand the platform"

| Order | Document | What You'll Learn | Time |
|-------|----------|-------------------|------|
| 1 | **[Executive Brief](../PITCH/executive-brief.md)** | One-page investment thesis | 3 min |
| 2 | **[Case Study](../PITCH/case-study.md)** | Live proof: 29 companies scored in 3 days | 10 min |
| 3 | **[Origin Story](../LORE/origin.md)** | The vision — Gravity of Legacy, the Sunstone | 10 min |
| 4 | **[Business Model](../PITCH/business-model.md)** | Pricing tiers and commercial strategy | 5 min |

---

## Key Concepts

Understanding these three concepts is essential before working with Solstein.

### Scoring

Every company is scored across three dimensions on a 0–10 scale:

| Dimension | What It Measures | Key Signals |
|-----------|-----------------|-------------|
| **Growth Score** | Revenue trajectory, margin health | Revenue growth rate, gross margin trends |
| **Financial Health Score** | Scale, funding cushion, efficiency | Total revenue, cash reserves, burn rate |
| **Competitive Position Score** | AI maturity, SaaS adoption, tech depth | Technology stack, AI integration, SaaS metrics |

Scores are combined into an overall **Attractiveness Score** used for ranking. Every score exposes its full signal chain — you can drill down to see exactly which data points contributed to each number.

> Deep dive: [API Reference — Scoring Endpoints](../api/reference.md)

### Classification

Based on the overall score, each company receives one of three classifications:

| Classification | Score Range | Meaning |
|---------------|-------------|---------|
| 🔥 **Phoenix** | ≥ 7.0 | High-growth, AI-native. Top acquisition targets. |
| 🧂 **Salt** | 4.0 – 7.0 | Stable players. Watch for directional signals. |
| ⚖️ **Lead** | ≤ 4.0 | Legacy weight. Hidden diamonds or transformation targets. |

> See the classification system in action: [Case Study](../PITCH/case-study.md)

### Enrichment

Solstein fills gaps in company data using external connectors:

| Connector | Data Source | What It Provides |
|-----------|------------|-----------------|
| **SEC EDGAR** | US public filings | Revenue, margins, financial statements |
| **Companies House** | UK company registry | Registration data, financial filings |
| **News Signals** | Real-time news | Funding rounds, partnerships, key hires |

The enrichment pipeline runs automatically during data loading, or can be triggered manually via the async API.

> Deep dive: [Connector Enrichment Guide](connector-enrichment.md) · [Async Patterns Guide](async-patterns.md)

---

## Common Tasks

Quick links to the most frequently needed operations.

### How do I score a company?

```bash
curl -X POST http://localhost:8000/scoring/company/{company-id}/score
```

> Full details: [API Reference — Score a Company](../api/reference.md)

### How do I enrich company data?

```bash
# Start async enrichment
curl -X POST http://localhost:8000/async/enrich/single \
  -H "Content-Type: application/json" \
  -d '{"company_id": "company-id"}'

# Check job status
curl http://localhost:8000/async/jobs/{job_id}/status
```

> Full details: [Connector Enrichment Guide](connector-enrichment.md) · [API Reference — Async Endpoints](../api/reference.md)

### How do I export results?

```bash
# Export as Excel dashboard
curl http://localhost:8000/export/excel --output report.xlsx

# Export as JSON
curl http://localhost:8000/export/json --output report.json
```

> Full details: [API Reference — Export Endpoints](../api/reference.md)

### How do I deploy Solstein?

```bash
# Docker Compose (recommended)
docker compose -f docker/docker-compose.yml up -d

# Verify deployment
curl http://your-server:8000/health
```

> Full details: [Operator Guide](operator.md) · [Health Checks Guide](health-checks.md)

### How do I run the test suite?

```bash
pytest tests/ --cov=src/solstein
```

> Full details: [Developer Guide — Testing](developer.md)

### How do I add a new data source or scoring dimension?

> See: [Extending Solstein](extending-solstein.md)

---

## Next Steps

Now that you have the basics, explore the full documentation:

| Category | Documents |
|----------|-----------|
| **API & Integration** | [API Reference](../api/reference.md) · [Rate Limiting](rate-limiting.md) · [Retry Logic](retry-logic.md) |
| **Development** | [Developer Guide](developer.md) · [Async Patterns](async-patterns.md) · [Extending Solstein](extending-solstein.md) |
| **Operations** | [Operator Guide](operator.md) · [Health Checks](health-checks.md) · [Database Guide](database.md) · [Troubleshooting](troubleshooting.md) |
| **Architecture** | [Architecture Decisions](../architecture/decisions.md) · [Data Gathering Stages](data-gathering-stages.md) |
| **Business** | [Executive Brief](../PITCH/executive-brief.md) · [Case Study](../PITCH/case-study.md) · [Business Model](../PITCH/business-model.md) |
| **Lore** | [Origin Story](../LORE/origin.md) · [The Strategic Play](../LORE/the-play.md) · [The Grimoire](../LORE/grimoire.md) |

---

*Built by* **AI Whisperers** *— finding the diamonds nobody knew were there.*
