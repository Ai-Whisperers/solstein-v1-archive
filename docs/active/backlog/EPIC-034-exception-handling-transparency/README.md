# EPIC-034: Exception Handling Transparency

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Created** | 2026-03-01 |
| **Owner** | Platform Engineering |
| **Dependencies** | EPIC-014 (Observability Infrastructure), EPIC-021 (LLM Stack Reliability) |

---

## Executive Summary

A forensic audit of the Solstein codebase identified **20+ locations** where exceptions are silently caught and `None` is returned with no logging, no metrics, and no alerting. The platform presents a healthy exterior while internally discarding errors wholesale. This epic exists to make failures visible — because a system that hides its failures is not reliable; it is merely optimistic.

---

## Audit Findings

The audit found three distinct failure modes, each more insidious than the last:

### 1. The Black Hole Client (`enhanced_client.py:296`)
The enhanced LLM client wraps its entire execution in a catch-all handler that returns `None` on **any** exception. Network timeout? `None`. Bad API key? `None`. Malformed response? `None`. The caller cannot distinguish a successful empty response from a catastrophic authentication failure. Every LLM call is a coin flip with no feedback mechanism.

### 2. The Silent Research Pipeline
The research pipeline — `data/fetchers.py`, `research/signals.py`, `research/gather.py`, `research/evidence.py` — contains **12+ exception handlers** that return `None` without logging. An adapter fails, the pipeline continues, and the analyst receives a report with missing data and no indication that anything went wrong. The system logs a successful run. The data is simply absent.

### 3. The Math Errors Masquerading as Data Gaps
The scoring algorithms divide by revenue and employee count without zero-checks. When a pre-revenue startup has `revenue = 0`, the division raises `ZeroDivisionError`. This is caught somewhere up the stack, converted to `None`, and surfaced as a missing score. The analyst assumes the company wasn't analyzed. In reality, the analysis crashed on arithmetic.

---

## Scope

| Story | Title | Priority | Severity |
|-------|-------|----------|----------|
| [STORY-129](STORIES/STORY-129-enhanced-client-silent-failures.md) | Eliminate Silent None Returns in enhanced_client.py | P1 | Critical |
| [STORY-130](STORIES/STORY-130-adapter-exception-logging.md) | Add Structured Logging to All Adapter Exception Handlers | P1 | Critical |
| [STORY-131](STORIES/STORY-131-null-safety-division.md) | Add Null Safety Guards for Division Operations | P1 | High |
| [STORY-132](STORIES/STORY-132-exception-standards-doc.md) | Create Exception Handling Standards Document | P2 | Medium |

---

## Problem Statement

The platform was built with a philosophy of "never crash" that was implemented as "never surface errors." These are not the same thing. A system that never crashes because it silently discards all failures is not resilient — it is deceptive. Operators cannot monitor what they cannot see. Developers cannot debug what is not logged. Analysts cannot trust data whose provenance is unknown.

The consequence is a platform that appears healthy in monitoring dashboards while producing incomplete, potentially incorrect output. Silent failures are the worst kind of failure: they are invisible until a business decision is made on corrupted data.

This epic does not ask for perfect error handling. It asks for **honest** error handling: log what fails, surface what is missing, and give operators the information they need to understand system health.

---

## Impact Assessment

| Dimension | Current State | Target State |
|-----------|--------------|--------------|
| **Reliability** | Failures invisible; no circuit breaking | Failures logged, metered, and circuit-broken |
| **Observability** | Logs show success on failure | Structured error logs with full context |
| **Data Quality** | Missing data indistinguishable from absent data | Missing data flagged with reason codes |
| **Debuggability** | No diagnostic information on failure | Full context: adapter, company, endpoint, error type |
| **Trust** | Platform appears healthy while failing | Platform accurately represents its own health |
| **Onboarding** | New developers guess at error patterns | Standards document with decision tree |

---

## Dependencies

### Upstream (Must Exist Before This Epic)
- **EPIC-014 (Observability Infrastructure)**: Structured logging pipeline, metrics collection, and alerting infrastructure must be in place before error logs and metrics can be emitted meaningfully. If EPIC-014 is not complete, STORY-129 and STORY-130 should still add logging — but the logs will not be aggregated or alerted on until EPIC-014 delivers.
- **EPIC-021 (LLM Stack Reliability)**: The LLM provider abstraction layer must be stable before STORY-129 can implement circuit breakers and provider-specific error classification.

### Downstream (Blocked By This Epic)
- Any epic that depends on accurate pipeline health metrics
- Any epic that adds new data adapters (must follow standards from STORY-132)
- EPIC-035 (Retry and Backoff Strategy) — cannot implement intelligent retry without first knowing what errors are occurring

---

## Delivery Order

Stories should be delivered in this sequence to maximize early value:

1. **STORY-132** (Standards Document) — Define the target state before implementing it. Prevents rework.
2. **STORY-129** (enhanced_client.py) — Highest-impact single file. LLM failures are the most expensive silent failures.
3. **STORY-130** (Adapter Logging) — Broadest coverage. Touches the most files.
4. **STORY-131** (Division Safety) — Narrowest scope. Targeted math fixes.

---

## Definition of Done (Epic Level)

- [ ] All 4 stories completed and merged
- [ ] Zero bare `except:` clauses in codebase (verified by linting rule)
- [ ] All exception handlers log with structured context
- [ ] Metrics emitted for LLM errors (at minimum)
- [ ] Standards document committed and linked from AGENTS.md
- [ ] Code review checklist updated to include exception handling section
- [ ] Monitoring dashboard shows error rates (requires EPIC-014)

---

## Notes

The 20+ silent failure locations identified in the audit represent the **known** failures. The actual count is likely higher — the audit was not exhaustive. Any new adapters or LLM integrations added before this epic is complete should be held to the standards defined in STORY-132, even if the document is not yet formally published.

The cynical read: the platform was built to never show errors because errors are embarrassing. The professional read: the platform needs to show errors because errors are information. This epic is the transition from the former to the latter.
