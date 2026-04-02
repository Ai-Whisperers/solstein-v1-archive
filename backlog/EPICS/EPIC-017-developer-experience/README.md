# EPIC-017: Developer Experience

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 4 |
| Created | 2026-02-28 |
| Depends On | [EPIC-013](../EPIC-013-test-suite-integrity/README.md) (test suite fixed first) |

## Context

Setting up Solstein for local development currently requires archaeological knowledge. The configuration requirements are not documented in one place. The test suite has a hidden autouse fixture that silently changes behaviour. LLM prompt templates are embedded inline throughout `llm/enhanced_client.py`, making prompt engineering an exercise in grepping. There is no LLM output evaluation — prompts are changed by feel.

This is not just inconvenience. Poor developer experience increases the cost of every future change, lengthens onboarding time, and drives senior engineers to avoid the codebase. Fixing this is an investment in the velocity of everything else in this backlog.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-055](STORIES/STORY-055-centralize-prompt-templates.md) | Centralize LLM Prompt Templates | MEDIUM |
| [STORY-056](STORIES/STORY-056-llm-evaluation-harness.md) | Build LLM Output Evaluation Harness | MEDIUM |
| [STORY-057](STORIES/STORY-057-automate-local-dev-setup.md) | Automate Local Development Setup | HIGH |
| [STORY-058](STORIES/STORY-058-developer-onboarding-docs.md) | Write Developer Onboarding Documentation | HIGH |

## Definition of Done

- [ ] All LLM prompts in one versioned location
- [ ] LLM evaluation harness exists with at least 5 test cases
- [ ] `make setup` brings up a working local environment from scratch
- [ ] Onboarding documentation gets a new engineer to first API response in under 30 minutes

## Autonomous Continuation Notes

### Queue Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` before starting any story here.
- `planning/QUEUE.md` currently marks only `STORY-057` and `STORY-058` unfinished here.
- `STORY-057` is `BLOCKED` on `STORY-059`.
- `STORY-058` is `BLOCKED` on `STORY-039`.

### Next Agent Action

- Do not start implementation work in this epic until the blockers are actually resolved in `develop` and the queue is updated.
- Once unblocked, prefer `STORY-057` before `STORY-058` so onboarding docs describe the real setup path instead of a guessed one.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` for machine-checkable work.
- Avoid prose-only “helpful” setup content. Setup and onboarding docs must be derived from commands that actually run in this repo.
- Any developer-experience fix should add at least one durable guardrail: regression test, generated reference update, schema/type gate, or AST/check script.

### Minimum Verification For Future Agents

- If `STORY-057` is worked: prove the setup path with real commands and actual output.
- If `STORY-058` is worked: verify the documented onboarding path matches the current `Makefile`, `.venv`, and active dev commands instead of historical docs.
