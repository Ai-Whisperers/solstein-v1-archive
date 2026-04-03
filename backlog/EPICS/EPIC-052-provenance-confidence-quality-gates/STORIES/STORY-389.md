# STORY-389: Fix SEC EDGAR connectors — replace `solstein@example.com` placeholder with configured email

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

Both SEC EDGAR connector files use a placeholder email as the default parameter:

```python
# src/solstein/connectors/financial/sec_edgar.py:18
def __init__(self, email: str = "solstein@example.com"):

# src/solstein/connectors/financial/extra.py:25
def __init__(self, email: str = "solstein@example.com"):
```

The SEC EDGAR EFTS API requires a real, valid contact email address in the `User-Agent` header
per their [fair access policy](https://efts.sec.gov/LATEST/search-index?q=%22user-agent%22).
The `@example.com` domain is an RFC 2606 reserved domain — it is explicitly not a real email
address. Requests using this address:

1. Violate SEC EDGAR's terms of service
2. May be rejected or rate-limited by the API
3. Cannot be used to contact Solstein if the API operator needs to reach us

Any production enrichment call through either connector that does not explicitly override the
`email` parameter will use the invalid placeholder.

## Fix

1. Remove the default parameter value — make `email` a required argument, or read it from
   `Settings`:

```python
# Option A: Read from settings (preferred)
def __init__(self, email: str | None = None):
    from solstein.config import get_settings
    self.email = email or get_settings().enrichment.sec_edgar_contact_email
    if not self.email or "@example.com" in self.email:
        raise ValueError("SEC EDGAR requires a valid contact email. Set enrichment.sec_edgar_contact_email.")

# Option B: Require explicitly
def __init__(self, email: str):
    self.email = email
```

2. Add `sec_edgar_contact_email: str` to the enrichment settings section in
   `src/solstein/config.py` (or equivalent).
3. Update all callers that currently use the default (relying on the placeholder) to pass
   an explicit email.

## Acceptance Criteria

- [ ] Neither `sec_edgar.py` nor `extra.py` has `"solstein@example.com"` as a default
- [ ] A `ValueError` (or config validation error) is raised if no valid email is configured
- [ ] The email is sourced from `Settings` in production paths
- [ ] Tests that instantiate these connectors use a test email via fixture, not the placeholder

## Files

- `src/solstein/connectors/financial/sec_edgar.py` — line 18
- `src/solstein/connectors/financial/extra.py` — line 25
- `src/solstein/config.py` — add `sec_edgar_contact_email` setting
- Any tests that instantiate either connector without an email override

## Notes

Both files have the identical default — likely copy-paste. Fix both in the same PR.
