# Solstein Database Schema

## Overview

Solstein uses PostgreSQL 14+ with 21 tables organized into logical groups. All tables use UUID primary keys and include `created_at` and `updated_at` timestamps.

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌───────────┐
│  companies  │◄──────┤  research_runs  │◄──────┤   facts   │
└─────────────┘       └─────────────────┘       └───────────┘
       │                      │                        │
       │                      ▼                        │
       │              ┌─────────────────┐              │
       └─────────────►│     signals     │◄─────────────┘
                      └─────────────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
┌──────────────┐   ┌─────────────────┐   ┌─────────────────┐
│scoring_records│   │ contradictions  │   │source_documents │
└──────────────┘   └─────────────────┘   └─────────────────┘
```

## Core Tables

### companies

Primary entity table for companies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| ticker | VARCHAR(20) | NOT NULL, UNIQUE | Stock ticker symbol |
| name | VARCHAR(255) | NOT NULL | Company name |
| status | VARCHAR(20) | CHECK | active, inactive, archived |
| sector | VARCHAR(100) | | Industry sector |
| industry | VARCHAR(100) | | Specific industry |
| metadata | JSONB | | Flexible metadata storage |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_companies_status_ticker` (status, ticker)
- `idx_companies_active` (ticker, name) WHERE status = 'active'

### research_runs

Tracks research execution runs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| status | VARCHAR(50) | CHECK | pending, running, completed, failed |
| temporal_run_id | VARCHAR(255) | | Temporal workflow ID |
| metadata | JSONB | | Run configuration |
| run_metadata | JSONB | | Run results |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |
| completed_at | TIMESTAMPTZ | | Completion timestamp |

**Foreign Keys:**
- `fk_research_runs_company` → companies(id) ON DELETE CASCADE

### facts

