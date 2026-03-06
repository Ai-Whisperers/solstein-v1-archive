from dataclasses import dataclass

from solstein.config import Settings, get_settings


@dataclass(frozen=True)
class FeatureFlags:
    new_classifier: bool
    new_readiness_gate: bool
    new_unified_loader: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> "FeatureFlags":
        return cls(
            new_classifier=settings.feature_new_classifier,
            new_readiness_gate=settings.feature_new_readiness_gate,
            new_unified_loader=settings.feature_new_unified_loader,
        )


def get_feature_flags(settings: Settings | None = None) -> FeatureFlags:
    resolved_settings = settings or get_settings()
    return FeatureFlags.from_settings(resolved_settings)
