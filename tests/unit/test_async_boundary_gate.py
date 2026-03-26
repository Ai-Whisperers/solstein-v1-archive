"""Tests for the async-boundary static gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "ci" / "check_async_boundaries.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("check_async_boundaries", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_gate_flags_direct_sync_patent_lookup_in_async(tmp_path: Path) -> None:
    gate = _load_gate_module()
    sample = tmp_path / "sample.py"
    sample.write_text(
        """
async def fetch_facts():
    result = search_company_patents("acme")
    return result
"""
    )

    findings = gate.scan_file(sample)

    assert len(findings) == 1
    assert findings[0].rule == "search_company_patents"


def test_gate_allows_sync_patent_lookup_when_offloaded(tmp_path: Path) -> None:
    gate = _load_gate_module()
    sample = tmp_path / "sample.py"
    sample.write_text(
        """
import asyncio

async def fetch_facts():
    result = await asyncio.to_thread(search_company_patents, "acme")
    return result
"""
    )

    findings = gate.scan_file(sample)

    assert findings == []


def test_gate_flags_unawaited_async_detector_call(tmp_path: Path) -> None:
    gate = _load_gate_module()
    sample = tmp_path / "sample.py"
    sample.write_text(
        """
async def fetch_facts(detector):
    funding = detector.detect_funding_signal("acme")
    return funding
"""
    )

    findings = gate.scan_file(sample)

    assert len(findings) == 1
    assert findings[0].rule == "detect_funding_signal"


def test_gate_allows_detector_call_inside_awaited_gather(tmp_path: Path) -> None:
    gate = _load_gate_module()
    sample = tmp_path / "sample.py"
    sample.write_text(
        """
import asyncio

async def fetch_facts(detector):
    funding, partnership = await asyncio.gather(
        detector.detect_funding_signal("acme"),
        detector.detect_partnership_signal("acme"),
    )
    return funding, partnership
"""
    )

    findings = gate.scan_file(sample)

    assert findings == []
