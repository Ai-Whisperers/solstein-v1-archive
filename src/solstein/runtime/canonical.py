"""Canonical runtime facade for the legacy pipeline.

STORY-257 / EPIC-067
---------------------
This module is the **single shared entry-point** that all canonical
pipeline participants (CLI, API, scripts) MUST use for:

1. Building the ``SourceRegistry`` (discovery + enrichment adapters).
2. Converting raw JSON dicts into ``Company`` domain objects.
3. Running the full market-intelligence pipeline.

If you are adding a new CLI command, API endpoint, or script that
discovers, enriches, or scores companies, import from
``solstein.runtime`` -- never call ``build_default_registry`` or
``convert_to_domain_company`` directly.

Non-canonical paths
~~~~~~~~~~~~~~~~~~~
The following surfaces are **not** part of the canonical runtime and
do NOT need to import from here:

* ``research/graph/`` -- frozen graph runtime (security patches only).
* ``cli_ai_research.py`` -- standalone AI research orchestrator.
* ``cli_research.py`` -- standalone real-data loader.
* ``data/unified_loader.py`` -- merger/enrichment surface (separate
  enrichment path; will converge with registry in future work).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from solstein.adapters.registry import SourceRegistry, build_default_registry
from solstein.config import Settings
from solstein.data.converters import convert_to_domain_company
from solstein.domain.models import Company

if TYPE_CHECKING:
    from pathlib import Path


def get_registry(settings: Settings | None = None) -> SourceRegistry:
    """Build the canonical ``SourceRegistry``.

    Parameters
    ----------
    settings:
        Optional pre-loaded settings.  When *None* (the default)
        ``Settings.load()`` is called automatically.

    Returns
    -------
    SourceRegistry
        A registry populated with all adapters that the current
        configuration enables (API-key gated sources are only
        registered when their key is present).
    """
    if settings is None:
        settings = Settings.load()
    registry = build_default_registry(settings)
    logger.debug(
        "Canonical registry built: {} discovery + {} enrichment sources",
        len(registry.discovery_sources),
        len(registry.enrichment_sources),
    )
    return registry


def convert_raw(raw: dict[str, Any], index: int = 0) -> Company:
    """Convert a raw JSON dict into a ``Company`` domain object.

    This is a thin wrapper around the canonical
    ``convert_to_domain_company`` so that all call-sites import from
    one place and any future migration to a new converter is a
    single-file change.
    """
    return convert_to_domain_company(raw, index)


def run_pipeline(
    seed_company: str,
    market: str,
    output_dir: Path,
    options: dict[str, object] | None = None,
    **legacy_kwargs: object,
) -> dict[str, object]:
    """Run the canonical market-intelligence pipeline.

    Delegates to ``research.pipeline.run_market_intelligence`` which
    internally calls ``get_registry()`` and orchestrates the full
    discover -> gather -> score -> export flow.

    Parameters
    ----------
    seed_company:
        Name or identifier of the seed company.
    market:
        Market / industry label.
    output_dir:
        Directory for pipeline artifacts.
    options:
        Pipeline configuration overrides.
    **legacy_kwargs:
        Backward-compatible keyword arguments forwarded to the
        pipeline.
    """
    from solstein.research.pipeline import run_market_intelligence

    return run_market_intelligence(
        seed_company=seed_company,
        market=market,
        output_dir=output_dir,
        options=options,
        **legacy_kwargs,
    )
