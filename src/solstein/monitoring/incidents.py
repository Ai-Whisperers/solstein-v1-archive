"""Automated incident response system.

EPIC-026 Story 7: Implements automated responses to common incidents:
- Restart stuck workers
- Scale up on high load
- LLM provider failover
- Runbook generation

Usage:
    from solstein.monitoring.incidents import IncidentManager, AutoRemediationRule

    manager = IncidentManager()
    manager.register_rule(AutoRemediationRule(
        name="restart_stuck_worker",
        condition="worker_heartbeat > 300",
        action=restart_worker
    ))
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class RemediationActionType(Enum):
    """Types of automated remediation actions."""

    RESTART_WORKER = "restart_worker"
    SCALE_UP = "scale_up"
    SWITCH_PROVIDER = "switch_provider"
    CLEAR_CACHE = "clear_cache"
    RESTART_SERVICE = "restart_service"
    NOTIFY = "notify"


class IncidentStatus(Enum):
    """Incident status."""

    DETECTED = "detected"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FAILED = "failed"
    IGNORED = "ignored"


@dataclass
class Incident:
    """Represents an incident."""

    id: str
    alert_name: str
    severity: str
    message: str
    status: IncidentStatus
    detected_at: datetime
    resolved_at: datetime | None = None
    actions_taken: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_name": self.alert_name,
            "severity": self.severity,
            "message": self.message,
            "status": self.status.value,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "actions_taken": self.actions_taken,
            "context": self.context,
        }


@dataclass
class AutoRemediationRule:
    """Rule for automated remediation."""

    name: str
    alert_pattern: str  # Regex to match alert names
    condition: str  # Expression to evaluate
    action_type: RemediationActionType
    action_params: dict[str, Any] = field(default_factory=dict)
    cooldown_minutes: int = 30
    max_attempts: int = 3
    enabled: bool = True


class RemediationAction:
    """Base class for remediation actions."""

    async def execute(self, incident: Incident, params: dict[str, Any]) -> bool:
        """Execute remediation action.

        Args:
            incident: Incident being remediated.
            params: Action parameters.

        Returns:
            True if successful.
        """
        raise NotImplementedError


class RestartWorkerAction(RemediationAction):
    """Restart stuck worker."""

    async def execute(self, incident: Incident, params: dict[str, Any]) -> bool:
        """Restart worker."""
        worker_id = params.get("worker_id", "unknown")
        logger.info(f"Restarting worker {worker_id}")

        # In production, this would call orchestration API
        # await kubernetes.restart_pod(worker_id)

        incident.actions_taken.append(
            {
                "action": "restart_worker",
                "worker_id": worker_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
            }
        )

        return True


class ScaleUpAction(RemediationAction):
    """Scale up service."""

    async def execute(self, incident: Incident, params: dict[str, Any]) -> bool:
        """Scale up."""
        service = params.get("service", "api")
        replicas = params.get("replicas", 2)
        max_replicas = params.get("max_replicas", 10)

        logger.info(f"Scaling up {service} by {replicas} replicas (max: {max_replicas})")

        # In production: await kubernetes.scale_deployment(service, replicas)

        incident.actions_taken.append(
            {
                "action": "scale_up",
                "service": service,
                "replicas": replicas,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
            }
        )

        return True


class SwitchProviderAction(RemediationAction):
    """Switch LLM provider."""

    async def execute(self, incident: Incident, params: dict[str, Any]) -> bool:
        """Switch provider."""
        from_provider = params.get("from_provider")
        to_provider = params.get("to_provider")

        logger.info(f"Switching LLM provider from {from_provider} to {to_provider}")

        # In production: Update configuration

        incident.actions_taken.append(
            {
                "action": "switch_provider",
                "from": from_provider,
                "to": to_provider,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
            }
        )

        return True


class IncidentManager:
    """Manage incidents and automated remediation."""

    def __init__(self):
        """Initialize incident manager."""
        self.incidents: dict[str, Incident] = {}
        self.rules: list[AutoRemediationRule] = []
        self.actions: dict[RemediationActionType, RemediationAction] = {
            RemediationActionType.RESTART_WORKER: RestartWorkerAction(),
            RemediationActionType.SCALE_UP: ScaleUpAction(),
            RemediationActionType.SWITCH_PROVIDER: SwitchProviderAction(),
        }
        self._last_action_time: dict[str, float] = {}

    def register_rule(self, rule: AutoRemediationRule):
        """Register a remediation rule.

        Args:
            rule: Rule to register.
        """
        self.rules.append(rule)
        logger.info(f"Registered remediation rule: {rule.name}")

    def create_incident(
        self,
        alert_name: str,
        severity: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> Incident:
        """Create new incident.

        Args:
            alert_name: Alert that triggered incident.
            severity: Incident severity.
            message: Incident description.
            context: Additional context.

        Returns:
            Created incident.
        """
        import hashlib
        import time

        incident_id = hashlib.md5(f"{alert_name}:{time.time()}".encode()).hexdigest()[:12]

        incident = Incident(
            id=incident_id,
            alert_name=alert_name,
            severity=severity,
            message=message,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.now(timezone.utc),
            context=context or {},
        )

        self.incidents[incident_id] = incident
        logger.warning(f"Incident created: {incident_id} - {alert_name}")

        return incident

    async def handle_alert(
        self,
        alert_name: str,
        severity: str,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> Incident | None:
        """Handle incoming alert.

        Args:
            alert_name: Alert name.
            severity: Alert severity.
            message: Alert message.
            context: Alert context.

        Returns:
            Incident if created and handled.
        """
        # Create incident
        incident = self.create_incident(alert_name, severity, message, context)

        # Find matching rules
        matching_rules = self._find_matching_rules(alert_name)

        if not matching_rules:
            logger.info(f"No remediation rules for alert: {alert_name}")
            incident.status = IncidentStatus.IGNORED
            return incident

        # Execute remediation
        incident.status = IncidentStatus.IN_PROGRESS

        for rule in matching_rules:
            if not rule.enabled:
                continue

            # Check cooldown
            if not self._check_cooldown(rule):
                logger.info(f"Rule {rule.name} in cooldown")
                continue

            # Execute action
            action = self.actions.get(rule.action_type)
            if action:
                try:
                    success = await action.execute(incident, rule.action_params)
                    if success:
                        self._last_action_time[rule.name] = asyncio.get_event_loop().time()
                        logger.info(f"Remediation executed: {rule.name}")
                except Exception as e:
                    logger.error(f"Remediation failed: {rule.name} - {e}")
                    incident.actions_taken.append(
                        {
                            "action": rule.name,
                            "error": str(e),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "status": "failed",
                        }
                    )

        return incident

    def _find_matching_rules(self, alert_name: str) -> list[AutoRemediationRule]:
        """Find rules matching alert.

        Args:
            alert_name: Alert name.

        Returns:
            Matching rules.
        """
        import re

        matching = []
        for rule in self.rules:
            if re.search(rule.alert_pattern, alert_name):
                matching.append(rule)

        return matching

    def _check_cooldown(self, rule: AutoRemediationRule) -> bool:
        """Check if rule is in cooldown.

        Args:
            rule: Rule to check.

        Returns:
            True if can execute.
        """
        import time

        last_action = self._last_action_time.get(rule.name, 0)
        cooldown_seconds = rule.cooldown_minutes * 60

        return time.time() - last_action > cooldown_seconds

    def resolve_incident(self, incident_id: str, resolution: str = ""):
        """Resolve an incident.

        Args:
            incident_id: Incident ID.
            resolution: Resolution notes.
        """
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.now(timezone.utc)
            logger.info(f"Incident resolved: {incident_id}")

    def get_active_incidents(self) -> list[Incident]:
        """Get active incidents.

        Returns:
            List of active incidents.
        """
        return [i for i in self.incidents.values() if i.status in (IncidentStatus.DETECTED, IncidentStatus.IN_PROGRESS)]

    def get_incident_stats(self) -> dict[str, Any]:
        """Get incident statistics.

        Returns:
            Statistics dictionary.
        """
        total = len(self.incidents)
        by_status = {}
        for i in self.incidents.values():
            status = i.status.value
            by_status[status] = by_status.get(status, 0) + 1

        auto_resolved = sum(
            1 for i in self.incidents.values() if i.status == IncidentStatus.RESOLVED and len(i.actions_taken) > 0
        )

        return {
            "total": total,
            "by_status": by_status,
            "active": len(self.get_active_incidents()),
            "auto_resolved": auto_resolved,
            "auto_resolution_rate": auto_resolved / max(total, 1),
        }


# Predefined runbooks
RUNBOOKS = {
    "database_connection_failed": """
