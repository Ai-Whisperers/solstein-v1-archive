#!/usr/bin/env python3
"""Dry-run compatibility validator for Company/FinancialMetric model migration.

Exit code:
- 0: all compatibility scenarios pass
- 1: one or more scenarios fail
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from solstein.domain.models import Company


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    details: str


def _legacy_flat_payload() -> dict[str, Any]:
    return {
        "id": "legacy-1",
        "name": "LegacyCo",
        "industry": "Energy Software",
        "revenue": 12.5,
        "employees": 40,
        "growth_rate": 22.0,
        "profit_margin": 14.0,
        "funding": 3.2,
        "valuation": 55.0,
    }


def _nested_payload() -> dict[str, Any]:
    return {
        "id": "nested-1",
        "name": "NestedCo",
        "industry": "Energy Software",
        "financials": {
            "revenue": 18.0,
            "employees": 55,
            "growth_rate": 28.0,
            "profit_margin": 17.0,
            "funding_raised": 8.0,
            "valuation": 120.0,
        },
    }


def _mixed_payload() -> dict[str, Any]:
    return {
        "id": "mixed-1",
        "name": "MixedCo",
        "industry": "Energy Software",
        "revenue": 9.0,
        "employees": 25,
        "financials": {
            "revenue": 11.0,
            "employees": 30,
            "growth_rate": 19.0,
            "profit_margin": 9.0,
            "funding_raised": 2.0,
            "valuation": 42.0,
        },
    }


def _incompatible_payload() -> dict[str, Any]:
    return {
        "id": "bad-1",
        "name": "BadCo",
        "industry": "Energy Software",
        "revenue": "not-a-number",
        "employees": -3,
    }


def _validate_legacy_flat() -> ScenarioResult:
    name = "legacy_flat_roundtrip"
    try:
        company = Company.model_validate(_legacy_flat_payload())
        dumped = company.model_dump()
        if dumped["financials"]["revenue"] != 12.5:
            return ScenarioResult(name, False, "financials.revenue did not sync from flat payload")
        if dumped["financials"]["employees"] != 40:
            return ScenarioResult(name, False, "financials.employees did not sync from flat payload")
        return ScenarioResult(name, True, "legacy flat payload parsed and synced")
    except ValidationError as exc:
        return ScenarioResult(name, False, f"ValidationError: {exc}")


def _validate_nested() -> ScenarioResult:
    name = "nested_roundtrip"
    try:
        company = Company.model_validate(_nested_payload())
        dumped = company.model_dump()
        if dumped["financials"]["revenue"] != 18.0:
            return ScenarioResult(name, False, "nested revenue mismatch")
        if dumped["financials"]["funding_raised"] != 8.0:
            return ScenarioResult(name, False, "nested funding mismatch")
        return ScenarioResult(name, True, "nested payload parsed")
    except ValidationError as exc:
        return ScenarioResult(name, False, f"ValidationError: {exc}")


def _validate_mixed() -> ScenarioResult:
    name = "mixed_payload_determinism"
    try:
        company = Company.model_validate(_mixed_payload())
        dumped = company.model_dump()
        if dumped["financials"]["revenue"] != 11.0:
            return ScenarioResult(name, False, "mixed payload did not resolve deterministically")
        return ScenarioResult(name, True, "mixed payload resolved deterministically")
    except ValidationError as exc:
        return ScenarioResult(name, False, f"ValidationError: {exc}")


def _validate_incompatible() -> ScenarioResult:
    name = "incompatible_payload_failure"
    try:
        _ = Company.model_validate(_incompatible_payload())
        return ScenarioResult(name, False, "incompatible payload unexpectedly parsed")
    except ValidationError as exc:
        return ScenarioResult(name, True, f"expected failure: {exc.errors()[0].get('msg', 'validation error')}")


def run() -> int:
    checks = [
        _validate_legacy_flat(),
        _validate_nested(),
        _validate_mixed(),
        _validate_incompatible(),
    ]

    print("== Model Migration Dry-Run Validator ==")
    print(json.dumps([c.__dict__ for c in checks], indent=2))

    failed = [c for c in checks if not c.passed]
    if failed:
        print("\nResult: FAIL")
        for item in failed:
            print(f"- {item.name}: {item.details}")
        return 1

    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
