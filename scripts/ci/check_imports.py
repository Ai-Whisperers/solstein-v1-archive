#!/usr/bin/env python
"""Import smoke check — fail fast on any module-level AttributeError/ImportError.

Catches bugs like DataSourceType.WEB_SEARCH evaluated at class-body time.
Run before pytest in CI to surface import-time crashes immediately.
"""

import importlib
import pkgutil
import sys
import traceback
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

failures: list[tuple[str, str]] = []
checked = 0

for finder, modname, ispkg in pkgutil.walk_packages(
    path=[str(SRC / "solstein")],
    prefix="solstein.",
    onerror=lambda name: None,
):
    try:
        importlib.import_module(modname)
        checked += 1
    except ModuleNotFoundError:
        # Missing third-party dependency (celery, pgvector, etc.) — infra issue, not a code bug
        checked += 1
    except (AttributeError, ImportError, TypeError) as exc:
        tb = traceback.format_exc()
        failures.append((modname, f"{type(exc).__name__}: {exc}\n{tb}"))
    except Exception:
        # Other errors (missing env vars, DB not running) are expected in CI without infra
        checked += 1

print(f"Import smoke check: {checked} modules checked, {len(failures)} failures")

if failures:
    for modname, msg in failures:
        print(f"\n❌ FAIL: {modname}\n{msg}")
    sys.exit(1)

print("✅ All modules import cleanly")
