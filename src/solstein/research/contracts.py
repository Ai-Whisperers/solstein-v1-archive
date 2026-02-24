import hashlib
import json
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, Field

StageName = Literal[
    "discovery",
    "gather",
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


def build_config_hash(config: Mapping[str, object]) -> str:
    encoded = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_stage_artifact(
    *,
    stage: StageName,
    artifact_schema_version: str,
    model_version: str,
    prompt_version: str,
    config_hash: str,
    payload: Mapping[str, object] | None = None,
    status: str | None = None,
    description: str | None = None,
) -> dict[str, object]:
    response = StageResponseEnvelope(
        stage=stage,
        payload=dict(payload or {}),
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
