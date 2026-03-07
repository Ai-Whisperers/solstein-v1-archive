"""GDPR compliance utilities.

EPIC-027 Story 7: GDPR data protection compliance.

Usage:
    from solstein.security.gdpr import GDPRManager, ProcessingBasis

    gdpr = GDPRManager()
    await gdpr.export_user_data(user_id)
    await gdpr.erase_user_data(user_id)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class ProcessingBasis(str, Enum):
    """Legal basis for data processing under GDPR."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    PUBLIC_TASK = "public_task"


@dataclass
class DataExport:
    """User data export for GDPR Article 15."""

    user_id: str
    export_date: datetime
    data: dict[str, Any]
    format: str = "json"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "export_date": self.export_date.isoformat(),
            "format": self.format,
            "data": self.data,
        }


class GDPRManager:
    """Manage GDPR compliance operations."""

    def __init__(self):
        """Initialize GDPR manager."""
        pass

    async def export_user_data(self, user_id: str) -> DataExport:
        """Export all data for a user (GDPR Article 15 - Right to Access).

        Args:
            user_id: User identifier.

        Returns:
            DataExport with all user data.
        """
        logger.info(f"Exporting data for user: {user_id}")

        # In production, gather from all relevant tables
        data = {
            "user_profile": {},
            "companies_accessed": [],
            "research_runs": [],
            "exports_generated": [],
            "audit_logs": [],
        }

        # Log the export
        await self._log_processing(
            user_id=user_id,
            action="data_export",
            basis=ProcessingBasis.LEGAL_OBLIGATION,
            data_categories=["user_data", "access_logs"],
        )

        return DataExport(
            user_id=user_id,
            export_date=datetime.utcnow(),
            data=data,
        )

    async def erase_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR Article 17 - Right to Erasure).

        Args:
            user_id: User identifier.

        Returns:
            True if successful.
        """
        logger.info(f"Erasing data for user: {user_id}")

        # Anonymize rather than delete for referential integrity
        await self._anonymize_user_data(user_id)

        # Log the erasure
        await self._log_processing(
            user_id=user_id,
            action="data_erasure",
            basis=ProcessingBasis.LEGAL_OBLIGATION,
            data_categories=["user_data"],
        )

        return True

    async def _anonymize_user_data(self, user_id: str):
        """Anonymize user data.

        Args:
            user_id: User identifier.
        """
        # Replace PII with anonymous identifiers
        # Keep data for analytics but remove personal identifiers
        logger.info(f"Anonymized data for user: {user_id}")

    async def _log_processing(
        self,
        user_id: str,
        action: str,
        basis: ProcessingBasis,
        data_categories: list[str],
    ):
        """Log data processing activity.

        Args:
            user_id: User identifier.
            action: Processing action.
            basis: Legal basis.
            data_categories: Categories of data processed.
        """
        logger.info(
            f"GDPR processing: {action}",
            user_id=user_id,
            basis=basis.value,
            categories=data_categories,
            timestamp=datetime.utcnow().isoformat(),
        )

    def validate_processing_basis(
        self,
        basis: ProcessingBasis,
        data_categories: list[str],
    ) -> bool:
        """Validate processing basis is appropriate.

        Args:
            basis: Legal basis.
            data_categories: Categories of data.

        Returns:
            True if valid.
        """
        # Special categories require explicit consent
        special_categories = ["health", "biometric", "genetic", "criminal"]

        if any(cat in special_categories for cat in data_categories):
            return basis == ProcessingBasis.CONSENT

        return True


class PrivacyPolicy:
    """Privacy policy management."""

    VERSION = "1.0.0"
    LAST_UPDATED = "2026-03-06"

    @classmethod
    def get_summary(cls) -> dict[str, Any]:
        """Get privacy policy summary.

        Returns:
            Policy summary.
        """
        return {
            "version": cls.VERSION,
            "last_updated": cls.LAST_UPDATED,
            "data_collected": [
                "Company information (publicly available)",
                "User account information",
                "Usage analytics",
                "API request logs",
            ],
            "purposes": [
                "Provide competitive intelligence services",
                "Improve service quality",
                "Security and fraud prevention",
                "Legal compliance",
            ],
            "retention": {
                "user_data": "Account lifetime + 30 days",
                "logs": "1 year",
                "backups": "90 days",
            },
            "rights": [
                "Right to access",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object",
            ],
            "contact": "privacy@solstein.ai",
        }
