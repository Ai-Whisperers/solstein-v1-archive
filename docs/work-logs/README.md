# Work Logs

Automated session logs from the Hermes Agent autonomous pipeline.

Each file documents one cron job session:
- What stories were worked on
- Metrics before/after (tests, lint, files)
- Changes made and why
- PRs created
- Blockers found
- What the next shift should focus on

## Naming Convention
```
YYYY-MM-DD-HHMM.md          — Development shift log
YYYY-MM-DD-HHMM-tests.md    — Test engineering shift log
YYYY-MM-DD-HHMM-audit.md    — Weekly audit log
```

## Usage
Read the latest log to see what was done most recently:
```bash
ls -t docs/work-logs/*.md | head -1 | xargs cat
```
