# Migration Rollback Runbook

## When to Use

Use this runbook when a migration must be reversed because it caused data issues, schema incompatibility with the running API, or deployment failure.

## Prerequisites

- Database credentials for the target environment
- `alembic` installed (`pip install alembic`)
- Access to the project repository

## Step 1: Assess the Situation

Check the current migration state:

```bash
alembic current
```

Check what the previous revision was:

```bash
alembic history --verbose | head -20
```

## Step 2: Rollback the Last Migration

Roll back one revision:

```bash
alembic downgrade -1
```

Verify the rollback succeeded:

```bash
alembic current
```

## Step 3: Rollback to a Specific Revision

If you need to roll back multiple migrations:

```bash
# Roll back to a specific revision
alembic downgrade <revision_hash>

# Roll back to base (all migrations reversed - DANGEROUS)
# alembic downgrade base
```

## Step 4: Verify Data Integrity

After rollback, verify the database schema matches the API version currently deployed:

```bash
# Check that the API health endpoint works
curl -f http://localhost:8000/api/v1/health

# Verify key tables exist and are accessible
alembic current
```

## Step 5: Deploy the Previous API Version

If the rollback was caused by a new API version expecting the new schema, you may need to roll back the API deployment as well. The old API version should work with the old schema.

## Using make targets

For convenience, the Makefile provides:

```bash
make migrate-rollback    # Roll back the last migration
make migrate-status      # Show current and head revisions
make migrate-dry-run     # Preview what would be applied
make migrate             # Apply pending migrations
```

## Automated Migration in CI/CD

Migrations run automatically before deploy in both staging and production workflows. If a migration fails, the deploy step is skipped and the previous API version continues serving traffic on the old schema. This is the safe default.

## Emergency Contacts

If a migration rollback fails or causes data corruption, escalate to the database administrator and halt all deployments until the issue is resolved.
