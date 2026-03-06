from solstein.core.canary_rollout import canary_decision


def test_canary_decision_is_deterministic_for_same_subject() -> None:
    first = canary_decision("company-123", 30)
    second = canary_decision("company-123", 30)

    assert first.bucket == second.bucket
    assert first.enabled == second.enabled


def test_canary_decision_bounds_percent() -> None:
    low = canary_decision("subject", -10)
    high = canary_decision("subject", 500)

    assert low.rollout_percent == 0
    assert low.enabled is False

    assert high.rollout_percent == 100
    assert high.enabled is True


def test_canary_decision_changes_with_rollout_percent() -> None:
    subject = "stable-subject"
    off = canary_decision(subject, 0)
    on = canary_decision(subject, 100)

    assert off.enabled is False
    assert on.enabled is True
