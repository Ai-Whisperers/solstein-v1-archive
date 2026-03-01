# STORY-XXX: [Story Title]

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open / 🟡 In Progress / 🟠 In Review / 🟢 Done / ⚫ Archived |
| **Priority** | P0 (Ship Blocker) / P1 (Current Sprint) / P2 (Next Quarter) / P3 (Sustaining) |
| **Size** | S (1-2 days) / M (3-5 days) / L (1-2 weeks) / XL (3+ weeks) |
| **Epic** | [EPIC-XXX: Epic Title](../EPIC-XXX-epic-name/README.md) |
| **Created** | YYYY-MM-DD |
| **Risk** | Low / Medium / High |
| **Assigned** | @username |

---

## Audit Verdict

> [Specific, quotable evidence from the codebase. Include file paths, line numbers, and verbatim code snippets. This is the smoking gun that proves the problem exists.]

Example:
> `src/solstein/api/routers/auth.py` lines 57–60 contain the comment `# Demo: Accept any credentials` followed by code that constructs and returns a valid JWT for any username/password pair with zero verification.

---

## Problem Statement

[Clear, concise description of what is broken and why it matters. One paragraph maximum.]

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Security** | [If applicable: data exposure, auth bypass, etc.] |
| **Performance** | [If applicable: timeouts, resource exhaustion, etc.] |
| **Reliability** | [If applicable: crashes, data loss, inconsistency] |
| **Maintainability** | [If applicable: tech debt, developer velocity] |
| **Compliance** | [If applicable: regulatory violations] |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/path/to/file.py` | Modify / Delete / Create | [Specific function, class, or line range] |
| `tests/unit/test_file.py` | Modify / Create | [What tests need to change] |
| `docs/architecture.md` | Modify | [What documentation needs updating] |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- [STORY-XXX](link) — [Why this blocks this story]

### Soft Dependencies (Preferred Order)
- [STORY-XXX](link) — [Why this should happen first]

### Supersedes (If Applicable)
- [STORY-XXX](link) — [Why this story replaces the old one]

---

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: [Specific, testable requirement]
- **REQ-2**: [Specific, testable requirement]
- **REQ-3**: [Specific, testable requirement]

---

## Acceptance Criteria

- [ ] [Specific, verifiable outcome 1]
- [ ] [Specific, verifiable outcome 2]
- [ ] [Specific, verifiable outcome 3]
- [ ] [Command to verify: e.g., `grep -r "pattern" src/` returns zero results]

---

## Definition of Done

### Tests Required
- [ ] Unit test: [specific scenario]
- [ ] Integration test: [specific scenario]
- [ ] Boundary test: [edge case]
- [ ] Load test: [if applicable]

### Documentation Required
- [ ] Inline code comments explaining [what]
- [ ] Architecture Decision Record (ADR) if this changes significant design
- [ ] API documentation update
- [ ] Developer guide update

### Code Review Gate
- [ ] Reviewer confirms [specific criterion]
- [ ] Reviewer confirms [specific criterion]
- [ ] No `type: ignore` or `as Any` suppressions added
- [ ] All new code has type hints

### Operations/Deployment
- [ ] Database migration script (if applicable)
- [ ] Feature flag configured (if applicable)
- [ ] Monitoring/alerting in place (if applicable)
- [ ] Rollback procedure documented (if high risk)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | Low/Medium/High | Low/Medium/High | [How we'll reduce risk] |

---

## Notes

[Any additional context, research links, or implementation hints that don't fit above.]

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | @username | Created |
| YYYY-MM-DD | @username | Updated status to 🟡 In Progress |