Extracted factual data from research.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| run_id | UUID | FK → research_runs | Source research run |
| fact_key | VARCHAR(255) | NOT NULL | Fact identifier |
| fact_value | TEXT | | Fact value |
| confidence | DECIMAL(3,2) | CHECK 0-1 | Confidence score |
| status | VARCHAR(20) | CHECK | active, superseded, retracted |
| source | VARCHAR(255) | | Data source |
| superseded_at | TIMESTAMPTZ | | When superseded |
| superseded_reason | TEXT | | Reason for supersession |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_facts_company_status` (company_id, status)
- `idx_facts_high_confidence` (company_id, confidence) WHERE confidence >= 0.8

### signals

Detected market signals.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| run_id | UUID | FK → research_runs | Source research run |
| signal_type | VARCHAR(50) | CHECK | price_movement, volume_spike, etc. |
| direction | VARCHAR(20) | CHECK | bullish, bearish, neutral |
| confidence | DECIMAL(3,2) | CHECK 0-1 | Confidence score |
| strength | DECIMAL(3,2) | CHECK 0-1 | Signal strength |
| status | VARCHAR(20) | CHECK | active, resolved, expired |
| detected_at | TIMESTAMPTZ | NOT NULL | Detection timestamp |
| expires_at | TIMESTAMPTZ | | Expiration timestamp |
| metadata | JSONB | | Signal metadata |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

## Scoring Tables

### scoring_records

Company scoring results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| total_score | INTEGER | CHECK 0-100 | Overall score |
| growth_score | INTEGER | CHECK 0-100 | Growth component |
| profitability_score | INTEGER | CHECK 0-100 | Profitability component |
| valuation_score | INTEGER | CHECK 0-100 | Valuation component |
| quality_score | INTEGER | CHECK 0-100 | Quality component |
| quartile | INTEGER | CHECK 1-4 | Score quartile |
| scored_at | TIMESTAMPTZ | NOT NULL | Scoring timestamp |
| metadata | JSONB | | Scoring metadata |

### signal_records

Generated signal records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| score | INTEGER | CHECK 0-100 | Signal score |
| signal_type | VARCHAR(20) | CHECK | bullish, bearish, neutral |
| strength | VARCHAR(20) | CHECK | weak, moderate, strong |
| generated_at | TIMESTAMPTZ | NOT NULL | Generation timestamp |
| metadata | JSONB | | Signal metadata |

## Enrichment Tables

### company_enrichment_queue

Pending enrichment jobs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Company to enrich |
| status | VARCHAR(20) | CHECK | pending, processing, completed |
| priority | INTEGER | CHECK 0-100 | Job priority |
| scheduled_at | TIMESTAMPTZ | | Scheduled time |
| completed_at | TIMESTAMPTZ | | Completion time |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

### enrichment_results

Enrichment job results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| enrichment_type | VARCHAR(50) | NOT NULL | Type of enrichment |
| status | VARCHAR(20) | CHECK | success, partial, failed |
| data | JSONB | | Enrichment data |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |

### enrichment_cache

Cached enrichment data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| data_source | VARCHAR(100) | NOT NULL | Data source name |
| cache_key | VARCHAR(255) | NOT NULL | Cache key |
| data | JSONB | | Cached data |
| expires_at | TIMESTAMPTZ | NOT NULL | Expiration time |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |

## Audit Tables

### audit_trails

Audit logging for all changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company (optional) |
| run_id | UUID | FK → research_runs | Related run (optional) |
| entity_type | VARCHAR(50) | CHECK | Type of entity |
| entity_id | UUID | NOT NULL | Entity identifier |
| action | VARCHAR(20) | CHECK | create, update, delete |
| old_values | JSONB | | Previous values |
| new_values | JSONB | | New values |
| performed_by | VARCHAR(255) | | User who performed action |
| created_at | TIMESTAMPTZ | NOT NULL | Timestamp |

### enrichment_audit

Enrichment-specific audit log.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| data_source | VARCHAR(100) | NOT NULL | Data source |
| status | VARCHAR(20) | CHECK | success, failed |
| request_data | JSONB | | Request details |
| response_data | JSONB | | Response data |
| error_message | TEXT | | Error if failed |
| duration_ms | INTEGER | | Processing time |
| created_at | TIMESTAMPTZ | NOT NULL | Timestamp |

## Utility Tables

### outbox_records

Event outbox for reliable message publishing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| run_id | UUID | FK → research_runs | Related run |
| event_type | VARCHAR(100) | NOT NULL | Type of event |
| payload | JSONB | NOT NULL | Event payload |
| status | VARCHAR(20) | CHECK | pending, processing, completed |
| retry_count | INTEGER | CHECK >= 0 | Retry attempts |
| max_retries | INTEGER | CHECK 0-10 | Max retry attempts |
| last_error | TEXT | | Last error message |
| processed_at | TIMESTAMPTZ | | Processing timestamp |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |

### market_snapshots

Market data snapshots.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company (optional) |
| snapshot_type | VARCHAR(50) | NOT NULL | Type of snapshot |
| data | JSONB | NOT NULL | Market data |
| recorded_at | TIMESTAMPTZ | NOT NULL | Recording timestamp |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |

### source_document_snapshots

Source document snapshots.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| run_id | UUID | FK → research_runs | Related run |
| source_url | TEXT | | Document URL |
| document_type | VARCHAR(50) | | Type of document |
| content_hash | VARCHAR(64) | | Content hash |
| snapshot_data | JSONB | | Document data |
| captured_at | TIMESTAMPTZ | NOT NULL | Capture timestamp |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |

### contradictions

Fact contradictions detected.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| company_id | UUID | FK → companies | Related company |
| run_id | UUID | FK → research_runs | Detection run |
| fact_1_id | UUID | NOT NULL | First fact |
| fact_2_id | UUID | NOT NULL | Second fact |
| severity | VARCHAR(20) | CHECK | low, medium, high, critical |
| status | VARCHAR(20) | CHECK | open, investigating, resolved |
| resolution_status | VARCHAR(50) | | How resolved |
| detected_at | TIMESTAMPTZ | NOT NULL | Detection timestamp |
| resolved_at | TIMESTAMPTZ | | Resolution timestamp |
| created_at | TIMESTAMPTZ | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

## Constraints Summary

### Foreign Keys
- 20+ foreign key constraints
- All use ON DELETE CASCADE (except market_snapshots which uses SET NULL)

### CHECK Constraints
- Score ranges: 0-100
- Confidence ranges: 0-1
- Status enum values
- Date consistency (updated_at >= created_at)

### NOT NULL
- Primary keys
- Required foreign keys
- Timestamps (created_at, updated_at)
- Required status fields

## Indexes Summary

### Composite Indexes
- Multi-column indexes for common query patterns
- Covering indexes for join operations

### Partial Indexes
- Active records only (WHERE status = 'active')
- Pending jobs (WHERE status IN ('pending', 'queued'))
- High confidence facts (WHERE confidence >= 0.8)

### Total Indexes
- 40+ indexes across all tables
- Optimized for read-heavy workloads

## Migrations

Schema managed through numbered migration files:

```
supabase/migrations/
├── 001_companies.sql
├── 002_research_runs.sql
├── 003_facts.sql
├── 004_signals.sql
├── 005_contradictions.sql
├── 006_source_documents.sql
├── 007_scoring_records.sql
├── 008_enrichment_tables.sql
├── 009_market_snapshots.sql
├── 010_audit_trails.sql
├── 011_foreign_keys.sql
├── 012_database_constraints.sql
└── 013_optimized_indexes.sql
```

---

**Last Updated**: 2024
**Schema Version**: 13
