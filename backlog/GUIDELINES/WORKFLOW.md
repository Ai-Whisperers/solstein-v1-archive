# Story Status Workflow

> Clear states, clear transitions, clear ownership.

## Develop Autonomy Guard

- For active `develop` work, consult `planning/QUEUE.md` first.
- Then consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md`.
- A story or epic file showing `Open` or `Not Started` is not by itself authorization to begin work.
- If the queue does not currently schedule the item, treat it as triage-required backlog inventory until a planning pass reactivates it.

---

## Status Definitions

| Status | Icon | Definition | Owner |
|--------|------|------------|-------|
| **Open** | 🔴 | Story defined, not started | Product/Tech Lead |
| **In Progress** | 🟡 | Actively being worked on | Assignee |
| **In Review** | 🟠 | PR open, under review | Reviewer |
| **Done** | 🟢 | Merged, verified in staging | Tech Lead |
| **Archived** | ⚫ | Superseded or obsolete | Tech Lead |

---

## State Transitions

```
┌─────────┐     assign      ┌─────────────┐     PR open     ┌─────────────┐
│  Open   │ ───────────────→│ In Progress │ ──────────────→│ In Review   │
│   🔴    │                 │    🟡       │                │    🟠       │
└─────────┘                 └─────────────┘                └──────┬──────┘
     ↑                                                            │
     │         ┌──────────────────────────────────────────────────┘
     │         │  changes requested
     │    ┌────┴────┐
     │    │         │
     │    └────┬────┘
     │         │  approved
     │    ┌────┴────┐     merge      ┌─────────┐     verify     ┌─────────┐
     └────┤  Done   │←───────────────┤  Done   │───────────────→│Archived │
            🟢                         🟢                         ⚫
```

---

## Transition Rules

### 🔴 Open → 🟡 In Progress

**Trigger:** Engineer starts work

**Requirements:**
- [ ] Story has assignee
- [ ] Dependencies resolved
- [ ] Story size estimated
- [ ] Risk assessed

**Action:**
```bash
git checkout -b feature/STORY-XXX-short-description
# Update story file status to 🟡 In Progress
```

---

### 🟡 In Progress → 🟠 In Review

**Trigger:** PR opened

**Requirements:**
- [ ] All acceptance criteria met
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Self-review completed

**Action:**
```bash
gh pr create --title "STORY-XXX: Brief description" \
             --body "Closes STORY-XXX"
# Update story file status to 🟠 In Review
```

---

### 🟠 In Review → 🟡 In Progress (Changes Requested)

**Trigger:** Reviewer requests changes

**Requirements:**
- [ ] Review comments addressed
- [ ] Changes pushed
- [ ] Re-request review

**Action:**
```bash
# Make changes
git commit --amend --no-edit
git push --force-with-lease
# Status remains 🟠 In Review
```

---

### 🟠 In Review → 🟢 Done

**Trigger:** PR approved and merged

**Requirements:**
- [ ] All review comments resolved
- [ ] CI passing
- [ ] Merged to main
- [ ] Deployed to staging

**Action:**
```bash
gh pr merge --squash
# Update story file status to 🟢 Done
```

---

### 🟢 Done → ⚫ Archived

**Trigger:** Story superseded or obsolete

**Requirements:**
- [ ] Tech Lead approval
- [ ] Superseded by documented
- [ ] Code reverted if needed

**Action:**
```bash
# Move story file to archive/superseded/
git mv story.md archive/superseded/
# Update story file status to ⚫ Archived
```

---

## Responsibilities

### Assignee (Engineer)

- Update status when transitioning
- Ensure acceptance criteria met before review
- Respond to review comments within 24 hours
- Verify in staging before marking done

### Reviewer

- Review within 24 hours of PR open
- Provide specific, actionable feedback
- Approve only when confident in quality
- Verify tests cover edge cases

### Tech Lead

- Archive superseded stories
- Resolve status disputes
- Ensure workflow compliance
- Weekly review of in-progress stories

---

## WIP Limits

To prevent context switching and ensure flow:

| Role | Max In Progress |
|------|-----------------|
| Engineer | 2 stories |
| Team | 3 × number of engineers |

When WIP limit reached:
1. Complete current story before starting new
2. Help unblock teammates
3. Review open PRs

---

## Blocked Stories

If a story is blocked:

1. **Add blocker label:** `blocked`
2. **Document blocker:** In story notes section
3. **Set status:** Remains 🟡 In Progress
4. **Escalate:** If blocked >3 days, escalate to Tech Lead

```markdown
## Notes

**Blocked:** 2026-03-01
**Reason:** Waiting for EPIC-020 STORY-067 to complete (JWT middleware)
**Escalated:** @tech-lead
```

---

## Story Aging

Stories should not linger:

| Age | Action |
|-----|--------|
| < 3 days | Normal |
| 3-5 days | Check for blockers |
| 5-7 days | Daily standup discussion |
| > 7 days | Escalate to Tech Lead, consider splitting |

---

## Related

- [Story Template](../.backlog/templates/story.md) — Include status field
- [Estimation Framework](ESTIMATION.md) — Size affects WIP
- [Milestones](../MILESTONES/) — Status rollup to milestones
