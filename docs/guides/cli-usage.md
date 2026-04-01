# Solstein CLI Usage Guide

STORY-118: The CLI is a first-class API client entrypoint.

## Installation

```bash
pip install -e .
solstein --help
```

## Authentication

```bash
# Login (stores credentials in ~/.solstein/credentials.json)
solstein login --email user@example.com

# Check auth status
solstein whoami

# Logout
solstein logout
```

The API URL defaults to `http://localhost:8000`. Override with:
- `--api-url` flag on `solstein login`
- `SOLSTEIN_API_URL` environment variable

## Commands

### Companies

```bash
# List companies
solstein companies list
solstein companies list --limit 50 --offset 0

# Get company details
solstein companies get <company_id>
```

### Research

```bash
# Start research (waits for completion by default)
solstein research "Company Name"

# Start without waiting
solstein research "Company Name" --no-wait
```

### Export

```bash
# Export company data
solstein export <company_id> --format excel
solstein export <company_id> --format json
solstein export <company_id> --format markdown
```

### Job Status

```bash
solstein status <job_id>
```

### Health Check

```bash
solstein health
```

## JSON Output

All commands support `--output json` for scripting:

```bash
solstein --output json companies list
solstein --output json whoami
solstein --output json research "Company Name"
```

## Architecture

The CLI calls the Solstein API via HTTP. It does not import domain layers directly. This ensures all operations go through authentication, middleware, rate limiting, and audit logging.

```
solstein CLI  -->  HTTP  -->  Solstein API  -->  Domain Layer
                   ^
                   |
            Auth token from
            ~/.solstein/credentials.json
```

## Legacy CLI

The previous CLI (which calls the domain layer directly) is available as `solstein-legacy` for backward compatibility during migration.
