import json
import subprocess
import sys
from pathlib import Path
from typing import cast


def _run_detector(src_path: Path) -> dict[str, object]:
    script = Path("scripts/ci/detect_dead_code.py")
    proc = subprocess.run(
        [sys.executable, str(script), str(src_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def test_detect_dead_code_flags_disconnected_refresh_router(tmp_path: Path) -> None:
    src = tmp_path / "src" / "solstein"
    routes_dir = src / "api" / "routes"
    routes_dir.mkdir(parents=True)
    (routes_dir / "refresh.py").write_text("def ping():\n    return True\n", encoding="utf-8")

    api_dir = src / "api"
    api_dir.mkdir(exist_ok=True)
    (api_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

    output = _run_detector(src)
    checks = cast("dict[str, bool]", output["structural_checks"])

    assert checks["refresh_router_exists"] is True
    assert checks["refresh_router_connected"] is False


def test_detect_dead_code_flags_worker_tasks_v2_file(tmp_path: Path) -> None:
    src = tmp_path / "src" / "solstein"
    src.mkdir(parents=True)
    (src / "worker_tasks_v2.py").write_text("def orphan_task():\n    return 1\n", encoding="utf-8")

    output = _run_detector(src)
    checks = cast("dict[str, bool]", output["structural_checks"])

    assert checks["worker_tasks_v2_exists"] is True
