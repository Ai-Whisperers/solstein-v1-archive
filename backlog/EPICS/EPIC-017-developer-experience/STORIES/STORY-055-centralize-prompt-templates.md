# STORY-055: Centralize All LLM Prompt Templates into a Managed Registry

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-017: Developer Experience](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> LLM prompt templates are embedded as inline strings throughout `llm/enhanced_client.py` and multiple agent files. Prompt engineering requires knowing which file, which function, and which string variable contains the relevant prompt. Version control of prompt changes is impossible — a prompt edit looks identical to a code edit in git history.

## Problem Statement
Inline prompt strings in Python files make prompt management indistinguishable from code management. Prompts cannot be A/B tested, versioned independently, or reviewed by non-engineers. A prompt regression requires a code deployment to fix. Finding the prompt responsible for a bad output requires navigating Python files, reading function bodies, and identifying which multi-line string is the template — a task that should be as simple as opening a named file.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Finding and editing prompts requires code navigation skills — prompt engineering is gatekept by Python proficiency |
| **Quality** | Prompt changes cannot be reviewed without understanding the surrounding Python code — non-engineer reviewers are excluded |
| **Versioning** | Prompt history is buried in git blame alongside code changes — isolating prompt evolution from code evolution is impossible |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/enhanced_client.py` | Modify | Extract all inline prompt strings |
| All agent files with inline prompts | Modify | Extract all inline prompt strings |
| `src/solstein/llm/prompts/` | Add | New directory: centralized prompt registry |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: All LLM prompt templates must be extracted to a dedicated `src/solstein/llm/prompts/` module structure
- **REQ-2**: Each prompt must be a named, versioned entity with a descriptive identifier (e.g., `COMPANY_ANALYSIS_V2`, not `prompt1`)
- **REQ-3**: Prompt templates must support variable interpolation for dynamic content without using Python f-strings inline at call sites
- **REQ-4**: The prompt registry must be the single source of truth — no prompt strings may remain inline in agent or client files
- **REQ-5**: Prompts must be loadable and testable independently of the LLM client — importing a prompt must not require importing the HTTP client

## Acceptance Criteria
- [ ] No multi-line string prompt templates appear in `enhanced_client.py` or agent files
- [ ] All prompts are accessible via a named import from the prompts module
- [ ] A prompt can be loaded and inspected without importing the LLM client
- [ ] Each prompt has a descriptive name that communicates its purpose

## Definition of Done

**Tests Required:**
- [ ] Unit test: each prompt loads correctly and is a non-empty string
- [ ] Unit test: prompt variable interpolation produces expected output for known inputs
- [ ] Grep: no multi-line string templates in non-prompts modules

**Documentation Required:**
- [ ] Prompt authoring guide: how to add, modify, and version prompts

**Code Review Gate:**
- [ ] Reviewer confirms no inline prompt strings remain in non-prompts modules
- [ ] Reviewer confirms each prompt has a descriptive name and is independently importable

## Notes
This story has no dependencies and can be started immediately. It is a prerequisite for STORY-056 (LLM evaluation harness), which needs independently loadable prompts to test against. The extraction is mechanical but requires careful attention — prompts that use f-string interpolation with local variables need to be converted to a template format that accepts those variables as parameters. The prompts module should be flat initially (one file per prompt or one file per prompt category) — avoid over-engineering the registry before the evaluation harness reveals what structure is actually needed.

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
