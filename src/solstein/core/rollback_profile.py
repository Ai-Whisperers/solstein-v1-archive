"""Rollback profile for feature flag overrides.

STORY-256: ``feature_new_unified_loader`` is deprecated.  The legacy
enrichment path is canonical and the registry no longer branches on
this flag.  The field is retained so existing rollback tooling keeps
working.  Deletion trigger: EPIC-067 complete.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RollbackProfile:
    feature_new_classifier: bool = False
    feature_new_readiness_gate: bool = False
    # DEPRECATED (STORY-256): retained for rollback compat only.
    feature_new_unified_loader: bool = False

    def as_env_overrides(self) -> dict[str, str]:
        return {
            "FEATURE_NEW_CLASSIFIER": str(self.feature_new_classifier).lower(),
            "FEATURE_NEW_READINESS_GATE": str(self.feature_new_readiness_gate).lower(),
            # DEPRECATED (STORY-256): no longer consumed by registry.
            "FEATURE_NEW_UNIFIED_LOADER": str(self.feature_new_unified_loader).lower(),
        }


def default_safe_rollback_profile() -> RollbackProfile:
    return RollbackProfile()
