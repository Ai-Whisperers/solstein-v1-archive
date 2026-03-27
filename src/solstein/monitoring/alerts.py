"""Intelligent alerting system for Solstein.

EPIC-026 Story 2: Implements smart alerting with:
- Severity-based alerting (critical, warning, info)
- Alert grouping to reduce noise
- Multiple notification channels
- Alert history and deduplication

Usage:
    from solstein.monitoring.alerts import AlertManager, AlertSeverity

    alerts = AlertManager()
    await alerts.send(
        "HighErrorRate",
        AlertSeverity.CRITICAL,
        "Error rate exceeds 10%",
        {"error_rate": 0.12}
    )
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels."""

    SLACK = "slack"
    EMAIL = "email"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class Alert:
    """Represents a single alert."""

    id: str
    name: str
    severity: AlertSeverity
    message: str
    details: dict[str, Any]
    timestamp: float
    channels: list[AlertChannel] = field(default_factory=list)
    runbook_url: str | None = None
    dashboard_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "channels": [c.value for c in self.channels],
            "runbook_url": self.runbook_url,
            "dashboard_url": self.dashboard_url,
        }


@dataclass
class AlertRule:
    """Alert rule configuration."""

    name: str
    severity: AlertSeverity
    condition: str
    duration: str
    channels: list[AlertChannel]
    description: str = ""
    runbook_url: str | None = None
    auto_resolve: bool = True


@dataclass
class AlertGroup:
    """Grouped related alerts."""

    group_name: str
    alerts: list[Alert] = field(default_factory=list)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    def add(self, alert: Alert):
        """Add alert to group."""
        self.alerts.append(alert)
        self.last_seen = time.time()

    def summary(self) -> str:
        """Get group summary."""
        counts = {}
        for alert in self.alerts:
            counts[alert.severity.value] = counts.get(alert.severity.value, 0) + 1

        parts = [f"{count} {sev}" for sev, count in counts.items()]
        return f"{self.group_name}: {', '.join(parts)}"


class NotificationChannel:
    """Base class for notification channels."""

    async def send(self, alert: Alert) -> bool:
        """Send alert through this channel.

        Args:
            alert: Alert to send.

        Returns:
            True if sent successfully.
        """
        raise NotImplementedError


class LogChannel(NotificationChannel):
    """Log-based notification channel."""

    async def send(self, alert: Alert) -> bool:
        """Send alert to logs."""
        log_func = logger.info
        if alert.severity == AlertSeverity.WARNING:
            log_func = logger.warning
        elif alert.severity == AlertSeverity.CRITICAL:
            log_func = logger.error

        log_func(
            f"ALERT [{alert.severity.value.upper()}] {alert.name}: {alert.message}",
            alert_id=alert.id,
            details=alert.details,
        )
        return True


class SlackChannel(NotificationChannel):
    """Slack notification channel."""

    def __init__(self, webhook_url: str | None = None):
        """Initialize Slack channel.

        Args:
            webhook_url: Slack webhook URL.
        """
        self.webhook_url = webhook_url

    async def send(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        if not self.webhook_url:
            logger.warning("Slack webhook not configured")
            return False

        # Color based on severity
        colors = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9900",
            AlertSeverity.CRITICAL: "#ff0000",
        }

        payload = {
            "attachments": [
                {
                    "color": colors.get(alert.severity, "#cccccc"),
                    "title": f"{alert.severity.value.upper()}: {alert.name}",
                    "text": alert.message,
                    "fields": [{"title": k, "value": str(v), "short": True} for k, v in alert.details.items()],
                    "footer": "Solstein Monitoring",
                    "ts": alert.timestamp,
                }
            ]
        }

        if alert.runbook_url:
            payload["attachments"][0]["actions"] = [
                {
                    "type": "button",
                    "text": "View Runbook",
                    "url": alert.runbook_url,
                }
            ]

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False


