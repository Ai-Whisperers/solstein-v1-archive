# STORY-254: Standardize Agent Handoff Artifact Bundle and Checkpoint Docs

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | Medium |

---

## Problem Statement

The dev log captures history, but there is not yet a concise, standard artifact bundle for handing work between sessions without reopening broad context.

### Audit Context — 2026-04-02

Recent workflow review found that agents can misread the repo if the handoff only says "check issues" or "review backlog" without naming which surface is authoritative. The handoff bundle must make the context contract explicit:

- `planning/QUEUE.md` decides what to work on next.
- `planning/generated/GITHUB_ISSUE_SNAPSHOT.{json,md}` gives a cached view of the current issue tracker for context only.
- Generated docs and audit indexes explain code reality and risk, but they do not replace the queue ordering.

## Acceptance Criteria

- [ ] A standard handoff artifact format exists for active work sessions.
- [ ] Handoff artifacts include current target, touched surfaces, verification results, unresolved risks, and links to generated indexes.
- [ ] The handoff format is short enough for practical reuse and enforced through templates or generators where reasonable.
- [ ] The format is linked from dev workflow docs.
- [ ] The handoff template has an explicit "execution authority" field that points to `planning/QUEUE.md`.
- [ ] The handoff template has an explicit "informational tracker snapshot" field that points to `planning/generated/GITHUB_ISSUE_SNAPSHOT.{json,md}` when available.

## Definition of Done

- [ ] Handoff template or generator committed
- [ ] Example artifact committed under a stable docs location
- [ ] Session workflow docs updated
