# Release Readiness Checklist

Use this checklist before delivering client reports. All steps are executable and map to automated artifacts.

## Preconditions

- `PYTHONPATH=src` set
- Database available (or use sqlite override when running in isolation)

## Steps

1) Generate refresh status snapshot

```bash
PYTHONPATH=src python scripts/export_refresh_status.py
```

Expected:
- `data/output/refresh/refresh_status.json` exists
- `overall_stale` is `false` for production delivery

2) Verify enrichment audit trail exists

```bash
ls -la data/output/enrichment_audit.jsonl
```

Expected:
- File exists and includes `paid_escalation` entries when escalation occurs

3) Verify release gate audit trail exists

```bash
ls -la data/output/release_gate_audit.jsonl
```

Expected:
- File exists and includes `passed` or `blocked` entries

4) Generate report (gate enforced)

```bash
PYTHONPATH=src solstein generate_report --input data/input/competitor_data_real.json --company "Target Company"
```

Expected:
- If gate passes, report is generated
- If gate fails, `REPORT_NOT_READY` reasons are surfaced

## Failure Handling

- `overall_stale: true` → run refresh job before release
- `gap_analysis` / `completeness` / `synthetic_data` → resolve data gaps before release
