# STORY-127: Deduplicate profit_margin and employee Fields

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

---

## The Audit Verdict

> "`profit_margin` exists in BOTH `FinancialMetric` AND `Company` top-level. `employees` (`FinancialMetric`) vs `employee_count` (`Company`) — no synchronization."

---

## Problem Statement

The same data lives in two places. When `profit_margin` is updated in `FinancialMetric` but not in `Company`, the Excel export — which pulls from both — shows different values for the same metric. This isn't just duplication; it's a consistency hazard. The platform has no single source of truth for basic financial metrics. The fix is to pick one canonical location and derive the other, or eliminate the duplication entirely.

The naming inconsistency compounds the problem. `employees` in `FinancialMetric` and `employee_count` in `Company` are almost certainly the same concept, but the different names make it non-obvious that they should be synchronized. A developer updating headcount data has no clear signal about which field to write to. The result is that some code paths update one, some update the other, and the two values drift apart silently. The export then picks whichever it happens to encounter first, which may or may not be the more recently updated value.

This is a data model design failure that has been deferred long enough to become a data integrity problem. Every day this duplication exists is another day that `profit_margin` in the export might be stale, wrong, or inconsistent with what the platform's analytics layer computed. For a platform whose value proposition is accurate competitive intelligence, having the wrong profit margin in the analyst's deliverable is not a minor bug — it is a credibility failure.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | The same metric can simultaneously hold two different values; the export may surface either one |
| **Reliability** | Updates to financial data must touch two places; partial updates create inconsistency without error |
| **Maintainability** | Developers have no clear signal about which field is authoritative; write paths are ambiguous |
| **Analytics Correctness** | Analytics computations that read from one location may produce results inconsistent with exports reading from the other |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/domain/models.py` | `profit_margin` and `employee_count` defined at `Company` top-level, duplicating `FinancialMetric` fields |
| `src/solstein/infrastructure/database_models.py` | Duplicated columns in database schema; no foreign key or constraint enforcing consistency |
| `src/solstein/exporters/excel.py` | Export pulls from both models without a defined canonical source; behavior is undefined when values differ |

---

## Architectural Requirements

### Canonical Source Designation

- `FinancialMetric` is designated as the single source of truth for all financial metrics, including `profit_margin` and employee headcount
- This designation must be documented in the domain model as a comment or docstring, not just in this story
- No other model may hold a writable copy of a field that is canonical in `FinancialMetric`

### Company Model Refactoring

- `Company.profit_margin` must become a read-only computed property that delegates to the associated `FinancialMetric`
- `Company.employee_count` must become a read-only computed property that delegates to the associated `FinancialMetric`
- The property must handle the case where no `FinancialMetric` is associated (return `None`, not raise an exception)
- The property must be clearly marked as derived/computed in the model definition to prevent future developers from treating it as a writable field
- Direct assignment to `Company.profit_margin` or `Company.employee_count` must raise an `AttributeError` or be prevented by the property setter

### Write Path Consolidation

- All code paths that write financial metrics must write exclusively to `FinancialMetric`
- Any existing code that writes directly to `Company.profit_margin` or `Company.employee_count` must be identified and redirected to `FinancialMetric`
- A codebase-wide audit of write paths must be performed and documented as part of this story's implementation

### Database Migration

- The duplicated columns in the database schema (`Company.profit_margin`, `Company.employee_count`) must be addressed
- Preferred approach: mark columns as deprecated in the schema, migrate existing data to `FinancialMetric`, then remove columns in a subsequent migration
- If immediate removal is not feasible due to migration risk, columns must be marked with a deprecation comment and a migration ticket created
- The migration must include a data reconciliation step: for each company, compare the value in `Company` with the value in `FinancialMetric` and log any discrepancies before overwriting

### Data Reconciliation

- Before any data migration, a reconciliation report must be generated showing all companies where `Company.profit_margin` differs from `FinancialMetric.profit_margin`
- The same reconciliation must be performed for employee count fields
- The reconciliation report must be reviewed by a human before the migration proceeds
- Discrepancies must be resolved by a defined rule (e.g., "FinancialMetric value takes precedence if more recently updated; otherwise flag for manual review")

### Export Update

- The export must be updated to pull `profit_margin` and `employee_count` exclusively from `FinancialMetric` via the canonical `Company` property
- No direct access to the deprecated `Company`-level columns in the export layer

---

## Acceptance Criteria

- [ ] `Company.profit_margin` is a read-only property that reads from the associated `FinancialMetric`
- [ ] `Company.employee_count` is a read-only property that reads from the associated `FinancialMetric`
- [ ] Direct assignment to `Company.profit_margin` raises `AttributeError` (or is prevented by property design)
- [ ] Direct assignment to `Company.employee_count` raises `AttributeError` (or is prevented by property design)
- [ ] All write paths for financial metrics write to `FinancialMetric` only (verified by codebase audit)
- [ ] Database migration removes or deprecates duplicated columns
- [ ] Data reconciliation report generated and reviewed before migration executes
- [ ] Export pulls from canonical source only (no direct access to deprecated Company-level columns)
- [ ] `FinancialMetric` is documented as the canonical source of truth in the domain model
- [ ] No existing tests broken by the refactoring (property interface is backward-compatible for reads)

---

## Definition of Done

- **Tests Required**: Unit test asserting `Company.profit_margin` returns the value from its associated `FinancialMetric`. Unit test asserting that updating `FinancialMetric.profit_margin` is reflected in `Company.profit_margin` without a separate write. Negative test asserting direct assignment to `Company.profit_margin` fails. Data reconciliation report committed to `docs/migrations/` as evidence of review.
- **Documentation Required**: Domain model docstring updated to document `FinancialMetric` as canonical source. Migration notes committed to `docs/migrations/STORY-127-deduplication.md`.
- **Code Review Gate**: Reviewer runs `grep` for direct `profit_margin` assignment to `Company` model — result must be empty. Reviewer verifies no write paths bypass `FinancialMetric`.

---

## Notes

**On the naming inconsistency (`employees` vs. `employee_count`):** The canonical field name in `FinancialMetric` should be standardized as part of this story. The recommended canonical name is `employee_count` for consistency with the `Company` property name. If `FinancialMetric.employees` is renamed to `FinancialMetric.employee_count`, all references must be updated and a database migration must rename the column. This is a breaking change and must be coordinated with any consumers of the `FinancialMetric` model.

**On the reconciliation-before-migration requirement:** This is non-negotiable. The platform has been running with two unsynchronized copies of these fields for an unknown period. The magnitude of divergence is unknown. Migrating without first understanding the discrepancies risks silently overwriting correct data with stale data. The reconciliation report is the evidence that the migration is safe to proceed.

**On the "mark deprecated vs. remove" decision:** Immediate column removal is cleaner but carries migration risk. If the team has a policy of two-phase migrations (deprecate, then remove in a subsequent release), that policy should be followed. The story is complete when the columns are either removed or formally deprecated with a tracked removal ticket. Leaving them in place without any deprecation marker is not acceptable.

**Delivery note:** This story must be completed before STORY-125 (Restore 20 Dropped Fields). The export rebuilt in STORY-125 must pull from the canonical source established here. Building the export on top of the duplicated fields would require rework when this story is eventually completed.
