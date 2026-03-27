"""Competitor data loader.

Extracted from loaders.py as part of EPIC-021 file splitting.
Main loader class for loading competitor data from JSON files.
"""

from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

from solstein.config import get_settings
from solstein.data.converters import convert_to_domain_company
from solstein.domain.models import Company

logger = logging.getLogger(__name__)


# TODO: STORY-171 — remove in next cleanup sprint
# The CLI no longer imports CompetitorDataLoader (replaced by _load_companies_for_report).
# This class is still used internally by UnifiedCompanyLoader as a JSON bootstrap step.
# Safe to remove once UnifiedCompanyLoader is refactored to read JSON directly.
class CompetitorDataLoader:
    """Load competitor data from JSON files and convert to domain entities.

    DEPRECATED: This loader is being consolidated. For new code, use UnifiedCompanyLoader
    from solstein.data.unified_loader which provides enriched data with conflict resolution.
    """

    def __init__(self, data_dir: Path | None = None):
        warnings.warn(
            "CompetitorDataLoader is deprecated. Use UnifiedCompanyLoader from "
            "solstein.data.unified_loader for enriched data with conflict resolution.",
            DeprecationWarning,
            stacklevel=2,
        )
        settings = get_settings()
        self.data_dir = data_dir or Path(settings.data.data_dir)
        self._cache: dict[str, list[Company]] = {}

    def load_companies(self, limit: int | None = None) -> list[Company]:
        """Load all companies from data directory."""
        cache_key = f"companies_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        companies = []

        # Try to load from the main competitor data JSON
        json_path = self.data_dir / "competitor_data.json"

        if not json_path.exists():
            error_msg = f"Critical error: Competitor data not found at {json_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        companies.extend(self._load_from_json(json_path, limit))

        if limit:
            companies = companies[:limit]

        self._cache[cache_key] = companies
        return companies

    def load_from_json(self, json_path: Path, limit: int | None = None) -> list[Company]:
        """Load companies from scored JSON file (e.g., from pipeline output)."""
        return self._load_from_json(json_path, limit)

    def _load_from_json(self, json_path: Path, limit: int | None = None) -> list[Company]:
        """Load companies from JSON file."""
        try:
            with open(json_path) as f:
                data = json.load(f)

            competitors = data.get("competitors", [])
            if limit:
                competitors = competitors[:limit]

            companies = []
            for i, comp in enumerate(competitors):
                try:
                    company = convert_to_domain_company(comp, i)
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"Error converting competitor {i}: {e}")
                    continue

            logger.info(f"Loaded {len(companies)} companies from {json_path}")
            return companies

        except Exception as e:
            logger.error(f"Error loading JSON from {json_path}: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
        logger.debug("Cleared data cache")


# Global instance for easy import
loader = CompetitorDataLoader()
