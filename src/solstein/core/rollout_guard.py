from dataclasses import dataclass


@dataclass(frozen=True)
class RolloutMetrics:
    gate_fail_ratio: float
    confidence_drift: float
    export_error_ratio: float


@dataclass(frozen=True)
class RolloutThresholds:
    max_gate_fail_ratio: float = 0.15
    max_confidence_drift: float = 0.2
    max_export_error_ratio: float = 0.05


@dataclass(frozen=True)
class RolloutDecision:
    should_rollback: bool
    reasons: list[str]


def evaluate_rollout(metrics: RolloutMetrics, thresholds: RolloutThresholds | None = None) -> RolloutDecision:
    active = thresholds or RolloutThresholds()
    reasons: list[str] = []

    if metrics.gate_fail_ratio > active.max_gate_fail_ratio:
        reasons.append(
            f"gate_fail_ratio {metrics.gate_fail_ratio:.3f} > {active.max_gate_fail_ratio:.3f}"
        )
    if metrics.confidence_drift > active.max_confidence_drift:
        reasons.append(
            f"confidence_drift {metrics.confidence_drift:.3f} > {active.max_confidence_drift:.3f}"
        )
    if metrics.export_error_ratio > active.max_export_error_ratio:
        reasons.append(
            f"export_error_ratio {metrics.export_error_ratio:.3f} > {active.max_export_error_ratio:.3f}"
        )

    return RolloutDecision(should_rollback=bool(reasons), reasons=reasons)
