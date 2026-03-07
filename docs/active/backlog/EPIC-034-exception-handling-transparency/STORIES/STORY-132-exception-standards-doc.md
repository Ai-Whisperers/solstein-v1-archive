# STORY-132: Create Exception Handling Standards Document

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

---

## The Audit Verdict

> No standards exist for exception handling. Each developer implements ad-hoc patterns.

---

## Problem Statement

The codebase has at least 15 distinct exception handling patterns. Some log, some don't. Some return `None`, some raise. Some catch specific exceptions, some catch `Exception`, some use bare `except:`. Some retry, some don't. Some use `WARNING`, some use `ERROR`, some use nothing. The inconsistency is not random — it reflects the absence of any agreed-upon standard. Each developer who touched an exception handler made a local decision in isolation, and those decisions accumulated into a codebase where the same error in different adapters produces different outcomes.

This inconsistency has operational consequences. An operator monitoring the platform cannot build reliable alerting rules when the same class of error is logged at `WARNING` in one adapter and silently swallowed in another. A developer debugging a production issue cannot predict where to look for error information when the logging behavior varies by file. A new team member writing a new adapter has no reference for how to handle exceptions — they look at existing code, find three different patterns, and pick one at random. The pattern they pick is probably one of the bad ones, because the bad ones are more numerous.

The fix is not to retroactively audit every exception handler in the codebase — that is the work of STORY-129 and STORY-130. The fix is to define the standard that those stories implement, and that all future code must follow. A standards document that lives in `docs/standards/` and is referenced from `AGENTS.md` and the code review checklist is the mechanism by which the current chaos becomes the historical baseline and the future codebase becomes consistent.

The document must be prescriptive, not aspirational. It must tell developers exactly what to do in each situation, not describe general principles and leave the application as an exercise. It must include a decision tree that can be followed mechanically. It must include concrete examples of correct and incorrect patterns. And it must be enforced — by linting rules that catch the most common violations, and by a code review checklist that makes exception handling a mandatory review item.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 15+ inconsistent patterns make the codebase unpredictable; every exception handler requires individual inspection to understand its behavior |
| **Reliability** | Inconsistent patterns produce inconsistent outcomes; the same error class produces different results depending on which adapter handles it |
| **Onboarding** | New developers have no reference for exception handling; they learn by reading existing code, which teaches bad patterns |
| **Code Review** | Reviewers have no standard to enforce; exception handling quality depends entirely on individual reviewer knowledge and attention |
| **Operational** | Inconsistent logging levels and formats make alerting rules unreliable and log queries unpredictable |

---

## Affected Files

| File | Issue |
|------|-------|
| `docs/standards/exception-handling.md` | Does not exist; must be created |
| `docs/standards/` | Directory may not exist; must be created if absent |
| `.ruff.toml` or `pyproject.toml` | Linting rules for exception handling not configured |
| `docs/code-review-checklist.md` | Exception handling section absent; must be added |
| `AGENTS.md` | No reference to exception handling standards; link must be added |

---

## Architectural Requirements

- The standards document must be committed to `docs/standards/exception-handling.md` and must be the single authoritative reference for exception handling decisions in the Solstein codebase
- The document must include a decision tree that answers the following questions in sequence: Should this exception be caught here or propagated? If caught, should it be logged? At what level? Should the function return a value, raise a different exception, or return a structured error result? Should the operation be retried?
- The decision tree must cover at minimum the following exception categories: external API errors (HTTP 4xx, HTTP 5xx), network/timeout errors, authentication/authorization errors, rate limit errors, data parsing/validation errors, and unexpected/unknown errors
- The document must include a "patterns" section with named patterns and explicit guidance on when each applies: the Propagate pattern (re-raise after logging), the Structured Result pattern (return typed error result), the Default Value pattern (return safe default with logging), and the Circuit Breaker pattern (signal failure to circuit breaker before returning)
- The document must include a "bad patterns" section with explicit examples of what is prohibited and why: bare `except:`, `except Exception` without logging, returning `None` without logging, swallowing exceptions in constructors
- The document must specify the required fields for every structured log entry emitted from an exception handler: `error_type`, `error_message`, `component` (module/class), `operation` (function name), `context` (relevant identifiers such as company_id, adapter_name), and `trace_id` where available
- The document must specify log level conventions: `DEBUG` for expected, handled conditions; `WARNING` for transient errors that may self-resolve; `ERROR` for persistent errors requiring intervention; `CRITICAL` for errors that compromise data integrity or system availability
- Linting rules must be configured to enforce at minimum: no bare `except:` clauses (ruff `E722`), no broad `except Exception` without a comment explaining why it is necessary
- The code review checklist must include an "Exception Handling" section with specific questions reviewers must answer for every PR that modifies exception handlers
- The document must be referenced from `AGENTS.md` in the "Code Standards" section so that it is visible to all developers (and AI assistants) working in the codebase
- The document must include an "Adapter-Specific Guidelines" section covering the specific patterns for: external HTTP API adapters, file system operations, database operations, LLM client calls, and data parsing operations

