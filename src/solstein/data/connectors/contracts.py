from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

PayloadT = TypeVar("PayloadT")


@dataclass(frozen=True)
class ConnectorRequest:
    connector: str
    operation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    requested_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class ConnectorResponse(Generic[PayloadT]):
    status: str
    connector: str
    operation: str
    payload: PayloadT | None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    completed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @staticmethod
    def success(
        request: ConnectorRequest,
        payload: PayloadT,
        metadata: dict[str, Any] | None = None,
    ) -> "ConnectorResponse[PayloadT]":
        return ConnectorResponse(
            status="success",
            connector=request.connector,
            operation=request.operation,
            payload=payload,
            metadata=metadata or {},
        )

    @staticmethod
    def degraded(
        request: ConnectorRequest,
        payload: PayloadT | None,
        error: str,
        metadata: dict[str, Any] | None = None,
    ) -> "ConnectorResponse[PayloadT]":
        return ConnectorResponse(
            status="degraded",
            connector=request.connector,
            operation=request.operation,
            payload=payload,
            error=error,
            metadata=metadata or {},
        )

    @staticmethod
    def failure(
        request: ConnectorRequest,
        error: str,
        metadata: dict[str, Any] | None = None,
    ) -> "ConnectorResponse[PayloadT]":
        return ConnectorResponse(
            status="failure",
            connector=request.connector,
            operation=request.operation,
            payload=None,
            error=error,
            metadata=metadata or {},
        )
