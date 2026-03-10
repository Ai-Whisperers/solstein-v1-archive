from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

from solstein.domain.models import Company


@dataclass(frozen=True)
class AdjudicationDecision:
    decision_id: str
    metric: str
    decision: str
    status: str
    actor: str
    reason: str
    value: Any = None
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "decision_id": self.decision_id,
            "metric": self.metric,
            "decision": self.decision,
            "status": self.status,
            "actor": self.actor,
            "reason": self.reason,
            "timestamp": self.timestamp or datetime.now(UTC).isoformat(),
        }
        if self.value is not None:
            payload["value"] = self.value
        return payload


def _decision_key(metric: str) -> str:
    return f"adjudication:{metric.lower().strip()}"


def _encode_decision_payload(payload: Mapping[str, Any]) -> str:
    serialized: list[str] = []
    for key, value in payload.items():
        if value is None:
            continue
        serialized.append(f"{key}={value}")
    return ";".join(serialized)


def _decode_decision_payload(raw: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for token in raw.split(";"):
        token = token.strip()
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def record_adjudication_decision(company: Company, decision: AdjudicationDecision) -> None:
    company.metric_justifications[_decision_key(decision.metric)] = _encode_decision_payload(decision.to_dict())


def get_adjudication_decision(company: Company, metric: str) -> dict[str, Any] | None:
    raw = company.metric_justifications.get(_decision_key(metric))
    if not raw:
        return None
    if not isinstance(raw, str):
        return None
    payload = _decode_decision_payload(raw)
    return payload or None


def list_adjudication_decisions(company: Company) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, value in company.metric_justifications.items():
        if not key.startswith("adjudication:"):
            continue
        if not isinstance(value, str):
            continue
        metric = key.split(":", 1)[1]
        parsed = _decode_decision_payload(value)
        if parsed:
            out[metric] = parsed
    return out
