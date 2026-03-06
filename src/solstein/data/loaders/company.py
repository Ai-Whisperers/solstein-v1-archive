"""Unified company model with data source tracking.

Extracted from unified_loader.py as part of EPIC-021 file splitting.
"""

from __future__ import annotations

from datetime import datetime, timezone

from solstein.domain.models import Company


class UnifiedCompany(Company):
    """Extended Company model with data source tracking and merge conflict documentation."""

    data_source_per_field: dict[str, str] = {}  # Track where each field came from
    merge_conflicts: list[str] = []  # Fields where JSON and Markdown differed
    merge_priority: str = "Markdown > JSON"  # Document priority rules
    merge_timestamp: datetime | None = None
