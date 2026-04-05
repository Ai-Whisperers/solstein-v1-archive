# Agent Bootstrap — Mandatory Session Start

## Read These First

Every session — autonomous or interactive — must read these two files before any code work:

1. `.hermes.md` — full protocol, prohibited actions, verified codebase facts, regression floor
2. `backlog/EXECUTION_ORDER.md` — 95 stories in priority order

## Story Selection Rule

**The only valid way to choose what to work on:**
→ Open `backlog/EXECUTION_ORDER.md`
→ Find the first row with `Status = READY`
→ Work that story

Do not pick from GitHub issues, epic READMEs, git log, or intuition.

## After Each Story

Update `backlog/EXECUTION_ORDER.md` — change the Status from READY to DONE in the same
commit as the implementation. Check if any BLOCKED rows below it are now unblocked.

## Regression Floor

3800 passing tests minimum. If your change drops below this, revert before pushing.