class PagerDutyChannel(NotificationChannel):
    """PagerDuty notification channel."""

    def __init__(self, integration_key: str | None = None):
        """Initialize PagerDuty channel.

        Args:
            integration_key: PagerDuty integration key.
        """
        self.integration_key = integration_key

    async def send(self, alert: Alert) -> bool:
        """Send alert to PagerDuty."""
        if not self.integration_key:
            logger.warning("PagerDuty integration key not configured")
            return False

        # Only send critical alerts to PagerDuty
        if alert.severity != AlertSeverity.CRITICAL:
            return True

        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": alert.id,
            "payload": {
                "summary": f"{alert.name}: {alert.message}",
                "severity": "critical",
                "source": "solstein-monitoring",
                "custom_details": alert.details,
            },
        }

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post("https://events.pagerduty.com/v2/enqueue", json=payload) as response:
                    return response.status == 202
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
            return False


class AlertManager:
    """Manages alerts, deduplication, and notifications."""

    # Alert groupings
    ALERT_GROUPS = {
        "database": ["DatabaseConnectionFailed", "SlowQuery", "PoolExhaustion"],
        "api": ["HighErrorRate", "HighLatency", "RateLimitExceeded"],
        "llm": ["ProviderUnavailable", "HighCost", "LowSuccessRate"],
        "infrastructure": ["DiskFull", "MemoryPressure", "HighCPU"],
    }

    def __init__(
        self,
        slack_webhook: str | None = None,
        pagerduty_key: str | None = None,
        dedup_window: int = 300,  # 5 minutes
    ):
        """Initialize alert manager.

        Args:
            slack_webhook: Slack webhook URL.
            pagerduty_key: PagerDuty integration key.
            dedup_window: Deduplication window in seconds.
        """
        self.dedup_window = dedup_window
        self.alert_history: dict[str, float] = {}  # alert_id -> timestamp
        self.channels: dict[AlertChannel, NotificationChannel] = {
            AlertChannel.LOG: LogChannel(),
            AlertChannel.SLACK: SlackChannel(slack_webhook),
            AlertChannel.PAGERDUTY: PagerDutyChannel(pagerduty_key),
        }
        self.active_alerts: dict[str, Alert] = {}
        self.alert_groups: dict[str, AlertGroup] = {}

    def _generate_alert_id(self, name: str, details: dict[str, Any]) -> str:
        """Generate unique alert ID for deduplication.

        Args:
            name: Alert name.
            details: Alert details.

        Returns:
            Alert ID hash.
        """
        content = f"{name}:{str(sorted(details.items()))}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _get_group_name(self, alert_name: str) -> str | None:
        """Get group name for an alert.

        Args:
            alert_name: Alert name.

        Returns:
            Group name or None.
        """
        for group, alerts in self.ALERT_GROUPS.items():
            if alert_name in alerts:
                return group
        return None

    def _should_send(self, alert_id: str) -> bool:
        """Check if alert should be sent (deduplication).

        Args:
            alert_id: Alert ID.

        Returns:
            True if should send.
        """
        now = time.time()
        last_sent = self.alert_history.get(alert_id, 0)

        if now - last_sent > self.dedup_window:
            self.alert_history[alert_id] = now
            return True

        return False

    async def send(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        details: dict[str, Any] | None = None,
        channels: list[AlertChannel] | None = None,
        runbook_url: str | None = None,
        dashboard_url: str | None = None,
    ) -> Alert | None:
        """Send an alert.

        Args:
            name: Alert name.
            severity: Alert severity.
            message: Alert message.
            details: Additional details.
            channels: Override channels to use.
            runbook_url: Runbook documentation URL.
            dashboard_url: Dashboard URL.

        Returns:
            Alert if sent, None if deduplicated.
        """
        details = details or {}
        alert_id = self._generate_alert_id(name, details)

        # Check deduplication
        if not self._should_send(alert_id):
            logger.debug(f"Alert {name} deduplicated")
            return None

        # Determine channels based on severity
        if channels is None:
            channels = self._get_channels_for_severity(severity)

        alert = Alert(
            id=alert_id,
            name=name,
            severity=severity,
            message=message,
            details=details,
            timestamp=time.time(),
            channels=channels,
            runbook_url=runbook_url,
            dashboard_url=dashboard_url,
        )

        self.active_alerts[alert_id] = alert

        # Add to group
        group_name = self._get_group_name(name)
        if group_name:
            if group_name not in self.alert_groups:
                self.alert_groups[group_name] = AlertGroup(group_name)
            self.alert_groups[group_name].add(alert)

        # Send to channels
        await self._notify_channels(alert)

        return alert

    def _get_channels_for_severity(self, severity: AlertSeverity) -> list[AlertChannel]:
        """Get default channels for severity.

        Args:
            severity: Alert severity.

        Returns:
            List of channels.
        """
        if severity == AlertSeverity.CRITICAL:
            return [AlertChannel.PAGERDUTY, AlertChannel.SLACK, AlertChannel.LOG]
        elif severity == AlertSeverity.WARNING:
            return [AlertChannel.SLACK, AlertChannel.LOG]
        else:
            return [AlertChannel.LOG]

    async def _notify_channels(self, alert: Alert):
        """Send alert to all configured channels.

        Args:
            alert: Alert to send.
        """
        tasks = []
        for channel in alert.channels:
            if channel in self.channels:
                handler = self.channels[channel]
                tasks.append(handler.send(alert))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for channel, result in zip(alert.channels, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to send to {channel.value}: {result}")

    async def resolve(self, alert_id: str, message: str = ""):
        """Resolve an active alert.

        Args:
            alert_id: Alert ID to resolve.
            message: Resolution message.
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            logger.info(
                f"Alert resolved: {alert.name}",
                alert_id=alert_id,
                message=message,
            )

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get list of active alerts.

        Args:
            severity: Filter by severity.

        Returns:
            List of active alerts.
        """
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_group_summary(self) -> dict[str, str]:
        """Get summary of all alert groups.

        Returns:
            Dictionary mapping group name to summary.
        """
        return {name: group.summary() for name, group in self.alert_groups.items()}

    def clear_group(self, group_name: str):
        """Clear all alerts in a group.

        Args:
            group_name: Group name to clear.
        """
        if group_name in self.alert_groups:
            group = self.alert_groups[group_name]
            for alert in group.alerts:
                self.active_alerts.pop(alert.id, None)
            del self.alert_groups[group_name]


# Predefined alert rules
DEFAULT_ALERT_RULES = [
    AlertRule(
        name="ServiceDown",
        severity=AlertSeverity.CRITICAL,
        condition="up{job='solstein-api'} == 0",
        duration="1m",
        channels=[AlertChannel.PAGERDUTY, AlertChannel.SLACK],
        description="Service is not responding",
        runbook_url="https://wiki.solstein.ai/runbooks/service-down",
    ),
    AlertRule(
        name="DatabaseConnectionFailed",
        severity=AlertSeverity.CRITICAL,
        condition="db_connection_errors_total > 10",
        duration="2m",
        channels=[AlertChannel.PAGERDUTY, AlertChannel.SLACK],
        description="Database connection failures",
        runbook_url="https://wiki.solstein.ai/runbooks/database-connection-failed",
    ),
    AlertRule(
        name="HighErrorRate",
        severity=AlertSeverity.CRITICAL,
        condition="rate(http_requests_total{status=~'5..'}[5m]) > 0.1",
        duration="2m",
        channels=[AlertChannel.SLACK, AlertChannel.PAGERDUTY],
        description="High error rate detected",
    ),
    AlertRule(
        name="HighLatency",
        severity=AlertSeverity.WARNING,
        condition="histogram_quantile(0.95, http_request_duration_seconds) > 0.5",
        duration="5m",
        channels=[AlertChannel.SLACK],
        description="High API latency",
    ),
    AlertRule(
        name="LowCacheHitRate",
        severity=AlertSeverity.WARNING,
        condition="cache_hit_rate < 0.5",
        duration="10m",
        channels=[AlertChannel.SLACK],
        description="Low cache hit rate",
    ),
    AlertRule(
        name="ProviderUnavailable",
        severity=AlertSeverity.WARNING,
        condition="llm_provider_available == 0",
        duration="2m",
        channels=[AlertChannel.SLACK],
        description="LLM provider unavailable",
    ),
    AlertRule(
        name="HighDailyLLMCost",
        severity=AlertSeverity.WARNING,
        condition="increase(llm_cost_dollars_total[1d]) > 500",
        duration="0m",
        channels=[AlertChannel.SLACK],
        description="Daily LLM cost exceeds $500",
    ),
]
