import hashlib
import json
from collections.abc import Mapping
from enum import Enum
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

StageName = Literal[
    "discovery",
    "gather",
    "per_company_source_gate",
    "provenance_validation",
    "contradiction_detection",
    "evidence_readiness",
    "scoring",
    "analysis",
    "export",
    "persist",
    "source_volume_gate",
]


class StageRequestEnvelope(BaseModel):
    stage: StageName
    payload: dict[str, object] = Field(default_factory=dict)
    artifact_schema_version: str
    model_version: str
    prompt_version: str
    config_hash: str


class StageResponseEnvelope(BaseModel):
    stage: StageName
    payload: dict[str, object] = Field(default_factory=dict)
    artifact_schema_version: str
    model_version: str
    prompt_version: str
    config_hash: str
    status: str | None = None
    description: str | None = None


class RunState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


_RUN_STATE_TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.CREATED: {RunState.RUNNING, RunState.CANCELLED},
    RunState.RUNNING: {RunState.PAUSED, RunState.FAILED, RunState.COMPLETED, RunState.CANCELLED},
    RunState.PAUSED: {RunState.RUNNING, RunState.CANCELLED},
    RunState.FAILED: set(),
    RunState.COMPLETED: set(),
    RunState.CANCELLED: set(),
}


class RunStateTransitionError(ValueError):
    pass


class PipelineRunState(BaseModel):
    run_id: str
    state: RunState = RunState.CREATED
    current_stage: StageName | None = None
    reason: str | None = None

    def transition_to(self, next_state: RunState, reason: str | None = None) -> None:
        allowed = _RUN_STATE_TRANSITIONS[self.state]
        if next_state not in allowed:
            raise RunStateTransitionError(f"Invalid run-state transition: {self.state.value} -> {next_state.value}")
        self.state = next_state
        if reason is not None:
            self.reason = reason


def build_config_hash(config: Mapping[str, object]) -> str:
    encoded = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_stage_artifact(
    stage: StageName,
    envelope: object | None = None,
    payload: object | None = None,
    **legacy_meta: object,
) -> dict[str, object]:
    status = cast("str | None", legacy_meta.pop("status", None))
    description = cast("str | None", legacy_meta.pop("description", None))

    envelope_map = cast("Mapping[str, Any]", envelope or {})
    resolved_envelope = dict(envelope_map)
    if not resolved_envelope:
        resolved_envelope = {
            "artifact_schema_version": legacy_meta.get("artifact_schema_version", "1.0.0"),
            "model_version": legacy_meta.get("model_version", "research.v2"),
            "prompt_version": legacy_meta.get("prompt_version", "research.pipeline.v2"),
            "config_hash": legacy_meta.get("config_hash", ""),
        }

    artifact_schema_version = str(resolved_envelope.get("artifact_schema_version", "1.0.0"))
    model_version = str(resolved_envelope.get("model_version", "research.v2"))
    prompt_version = str(resolved_envelope.get("prompt_version", "research.pipeline.v2"))
    config_hash = str(resolved_envelope.get("config_hash", ""))
    response = StageResponseEnvelope(
        stage=stage,
        payload=dict(cast("Mapping[str, Any]", payload or {})),
        artifact_schema_version=artifact_schema_version,
        model_version=model_version,
        prompt_version=prompt_version,
        config_hash=config_hash,
        status=status,
        description=description,
    )
    artifact: dict[str, object] = {
        "stage": response.stage,
        "artifact_schema_version": response.artifact_schema_version,
        "model_version": response.model_version,
        "prompt_version": response.prompt_version,
        "config_hash": response.config_hash,
    }
    if response.status is not None:
        artifact["status"] = response.status
    if response.description is not None:
        artifact["description"] = response.description
    artifact.update(response.payload)
    return artifact
