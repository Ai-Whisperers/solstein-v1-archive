from dataclasses import dataclass


@dataclass(frozen=True)
class RollbackProfile:
    feature_new_classifier: bool = False
    feature_new_readiness_gate: bool = False
    feature_new_unified_loader: bool = False

    def as_env_overrides(self) -> dict[str, str]:
        return {
            "FEATURE_NEW_CLASSIFIER": str(self.feature_new_classifier).lower(),
            "FEATURE_NEW_READINESS_GATE": str(self.feature_new_readiness_gate).lower(),
            "FEATURE_NEW_UNIFIED_LOADER": str(self.feature_new_unified_loader).lower(),
        }


def default_safe_rollback_profile() -> RollbackProfile:
    return RollbackProfile()
