"""Notification channel implementations: Slack webhook, Email (SMTP).

STORY-104: Each channel implements the NotificationChannel protocol.
Delivery is best-effort with 3 retries. Failures are logged, never propagated.
"""

from __future__ import annotations

import logging
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiohttp

from solstein.notifications.events import EventType, NotificationEvent

logger = logging.getLogger(__name__)

# Max retries for notification delivery (best-effort)
MAX_DELIVERY_RETRIES = 3


class NotificationChannel(ABC):
    """Abstract base class for notification delivery channels."""

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Human-readable channel name."""

    @abstractmethod
    async def send(self, event: NotificationEvent) -> bool:
        """Send a notification event through this channel.

        Returns:
            True if delivery succeeded, False otherwise.
            Failures are logged internally — callers should not retry.
        """


class SlackChannel(NotificationChannel):
    """Slack webhook notification channel.

    Sends formatted messages to a Slack channel via incoming webhook URL.
    Supports per-event-type emoji and color coding.
    """

    # Event type to Slack formatting
    EVENT_EMOJI: dict[EventType, str] = {
        EventType.RESEARCH_COMPLETED: ":white_check_mark:",
        EventType.RESEARCH_FAILED: ":x:",
        EventType.SOURCE_DEGRADED: ":warning:",
        EventType.DLQ_THRESHOLD_EXCEEDED: ":rotating_light:",
        EventType.EXPORT_READY: ":package:",
    }

    EVENT_COLOR: dict[EventType, str] = {
        EventType.RESEARCH_COMPLETED: "#36a64f",
        EventType.RESEARCH_FAILED: "#dc3545",
        EventType.SOURCE_DEGRADED: "#ffc107",
        EventType.DLQ_THRESHOLD_EXCEEDED: "#dc3545",
        EventType.EXPORT_READY: "#17a2b8",
    }

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    @property
    def channel_name(self) -> str:
        return "slack"

    def _build_payload(self, event: NotificationEvent) -> dict[str, Any]:
        """Build Slack message payload with attachment formatting."""
        emoji = self.EVENT_EMOJI.get(event.event_type, ":bell:")
        color = self.EVENT_COLOR.get(event.event_type, "#808080")

        return {
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} {event.title}",
                    "text": event.message,
                    "footer": f"Solstein | {event.event_type.value}",
                    "ts": int(event.timestamp.timestamp()),
                }
            ]
        }

    async def send(self, event: NotificationEvent) -> bool:
        """Send notification via Slack webhook."""
        payload = self._build_payload(event)

        for attempt in range(MAX_DELIVERY_RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            logger.info(
                                "[Slack] Notification sent: %s",
                                event.event_type.value,
                            )
                            return True
                        body = await resp.text()
                        logger.warning(
                            "[Slack] HTTP %d on attempt %d: %s",
                            resp.status,
                            attempt + 1,
                            body[:200],
                        )
            except Exception as exc:
                logger.warning(
                    "[Slack] Delivery attempt %d failed: %s",
                    attempt + 1,
                    exc,
                )

        logger.error(
            "[Slack] Notification delivery failed after %d attempts: %s",
            MAX_DELIVERY_RETRIES,
            event.event_type.value,
        )
        return False


class EmailChannel(NotificationChannel):
    """SMTP email notification channel.

    Sends HTML-formatted emails via configured SMTP server.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str | None = None,
        use_tls: bool = True,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    @property
    def channel_name(self) -> str:
        return "email"

    def _build_html(self, event: NotificationEvent) -> str:
        """Build simple HTML email body."""
        meta_rows = ""
        for key, value in event.metadata.items():
            if value is not None:
                meta_rows += f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>{event.title}</h2>
            <p>{event.message}</p>
            <table style="border-collapse: collapse; margin-top: 10px;">
                {meta_rows}
            </table>
            <hr>
            <p style="color: #888; font-size: 12px;">
                Solstein Notification | {event.event_type.value} | {event.timestamp.isoformat()}
            </p>
        </body>
        </html>
        """

    async def send(self, event: NotificationEvent) -> bool:
        """Send notification via email.

        Note: SMTP is synchronous. In production, this should be wrapped
        in asyncio.to_thread or dispatched via Celery task.
        """
        recipient = event.metadata.get("recipient_email")
        if not recipient:
            logger.warning("[Email] No recipient_email in event metadata, skipping")
            return False

        for attempt in range(MAX_DELIVERY_RETRIES):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"[Solstein] {event.title}"
                msg["From"] = self.sender_email
                msg["To"] = recipient

                html_body = self._build_html(event)
                msg.attach(MIMEText(html_body, "html"))

                if self.use_tls:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                    server.starttls()
                else:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port)

                if self.sender_password:
                    server.login(self.sender_email, self.sender_password)

                server.sendmail(self.sender_email, [recipient], msg.as_string())
                server.quit()

                logger.info("[Email] Notification sent to %s: %s", recipient, event.event_type.value)
                return True

            except Exception as exc:
                logger.warning(
                    "[Email] Delivery attempt %d failed: %s",
                    attempt + 1,
                    exc,
                )

        logger.error(
            "[Email] Notification delivery failed after %d attempts: %s",
            MAX_DELIVERY_RETRIES,
            event.event_type.value,
        )
        return False
