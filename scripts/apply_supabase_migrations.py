from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(
            f"Missing required environment variable: {name}. "
            "Set it to your Supabase Postgres connection URL."
        )
    return value


def main() -> int:
    db_url = _require_env("SUPABASE__DB_URL")
    migrations_dir = Path(__file__).resolve().parents[1] / "supabase" / "migrations"
    migrations = sorted(migrations_dir.glob("*.sql"))
    if not migrations:
        raise SystemExit(f"No migrations found in {migrations_dir}")

    for migration in migrations:
        subprocess.run(
            [
                "psql",
                db_url,
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(migration),
            ],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
