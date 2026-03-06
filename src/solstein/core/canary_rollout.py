from __future__ import annotations

from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class CanaryDecision:
    subject_id: str
    rollout_percent: int
    bucket: int
    enabled: bool


def _bucket_for_subject(subject_id: str) -> int:
    digest = hashlib.sha256(subject_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def canary_decision(subject_id: str, rollout_percent: int) -> CanaryDecision:
    bounded = max(0, min(100, rollout_percent))
    bucket = _bucket_for_subject(subject_id)
    enabled = bucket < bounded
    return CanaryDecision(subject_id=subject_id, rollout_percent=bounded, bucket=bucket, enabled=enabled)
