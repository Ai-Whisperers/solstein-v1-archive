from solstein.core.rollback_profile import RollbackProfile, default_safe_rollback_profile


def test_default_safe_rollback_profile_disables_all_flags() -> None:
    profile = default_safe_rollback_profile()

    assert profile.feature_new_classifier is False
    assert profile.feature_new_readiness_gate is False
    assert profile.feature_new_unified_loader is False


def test_rollback_profile_env_overrides_are_deterministic() -> None:
    profile = RollbackProfile(
        feature_new_classifier=False,
        feature_new_readiness_gate=False,
        feature_new_unified_loader=False,
    )

    assert profile.as_env_overrides() == {
        "FEATURE_NEW_CLASSIFIER": "false",
        "FEATURE_NEW_READINESS_GATE": "false",
        "FEATURE_NEW_UNIFIED_LOADER": "false",
    }
