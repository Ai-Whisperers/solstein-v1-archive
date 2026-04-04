# STORY-312: Run all Alembic migrations on deployed database

| Field | Value |
|-------|-------|
| **Epic** | EPIC-078 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-311 |

## Description

Run all Alembic migrations on the deployed PostgreSQL database. Verify all tables are created correctly including the new `data_source_type` column (STORY-384).

## Acceptance Criteria

- [ ] `alembic upgrade head` completes without error
- [ ] All expected tables exist (company_records, research_jobs, tenant_records, etc.)
- [ ] `data_source_type` column exists on `company_records` table
- [ ] `alembic current` shows head revision
