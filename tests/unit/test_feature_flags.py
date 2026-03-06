from _pytest.monkeypatch import MonkeyPatch

from solstein.config import Settings
from solstein.core.feature_flags import FeatureFlags, get_feature_flags


def test_feature_flags_default_values_are_false():
    settings = Settings()

    flags = get_feature_flags(settings)

    assert flags == FeatureFlags(
        new_classifier=False,
        new_readiness_gate=False,
        new_unified_loader=False,
    )


def test_feature_flags_read_environment_overrides(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("FEATURE_NEW_CLASSIFIER", "true")
    monkeypatch.setenv("FEATURE_NEW_READINESS_GATE", "1")
    monkeypatch.setenv("FEATURE_NEW_UNIFIED_LOADER", "yes")

    settings = Settings()
    flags = get_feature_flags(settings)

    assert flags.new_classifier is True
    assert flags.new_readiness_gate is True
    assert flags.new_unified_loader is True


def test_feature_flags_can_be_constructed_directly_from_settings(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("FEATURE_NEW_CLASSIFIER", "false")
    monkeypatch.setenv("FEATURE_NEW_READINESS_GATE", "true")
    monkeypatch.setenv("FEATURE_NEW_UNIFIED_LOADER", "false")

    settings = Settings()
    flags = FeatureFlags.from_settings(settings)

    assert flags.new_classifier is False
    assert flags.new_readiness_gate is True
    assert flags.new_unified_loader is False
