# STORY-070: Fix SSRF Vulnerability in Web and Website Agents

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | CRITICAL |
| Epic | [EPIC-020: Supabase Auth Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `agents/website_agent.py` fetches URLs passed through the research pipeline without validation. A user-supplied or externally-sourced URL can cause the agent to make requests to internal network addresses (`http://localhost/`, `http://169.254.169.254/` AWS metadata endpoint, `http://10.0.0.1/` internal services). No URL allowlist, no scheme validation, no private IP range rejection exists.

## Problem Statement

Server-Side Request Forgery (SSRF) allows an attacker to use the application server as a proxy to reach internal services that are not accessible from the internet — including cloud metadata endpoints, internal APIs, and database management interfaces. This is OWASP A10:2021.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | Attacker can exfiltrate cloud credentials from the AWS metadata endpoint via SSRF |
| **Compliance** | Internal service enumeration possible via the research pipeline |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/agents/website_agent.py` | Modify | Add URL validation before any fetch |
| `src/solstein/agents/web_search_agent.py` | Modify | Same if it fetches arbitrary URLs |
| New shared URL validation utility | Add | Central URL validation for all agents |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: All URLs fetched by any agent must be validated before the HTTP request is made
- **REQ-2**: Validation must reject: private IP ranges (10.x, 172.16-31.x, 192.168.x), loopback (127.x, ::1), link-local (169.254.x), and any non-HTTP/HTTPS scheme
- **REQ-3**: DNS resolution of the target hostname must be checked against private IP ranges after resolution (DNS rebinding prevention)
- **REQ-4**: A shared URL validation utility must be used by all agents — validation logic must not be duplicated per agent

## Acceptance Criteria

- [ ] Fetching `http://localhost/` from an agent raises a validation error
- [ ] Fetching `http://169.254.169.254/latest/meta-data/` raises a validation error
- [ ] Fetching `http://10.0.0.1/` raises a validation error
- [ ] Valid external URLs (`https://example.com`) pass validation

## Definition of Done

**Tests Required:**
- [ ] Unit tests: each blocked IP range and scheme triggers rejection
- [ ] Unit test: valid external URL passes
- [ ] DNS rebinding test: hostname resolving to private IP is rejected

**Documentation Required:**
- [ ] SSRF prevention strategy documented
- [ ] URL validation utility API documented

**Code Review Gate:**
- [ ] Reviewer confirms all agents use the shared URL validation utility
- [ ] Reviewer confirms DNS rebinding prevention is implemented

## Notes

This is a new gap — not a supersession of any EPIC-001 story. The SSRF vulnerability was identified during the audit but was not covered by the original EPIC-001 scope. It has no dependency on the auth migration itself but is included in EPIC-020 because it is a CRITICAL security finding that should ship alongside the auth hardening work. No reason to leave this door open while locking the others.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