---

## Acceptance Criteria

- [ ] `docs/standards/exception-handling.md` exists and is committed to the repository
- [ ] The document includes a decision tree covering all five exception categories (API errors, network errors, auth errors, rate limit errors, parse errors, unknown errors)
- [ ] The document defines at least four named patterns (Propagate, Structured Result, Default Value, Circuit Breaker) with guidance on when each applies
- [ ] The document includes a "bad patterns" section with at least three prohibited patterns and explanations
- [ ] The document specifies required log fields for exception handler log entries
- [ ] The document specifies log level conventions for all severity categories
- [ ] Linting rule for bare `except:` (ruff `E722`) is enabled and enforced in CI
- [ ] `docs/code-review-checklist.md` includes an "Exception Handling" section with at least five reviewer questions
- [ ] `AGENTS.md` references `docs/standards/exception-handling.md` in the Code Standards section
- [ ] The document includes adapter-specific guidelines for at least three adapter types (HTTP API, LLM client, data parsing)
- [ ] A new developer unfamiliar with the codebase can read the document and correctly implement exception handling for a new adapter without additional guidance

---

## Definition of Done

- **Tests Required**: No automated tests for the document itself. However, the linting rules added as part of this story must be verified: run `ruff check` against the existing codebase and confirm that `E722` violations are flagged. The linting rule is the automated enforcement mechanism.
- **Documentation Required**: The standards document is itself the deliverable. Additionally, a brief summary of the standards must be added to `AGENTS.md` (not the full document — a link and a one-paragraph summary). The code review checklist update is a required deliverable.
- **Code Review Gate**: Reviewer verifies the decision tree is complete and unambiguous — a developer following it mechanically should reach a clear decision for each exception category. Reviewer verifies the bad patterns section covers the specific violations found in the audit (bare `except:`, `None` returns without logging). Reviewer verifies the linting rule is active in CI configuration.

---

## Notes

This story is listed as P2 but should be delivered **first** among the four stories in EPIC-034. The standards document defines the target state that STORY-129, STORY-130, and STORY-131 implement. Implementing those stories before the standards are defined risks inconsistent patterns across the implementations — which is the problem this epic is trying to solve.

The decision tree is the most important artifact in the document. It must be genuinely useful, not decorative. A decision tree that requires judgment calls at every node is not a decision tree; it is a list of considerations. The target is a tree that a developer can follow mechanically and arrive at a correct implementation decision.

The linting rules are the enforcement mechanism. A standards document without enforcement is a suggestion. The minimum viable enforcement is `E722` (bare `except:`). Additional rules — such as requiring logging in exception handlers — may require custom ruff plugins or pre-commit hooks, which are out of scope for this story but should be noted as future work.

The "new developer test" in the acceptance criteria is intentionally subjective. It should be validated by having a team member who did not write the document attempt to implement exception handling for a hypothetical new adapter using only the document as a reference. If they get it wrong, the document needs revision.

The document should acknowledge that not every exception handling decision is mechanical. There are genuinely ambiguous cases. The document should identify those cases explicitly and provide guidance on how to resolve ambiguity (e.g., "when in doubt, log and propagate rather than swallow").
