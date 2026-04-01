"""Feature flags for Solstein runtime behavior.

STORY-256: ``new_unified_loader`` is deprecated.  The legacy enrichment
path is canonical and the registry no longer branches on this flag.
The field is retained so existing config files keep loading without errors.
Deletion trigger: EPIC-067 complete.
"""

import warnings
from dataclasses import dataclass

from solstein.config import Settings, get_settings


@dataclass(frozen=True)
class FeatureFlags:
    new_classifier: bool
    new_readiness_gate: bool
    # DEPRECATED (STORY-256): retained for config compat only.
    new_unified_loader: bool = False

    @classmethod
    def from_settings(cls, settings: Settings) -> "FeatureFlags":
        if settings.feature_new_unified_loader:
            warnings.warn(
                "FEATURE_NEW_UNIFIED_LOADER is deprecated (STORY-256). "
                "The legacy enrichment path is now canonical. "
                "This flag is ignored by build_default_registry.",
                DeprecationWarning,
                stacklevel=2,
            )
        return cls(
            new_classifier=settings.feature_new_classifier,
            new_readiness_gate=settings.feature_new_readiness_gate,
            new_unified_loader=settings.feature_new_unified_loader,
        )


def get_feature_flags(settings: Settings | None = None) -> FeatureFlags:
    resolved_settings = settings or get_settings()
    return FeatureFlags.from_settings(resolved_settings)
