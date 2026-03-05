import json
from datetime import datetime, timezone
from pathlib import Path

from auto_enrich_real_data import main as run_auto_enrichment


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _company_index(data: dict) -> dict[str, dict]:
    companies = data.get("competitors", []) if isinstance(data, dict) else []
    index: dict[str, dict] = {}
    for c in companies:
        name = c.get("company_name") or c.get("name")
        if isinstance(name, str) and name:
            index[name] = c
    return index


def _metric_snapshot(company: dict) -> dict[str, object]:
    return {
        "revenue": company.get("revenue"),
        "employees": company.get("employees"),
        "growth_rate": company.get("growth_rate"),
        "profit_margin": company.get("profit_margin"),
        "funding_raised": company.get("funding_raised"),
        "valuation": company.get("valuation"),
        "ticker": company.get("ticker"),
        "company_number": company.get("company_number"),
    }


def _build_delta(previous: dict, current: dict) -> dict:
    prev_index = _company_index(previous)
    curr_index = _company_index(current)

    added = sorted([name for name in curr_index if name not in prev_index])
    removed = sorted([name for name in prev_index if name not in curr_index])
    changed = []

    for name in sorted(set(prev_index.keys()) & set(curr_index.keys())):
        before = _metric_snapshot(prev_index[name])
        after = _metric_snapshot(curr_index[name])
        if before != after:
            field_changes = {}
            for key in before:
                if before[key] != after[key]:
                    field_changes[key] = {"before": before[key], "after": after[key]}
            changed.append({"company": name, "changes": field_changes})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "added_companies": added,
        "removed_companies": removed,
        "changed_companies": changed,
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "total_current": len(curr_index),
        },
    }


def main() -> None:
    enriched_path = Path("data/input/competitor_data_real_enriched.json")
    previous_snapshot_path = Path("data/output/refresh/previous_enriched_snapshot.json")
    delta_path = Path("data/output/refresh/delta_report.json")

    previous_data = _load_json(enriched_path)
    previous_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    previous_snapshot_path.write_text(json.dumps(previous_data, indent=2))

    run_auto_enrichment()

    current_data = _load_json(enriched_path)
    delta = _build_delta(previous_data, current_data)
    delta_path.write_text(json.dumps(delta, indent=2))

    print(f"✅ Refresh cycle complete: {enriched_path}")
    print(f"✅ Delta report written: {delta_path}")
    print(f"Summary: {delta['summary']}")


if __name__ == "__main__":
    main()
