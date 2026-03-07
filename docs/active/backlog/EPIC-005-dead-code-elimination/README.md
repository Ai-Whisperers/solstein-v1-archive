# EPIC-005: Dead Code Elimination

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-015, STORY-016, STORY-017, STORY-018 |
| Created | 2026-02-28 |

---

## Summary

Dead code is a tax on every future developer. Every engineer who reads `worker_tasks_v2.py` will spend time understanding whether it is the canonical file or the legacy one. Every engineer who encounters `UsageTracker` will wonder why LLM costs aren't being tracked — and then discover the class is never called. Every engineer who sees seven agent classes with real-sounding names will assume they work.

This epic eliminates dead code that actively misleads developers and, in the case of the stub agents, may be injecting fabricated data into client deliverables.

## Scope

### Worker Task File Duplication
`worker_tasks.py` and `worker_tasks_v2.py` coexist in the codebase with overlapping task definitions. No documentation explains which is canonical. Celery workers configured to load one will silently miss tasks defined only in the other. This is not a naming problem — it is a reliability problem.

### Orphaned UsageTracker Class
`llm/enhanced_client.py` lines 591–661 define a 70-line `UsageTracker` class that is never imported, never instantiated, never called. It was built with methods for recording token counts, cost estimates, and provider-level usage statistics. It tracks nothing. Meanwhile, the business has no visibility into LLM API spend.

### Stub Agent Classes
`agents/additional_agents.py` lines 45–268 contain 7 stub agent classes: `LinkedInAgent`, `SECEdgarAgent`, `PatentsAgent`, `NewsSignalAgent`, `JobsAgent`, `TechTrendsAgent`, and `WebsiteAgent`. Each returns hardcoded mock data strings. None contact real external systems. If these agents are registered in the production agent coordinator, they are returning fabricated competitive intelligence to clients.

### Dead Temporal Workflow Stubs
`analytics/workflows.py` and `analytics/activities.py` contain Temporal workflow and activity definitions that reference a localhost Temporal server (`localhost:7233` hardcoded in `api/routers/jobs.py`). These stubs were apparently built for a Temporal-based workflow orchestration approach that was abandoned. They exist only as dead imports and cognitive overhead.

## Stories

| Story | Title | Priority | Severity |
|-------|-------|----------|----------|
| [STORY-015](STORIES/STORY-015-consolidate-worker-tasks.md) | Consolidate Competing Worker Task Files | P1 | HIGH |
| [STORY-016](STORIES/STORY-016-wire-or-delete-usage-tracker.md) | Wire or Delete the UsageTracker Class | P1 | MEDIUM |
| [STORY-017](STORIES/STORY-017-implement-or-remove-stub-agents.md) | Implement or Permanently Remove Stub Agents | P1 | HIGH |
| [STORY-018](STORIES/STORY-018-remove-temporal-workflow-stubs.md) | Remove Dead Temporal Workflow Stubs | P1 | LOW |

## Definition of Done

- [ ] One worker tasks file exists — the other is deleted, not renamed
- [ ] `UsageTracker` is either wired into every LLM call and producing observable usage data, or entirely absent from the codebase
- [ ] Zero stub agents exist in the production agent registry that return hardcoded data
- [ ] Temporal workflow stubs are deleted and an ADR documents the decision
- [ ] `grep -r "localhost:7233"` returns zero results
- [ ] All existing tests pass after cleanup

## Ordering Notes

Stories in this epic are independent and can be executed in parallel. STORY-017 (stub agents) is the highest-risk item due to the possibility of fabricated data in client deliverables — it should be prioritised for investigation even if full implementation of replacement agents is deferred.
