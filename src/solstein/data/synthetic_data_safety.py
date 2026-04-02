"""Synthetic data safety controls.

L1: Enforce authenticity labeling and hard no-ship gate for synthetic data.
Prevents synthetic or mixed data from being exported to production reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from ..domain.models import Company


class DataSourceType(Enum):
    """Classification of data source authenticity."""

    REAL = "real"
    SYNTHETIC = "synthetic"
    MIXED = "mixed"
    UNKNOWN = "unknown"

    @property
    def is_blocked(self) -> bool:
        """Whether this source type is blocked from export."""
        return self in (DataSourceType.SYNTHETIC, DataSourceType.MIXED)


@dataclass(frozen=True)
class DataAuthenticity:
    """Represents the authenticity status of company data.

    L1: Tracks whether data is real, synthetic, or mixed, and whether
    it should be blocked from production exports.
    """

    source_type: DataSourceType = DataSourceType.UNKNOWN
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)
    synthetic_percentage: float = 0.0
    verification_method: str = ""
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_blocked(self) -> bool:
        """Whether this data should be blocked from export."""
        if self.source_type == DataSourceType.SYNTHETIC:
            return True
        if self.source_type == DataSourceType.MIXED and self.synthetic_percentage > 0:
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_type": self.source_type.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "synthetic_percentage": self.synthetic_percentage,
            "verification_method": self.verification_method,
            "verified_at": self.verified_at.isoformat(),
            "is_blocked": self.is_blocked,
        }

    @classmethod
    def from_company(cls, company: Company) -> DataAuthenticity:
        """Create authenticity record from a company.

        Args:
            company: The company to analyze

        Returns:
            DataAuthenticity record
        """
        source_type_str = getattr(company, "data_source_type", "unknown")
        source_type_str = source_type_str or "unknown"
        source_type = DataSourceType(source_type_str.lower())
        source_type = DataSourceType(source_type_str.lower())

        sources = getattr(company, "data_sources", [])
        if isinstance(sources, str):
            sources = [sources]

        synthetic_percentage = getattr(company, "synthetic_percentage", 0.0)
        if isinstance(synthetic_percentage, (int, float)):
            synthetic_percentage = float(synthetic_percentage)
        else:
            synthetic_percentage = 0.0

        return cls(
            source_type=source_type,
            confidence=getattr(company, "data_confidence", 0.0),
            sources=sources or [],
            synthetic_percentage=synthetic_percentage,
            verification_method=getattr(company, "verification_method", ""),
        )


@dataclass(frozen=True)
class AuthenticityLabel:
    """Label attached to exported data indicating authenticity.

    L1: Every export must carry an authenticity label showing whether
    the data is real, synthetic, or mixed.
    """

    source_type: DataSourceType
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)
    synthetic_percentage: float = 0.0
    verification_method: str = ""
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    blocked_for_export: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for embedding in exports."""
        return {
            "source_type": self.source_type.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "synthetic_percentage": self.synthetic_percentage,
            "verification_method": self.verification_method,
            "verified_at": self.verified_at.isoformat(),
            "is_blocked": self.blocked_for_export,
            "authenticity_status": "BLOCKED" if self.blocked_for_export else "VERIFIED",
        }


def create_authenticity_label(company: Company) -> AuthenticityLabel:
    """Create an authenticity label for a company.

    Args:
        company: The company to label

    Returns:
        AuthenticityLabel with blocked status set appropriately
    """
    authenticity = DataAuthenticity.from_company(company)

    return AuthenticityLabel(
        source_type=authenticity.source_type,
        confidence=authenticity.confidence,
        sources=authenticity.sources,
        synthetic_percentage=authenticity.synthetic_percentage,
        verification_method=authenticity.verification_method,
        verified_at=authenticity.verified_at,
        blocked_for_export=authenticity.is_blocked,
    )


class SyntheticDataError(Exception):
    """Exception raised when synthetic data is detected and blocked.

    L1: Hard no-ship gate - raises this error when attempting to export
    synthetic or mixed data to production reports.
    """

    def __init__(
        self,
        message: str,
        code: str = "SYNTHETIC_DATA_BLOCKED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class BlockerCheckResult:
    """Result of checking companies for synthetic data."""

    passed: bool
    violations: list[DataAuthenticity]
    checked_count: int
    blocked_count: int
    allowed_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "passed": self.passed,
            "checked_count": self.checked_count,
            "blocked_count": self.blocked_count,
            "allowed_count": self.allowed_count,
            "violations": [v.to_dict() for v in self.violations],
        }


