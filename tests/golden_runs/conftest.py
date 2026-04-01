"""Shared fixtures for golden contract run tests.

STORY-267 / EPIC-070
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


@pytest.fixture()
def artifacts_dir() -> Path:
    """Return the golden run artifacts directory."""
    return ARTIFACTS_DIR


def load_artifact(name: str) -> dict[str, Any]:
    """Load a golden artifact JSON file by name (without extension)."""
    path = ARTIFACTS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Golden artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
