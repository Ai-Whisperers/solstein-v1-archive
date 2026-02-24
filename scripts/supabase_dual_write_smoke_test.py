from __future__ import annotations

import os
from pathlib import Path

from solstein.research.pipeline import run_market_intelligence


def main() -> int:
    db_url = os.getenv("SUPABASE__DB_URL", "").strip()
    if not db_url:
        raise SystemExit(
            "Missing SUPABASE__DB_URL. Set it to your Supabase Postgres connection URL."
        )

    out_dir = Path(os.getenv("OUTPUT_DIR", "data/output/runs/supabase"))
    run_market_intelligence(
        seed_company=os.getenv("SEED_COMPANY", "ueno"),
        market=os.getenv("MARKET", "LATAM Financial Services"),
        output_dir=out_dir,
        max_companies=int(os.getenv("MAX_COMPANIES", "25")),
        extra_keywords=[
            k for k in os.getenv("EXTRA_KEYWORDS", "bank,fintech").split(",") if k
        ],
        strict_provenance=os.getenv("STRICT_PROVENANCE", "false").lower() == "true",
        db_dual_write=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