class SyntheticDataBlocker:
    """Blocks synthetic and mixed data from being exported.

    L1: Enforces the hard no-ship policy for synthetic data.
    Configurable thresholds for what constitutes blockable data.
    """

    def __init__(
        self,
        block_synthetic: bool = True,
        block_mixed: bool = True,
        synthetic_threshold_percentage: float = 0.0,
    ) -> None:
        """Initialize the blocker.

        Args:
            block_synthetic: Whether to block fully synthetic data
            block_mixed: Whether to block mixed data
            synthetic_threshold_percentage: Threshold for blocking mixed data
                (0 = block any mixed data, 50 = block if >50% synthetic)
        """
        self.block_synthetic = block_synthetic
        self.block_mixed = block_mixed
        self.synthetic_threshold_percentage = synthetic_threshold_percentage

    def check_company(self, company: Company) -> BlockerCheckResult:
        """Check a single company for synthetic data.

        Args:
            company: The company to check

        Returns:
            BlockerCheckResult with pass/fail status
        """
        authenticity = DataAuthenticity.from_company(company)
        violations: list[DataAuthenticity] = []

        if authenticity.source_type == DataSourceType.SYNTHETIC and self.block_synthetic:
            violations.append(authenticity)
            logger.warning(
                "Synthetic data detected",
                company=getattr(company, "name", "unknown"),
                source_type=authenticity.source_type.value,
            )
        elif authenticity.source_type == DataSourceType.MIXED and self.block_mixed:
            if authenticity.synthetic_percentage >= self.synthetic_threshold_percentage:
                violations.append(authenticity)
                logger.warning(
                    "Mixed data with synthetic content detected",
                    company=getattr(company, "name", "unknown"),
                    synthetic_percentage=authenticity.synthetic_percentage,
                    threshold=self.synthetic_threshold_percentage,
                )

        return BlockerCheckResult(
            passed=len(violations) == 0,
            violations=violations,
            checked_count=1,
            blocked_count=len(violations),
            allowed_count=1 - len(violations),
        )

    def check_companies(self, companies: list[Company]) -> BlockerCheckResult:
        """Check multiple companies for synthetic data.

        Args:
            companies: The companies to check

        Returns:
            BlockerCheckResult with aggregated results
        """
        all_violations: list[DataAuthenticity] = []
        blocked_count = 0
        allowed_count = 0

        for company in companies:
            result = self.check_company(company)
            all_violations.extend(result.violations)
            blocked_count += result.blocked_count
            allowed_count += result.allowed_count

        return BlockerCheckResult(
            passed=blocked_count == 0,
            violations=all_violations,
            checked_count=len(companies),
            blocked_count=blocked_count,
            allowed_count=allowed_count,
        )

    def ensure_safe(self, companies: list[Company]) -> None:
        """Ensure all companies are safe to export, or raise error.

        L1: Hard no-ship gate - raises SyntheticDataError if any
        synthetic or blocked mixed data is detected.

        Args:
            companies: The companies to check

        Raises:
            SyntheticDataError: If any company contains blocked data
        """
        result = self.check_companies(companies)

        if not result.passed:
            violation_names = [
                f"Company with {v.source_type.value} data"
                for v in result.violations[:3]  # Show first 3
            ]
            message = (
                f"Export blocked: {result.blocked_count} company(s) contain "
                f"synthetic or mixed data: {', '.join(violation_names)}"
            )

            logger.error(
                "Synthetic data export blocked",
                blocked_count=result.blocked_count,
                violations=[v.to_dict() for v in result.violations],
            )

            raise SyntheticDataError(
                message=message,
                code="SYNTHETIC_DATA_BLOCKED",
                details={
                    "blocked_count": result.blocked_count,
                    "checked_count": result.checked_count,
                    "violations": [v.to_dict() for v in result.violations],
                },
            )

        logger.info(
            "All companies passed synthetic data check",
            count=len(companies),
        )

    def get_authenticity_summary(self, companies: list[Company]) -> dict[str, Any]:
        """Get a summary of authenticity status for all companies.

        Args:
            companies: The companies to analyze

        Returns:
            Summary dictionary with counts by type
        """
        type_counts: dict[str, int] = {
            "real": 0,
            "synthetic": 0,
            "mixed": 0,
            "unknown": 0,
        }
        blocked = 0
        allowed = 0

        for company in companies:
            auth = DataAuthenticity.from_company(company)
            type_counts[auth.source_type.value] += 1

            if auth.is_blocked:
                blocked += 1
            else:
                allowed += 1

        return {
            "total": len(companies),
            "real": type_counts["real"],
            "synthetic": type_counts["synthetic"],
            "mixed": type_counts["mixed"],
            "unknown": type_counts["unknown"],
            "blocked": blocked,
            "allowed": allowed,
        }
