# STORY-005: Propagate Input Sanitization to All Routers

| Field | Value |
|-------|-------|
| Status | ⚫ Superseded |
| Superseded By | [STORY-069: Migrate Error Handling and Input Sanitization](../../../EPIC-020-supabase-auth-migration/STORIES/STORY-069-error-handling-sanitization.md) |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-001: Security Restoration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-002](STORY-002-remove-auth-bypass.md) (Auth bypass must be removed first — sanitizing inputs that skip auth entirely is theatre) |

---

## The Audit Verdict

> `data/security_hardening.py` is a 410-line module of input sanitization, SQL injection prevention, and XSS protection utilities. It is imported in 2 of the platform's 10+ routers. The other 80% process user-supplied strings directly without any sanitization.

## Problem Statement

The security sanitization utilities exist and are functional but are applied inconsistently. Routers handling company names, search queries, date ranges, and filter parameters receive user input without sanitization. The platform has invested in building a comprehensive security hardening module and then failed to use it.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Injection attack surface exists across the majority of the API surface area |
| **Consistency** | Security posture varies per-router, creating unpredictable attack vectors that resist systematic analysis |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/security_hardening.py` | Reference only | Sanitization utilities to be reused — do not duplicate |
| `src/solstein/api/routers/companies.py` | Modify | Apply sanitization to all string parameters |
| `src/solstein/api/routers/enrichment.py` | Modify | Apply sanitization to all string parameters |
| `src/solstein/api/routers/scoring.py` | Modify | Apply sanitization to all string parameters |
| `src/solstein/api/dependencies.py` | Modify/Add | Create FastAPI Depends wrapper for sanitization |
| `tests/unit/test_routers_sanitization.py` | Add | Injection tests per router |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A central FastAPI `Depends` wrapper must apply sanitization to all user-supplied string inputs, eliminating per-router opt-in
- **REQ-2**: `security_hardening.py` must be imported and reused — its functions must not be duplicated in router files
- **REQ-3**: Each sanitization function must have documented behavior for which input types it applies to
- **REQ-4**: The sanitization layer must log (at DEBUG level) when input is modified, for traceability

## Acceptance Criteria

- [ ] All 10+ routers apply input sanitization via the central dependency
- [ ] SQL injection payloads sent to any string parameter are rejected or escaped
- [ ] XSS payloads sent to any string parameter are rejected or escaped
- [ ] Grep for `security_hardening` shows it imported in the dependencies module, not duplicated per router
- [ ] No router file contains its own inline sanitization logic

## Definition of Done

**Tests Required:**
- [ ] Parameterized tests: known SQL injection patterns against each router's string parameters
- [ ] Parameterized tests: known XSS patterns against each router's string parameters
- [ ] Test: sanitization modifies input and DEBUG log entry is produced

**Documentation Required:**
- [ ] Each sanitization function documented with: what it sanitizes, what input types it applies to, and what it does with rejected input

**Code Review Gate:**
- [ ] Reviewer confirms no router file imports `security_hardening.py` directly — all access is through the central dependency
- [ ] Reviewer confirms no string parameter in any endpoint bypasses sanitization

## Notes

This story depends on STORY-002. Sanitizing inputs to endpoints that skip authentication is security theatre — it protects the format of the injection but not who's injecting. Fix access control first, then ensure everything passing through access control is also sanitized.
