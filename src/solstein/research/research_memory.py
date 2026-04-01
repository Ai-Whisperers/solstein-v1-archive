"""
Research memory persistence and management.

Extracted from AIResearchOrchestrator to reduce class size.
Handles loading, saving, and querying research memory state.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from loguru import logger


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison and deduplication."""
    try:
        parsed = urlparse(url.strip())
        if not parsed.scheme or not parsed.netloc:
            return url.strip()
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = parsed.path.rstrip("/") or "/"
        query_params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if not k.startswith("utm_")]
        query = urlencode(query_params)
        return urlunparse((scheme, netloc, path, "", query, ""))
    except (ValueError, AttributeError):
        return url.strip()


def company_key(company_name: str) -> str:
    """Normalize company name for memory lookup."""
    return " ".join(company_name.lower().split())


def extract_report_urls(report: dict[str, Any]) -> list[str]:
    """Extract and normalize URLs from a report's data_sources."""
    urls: set[str] = set()
    for source in report.get("data_sources", []):
        if not isinstance(source, dict):
            continue
        url = source.get("url")
        if isinstance(url, str) and url:
            urls.add(normalize_url(url))
    return sorted(urls)


def is_report_stale(report_dict: dict[str, Any], max_age_hours: int = 24 * 7) -> bool:
    """Check if a report is older than max_age_hours."""
    metadata = report_dict.get("metadata", {}) if isinstance(report_dict.get("metadata"), dict) else {}
    research_date = metadata.get("research_date")
    if not isinstance(research_date, str) or not research_date:
        return True
    try:
        ts = datetime.fromisoformat(research_date.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return True
    age_seconds = (datetime.now(ts.tzinfo) - ts).total_seconds()
    return age_seconds > (max_age_hours * 3600)


def score_completeness(payload: dict[str, Any], fields: list[str]) -> float:
    """Score what fraction of fields are non-empty."""
    if not fields:
        return 0.0
    filled = sum(1 for f in fields if payload.get(f) not in (None, "", [], {}))
    return filled / len(fields)


def flatten_report_fields(report_dict: dict[str, Any]) -> dict[str, Any]:
    """Flatten a report's nested sections into a single dict."""
    basic = report_dict.get("basic_info", {}) if isinstance(report_dict.get("basic_info"), dict) else {}
    financials = report_dict.get("financials", {}) if isinstance(report_dict.get("financials"), dict) else {}
    funding = report_dict.get("funding", {}) if isinstance(report_dict.get("funding"), dict) else {}
    merged: dict[str, Any] = {}
    merged.update(basic)
    merged.update(financials)
    merged.update(funding)
    return merged


class ResearchMemoryStore:
    """Manages research memory persistence.

    Wraps the JSON-based memory file with load/save/query operations.
    """

    def __init__(self, memory_path: Path, bootstrap_path: Path | None = None) -> None:
        self.memory_path = memory_path
        self.bootstrap_path = bootstrap_path
        self._data: dict[str, Any] = self._load()

    @property
    def data(self) -> dict[str, Any]:
        """Raw memory data."""
        return self._data

    def _load(self) -> dict[str, Any]:
        """Load memory from disk, or bootstrap from results."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception as error:  # noqa: BLE001
                logger.warning(f"Failed loading research memory from {self.memory_path}: {error}")

        if self.bootstrap_path:
            bootstrapped = self._bootstrap(self.bootstrap_path)
            if bootstrapped is not None:
                return bootstrapped

        return {"companies": {}}

    @staticmethod
    def _bootstrap(bootstrap_path: Path) -> dict[str, Any] | None:
        """Bootstrap memory from research_results.json."""
        if not bootstrap_path.exists():
            return None
        try:
            with open(bootstrap_path) as f:
                bootstrap = json.load(f)
        except Exception as error:  # noqa: BLE001
            logger.warning(f"Failed bootstrapping research memory from {bootstrap_path}: {error}")
            return None

        companies_list = bootstrap.get("companies", []) if isinstance(bootstrap, dict) else []
        if not isinstance(companies_list, list):
            return None

        memory: dict[str, Any] = {"companies": {}}
        for report in companies_list:
            if not isinstance(report, dict):
                continue
            name = report.get("company_name")
            if not isinstance(name, str) or not name.strip():
                continue
            key = company_key(name)
            urls = extract_report_urls(report)
            memory["companies"][key] = {
                "latest_report": report,
                "known_urls": urls,
                "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            }
        return memory

    def save(self) -> None:
        """Persist memory to disk."""
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception as error:  # noqa: BLE001
            logger.warning(f"Failed saving research memory to {self.memory_path}: {error}")

    def get_company(self, name: str) -> dict[str, Any]:
        """Get a company's memory entry."""
        key = company_key(name)
        return self._data.get("companies", {}).get(key, {})

    def get_previous_report(self, name: str) -> dict[str, Any] | None:
        """Get the most recent report for a company."""
        entry = self.get_company(name)
        report = entry.get("latest_report")
        return report if isinstance(report, dict) else None

    def get_known_urls(self, name: str) -> set[str]:
        """Get known URLs for a company."""
        entry = self.get_company(name)
        urls = entry.get("known_urls", [])
        if isinstance(urls, list):
            return {normalize_url(u) for u in urls if isinstance(u, str) and u}
        return set()

    def update_company(self, name: str, report: dict[str, Any], urls: set[str]) -> None:
        """Update a company's memory entry."""
        key = company_key(name)
        companies = self._data.setdefault("companies", {})
        existing_urls = set(companies.get(key, {}).get("known_urls", []))
        all_urls = existing_urls | {normalize_url(u) for u in urls if isinstance(u, str)}
        companies[key] = {
            "latest_report": report,
            "known_urls": sorted(all_urls),
            "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        }
