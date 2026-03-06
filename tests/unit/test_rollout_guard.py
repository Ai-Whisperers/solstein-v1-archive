from solstein.core.rollout_guard import RolloutMetrics, RolloutThresholds, evaluate_rollout


def test_rollout_guard_no_rollback_within_thresholds() -> None:
    metrics = RolloutMetrics(gate_fail_ratio=0.05, confidence_drift=0.08, export_error_ratio=0.01)

    decision = evaluate_rollout(metrics)

    assert decision.should_rollback is False
    assert decision.reasons == []


def test_rollout_guard_rolls_back_when_any_metric_exceeds_threshold() -> None:
    metrics = RolloutMetrics(gate_fail_ratio=0.20, confidence_drift=0.04, export_error_ratio=0.01)

    decision = evaluate_rollout(metrics)

    assert decision.should_rollback is True
    assert any("gate_fail_ratio" in reason for reason in decision.reasons)


def test_rollout_guard_rolls_back_with_multiple_reasons() -> None:
    metrics = RolloutMetrics(gate_fail_ratio=0.20, confidence_drift=0.25, export_error_ratio=0.10)
    thresholds = RolloutThresholds(max_gate_fail_ratio=0.10, max_confidence_drift=0.15, max_export_error_ratio=0.03)

    decision = evaluate_rollout(metrics, thresholds)

    assert decision.should_rollback is True
    assert len(decision.reasons) == 3
    assert any("gate_fail_ratio" in reason for reason in decision.reasons)
    assert any("confidence_drift" in reason for reason in decision.reasons)
    assert any("export_error_ratio" in reason for reason in decision.reasons)