# Database Connection Failed

## Symptoms
- `DatabaseConnectionFailed` alert firing
- API returning 500 errors
- Health check failing

## Resolution Steps
1. Check RDS status in AWS console
2. Verify security group rules
3. Check connection pool usage
4. If pool exhausted: Restart application
5. If RDS down: Failover to read replica

## Escalation
If not resolved in 15 minutes, escalate to: on-call DBA
""",
    "high_error_rate": """
# High Error Rate

## Symptoms
- Error rate > 10%
- Multiple 5xx responses
- Users reporting issues

## Resolution Steps
1. Check recent deployments
2. Review error logs for pattern
3. Check database health
4. Check external dependencies
5. Rollback if recent deployment

## Escalation
If not resolved in 10 minutes, escalate to: on-call engineer
""",
    "llm_provider_down": """
# LLM Provider Unavailable

## Symptoms
- `ProviderUnavailable` alert
- LLM requests failing
- Enrichment pipeline stalled

## Resolution Steps
1. Check provider status page
2. Verify API key validity
3. Check rate limit status
4. Automatic: Switch to backup provider
5. Manual: Update provider priority

## Escalation
If all providers down, escalate to: platform team
""",
}


def get_runbook(alert_name: str) -> str:
    """Get runbook for alert.

    Args:
        alert_name: Alert name.

    Returns:
        Runbook markdown or default.
    """
    # Normalize alert name
    key = alert_name.lower().replace(" ", "_")
    return RUNBOOKS.get(key, "No runbook available for this alert.")
