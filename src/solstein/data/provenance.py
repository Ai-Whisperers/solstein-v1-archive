"""Data provenance tracking and validation.

H1-H3: Provenance and confidence tracking
Tracks data lineage and validates confidence for PE-critical fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Protocol

from loguru import logger


class SourceReliability(Enum):
    """Reliability levels for data sources."""

    VERIFIED = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    UNVERIFIED = 0.2


class ConfidenceLevel(Enum):
    """Confidence levels for data points.

    H3: Deterministic confidence level mapping.
    """

    CERTAIN = (0.95, "Certain")
    HIGH = (0.80, "High")
    MEDIUM = (0.60, "Medium")
    LOW = (0.40, "Low")
    UNCERTAIN = (0.0, "Uncertain")

    def __init__(self, min_score: float, label: str) -> None:
        self.min_score = min_score
        self.label = label

    @classmethod
    def from_score(cls, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level.

        H3: Deterministic confidence level mapping.
        """
        for level in [cls.CERTAIN, cls.HIGH, cls.MEDIUM, cls.LOW]:
            if score >= level.min_score:
                return level
        return cls.UNCERTAIN


class ValidationMode(Enum):
    """Validation strictness mode."""

    STRICT = auto()
    NORMAL = auto()
    LENIENT = auto()


@dataclass
class FieldProvenance:
    """Provenance information for a single field.

    H1: Tracks origin and confidence for each data point.
    """

    source: str | None = None
    timestamp: datetime | None = None
    confidence: float = 1.0
    reliability: SourceReliability = SourceReliability.VERIFIED
    extraction_method: str = "unknown"
    raw_value: Any = None
    verification_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence": self.confidence,
            "reliability": self.reliability.name.lower(),
            "extraction_method": self.extraction_method,
        }


@dataclass
class DataProvenance:
    """Container for all field-level provenance.

    H1: Aggregates provenance across all PE-critical fields.
    """

    fields: dict[str, FieldProvenance] = field(default_factory=dict)
    company_id: str | None = None
    collection_timestamp: datetime | None = None
    overall_confidence: float = 1.0

    def get_field_provenance(self, field_name: str) -> FieldProvenance:
        """Get provenance for a specific field."""
        return self.fields.get(field_name, FieldProvenance(confidence=0.0))
        """Get provenance for a specific field."""
        return self.fields.get(field_name)

    def set_field_provenance(self, field_name: str, provenance: FieldProvenance) -> None:
        """Set provenance for a specific field."""
        self.fields[field_name] = provenance

    def has_field(self, field_name: str) -> bool:
        """Check if field has provenance recorded."""
        return field_name in self.fields

    def add_field(self, field_name: str, **kwargs) -> None:
        """Add provenance for a field with keyword arguments."""
        self.fields[field_name] = FieldProvenance(**kwargs)

    def calculate_overall_confidence(self) -> float:
        """Calculate overall confidence score across all fields."""
        if not self.fields:
            return 1.0
        return sum(f.confidence for f in self.fields.values()) / len(self.fields)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "company_id": self.company_id,
            "collection_timestamp": self.collection_timestamp.isoformat() if self.collection_timestamp else None,
            "overall_confidence": self.calculate_overall_confidence(),
            "field_count": len(self.fields),
            "fields": {name: prov.to_dict() for name, prov in self.fields.items()},
        }


@dataclass
class ProvenanceViolation:
    """A provenance validation violation.

    H2: Structured violation reporting for missing/invalid provenance.
    """

    field: str
    violation_type: str
    message: str
    severity: str = "error"
    expected: Any = None
    actual: Any = None


class ProvenanceError(Exception):
    """Exception raised for provenance validation failures."""

    def __init__(
        self,
        message: str,
        code: str = "PROVENANCE_ERROR",
        violations: list[ProvenanceViolation] | None = None,
        company_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.violations = violations or []
        self.company_id = company_id
        self.violation_count = len(self.violations)


# H1: Required PE fields that must have provenance
REQUIRED_PE_FIELDS = {
    "revenue",
    "growth_rate",
    "profit_margin",
    "funding_total",
    "valuation",
    "employee_count",
    "ebitda",
}

# H3: Staleness thresholds by field category
STALENESS_THRESHOLDS = {
    "financial": timedelta(days=90),
    "employee": timedelta(days=180),
    "funding": timedelta(days=365),
    "valuation": timedelta(days=180),
}


class HasProvenance(Protocol):
    """Protocol for objects that have provenance."""

    provenance: DataProvenance


class ProvenanceValidator:
    """Validates data provenance for PE-critical fields.

    H1-H3: Validates that required fields have:
    - Source attribution (provenance exists)
    - Confidence scores above thresholds (H3)
    - Acceptable staleness (H3)
    - Reliable sources (H2)
    """

    def __init__(
        self,
        mode: ValidationMode = ValidationMode.NORMAL,
        min_confidence: float = 0.6,
        min_reliability: SourceReliability = SourceReliability.LOW,
        required_fields: set[str] | None = None,
    ) -> None:
        self.mode = mode
        self.min_confidence = min_confidence
        self.min_reliability = min_reliability
        self.required_fields = required_fields or REQUIRED_PE_FIELDS

    def is_field_complete(self, field_name: str, provenance: DataProvenance) -> bool:
        """Check if a field has complete provenance.

        Args:
            field_name: Name of the field
            provenance: Provenance information

        Returns:
            True if field has complete provenance
        """
        if not provenance.has_field(field_name):
            return False

        field_prov = provenance.get_field_provenance(field_name)
        if field_prov is None:
            return False

        # Check minimum requirements
        if field_prov.source is None:
            return False
        if field_prov.confidence < self.min_confidence:
            return False
        if field_prov.reliability.value < self.min_reliability.value:
            return False

        return True

    def validate_field(
        self,
        field_name: str,
        value: Any,
        expected_type: type,
        provenance: DataProvenance,
    ) -> list[ProvenanceViolation]:
        """Validate provenance for a single field.

        Args:
            field_name: Name of the field
            value: The field value
            expected_type: Expected type of the value
            provenance: Provenance information

        Returns:
            List of violations found
        """
        violations: list[ProvenanceViolation] = []

        # Check if field has provenance
        if not provenance.has_field(field_name):
            if field_name in self.required_fields:
                violations.append(
                    ProvenanceViolation(
                        field=field_name,
                        violation_type="missing_provenance",
                        message=f"Required field '{field_name}' has no provenance",
                        severity="error" if self.mode == ValidationMode.STRICT else "warning",
                    )
                )
            return violations

        field_prov = provenance.get_field_provenance(field_name)
        if field_prov is None:
            return violations

        # Check confidence
        if field_prov.confidence < self.min_confidence:
            violations.append(
                ProvenanceViolation(
                    field=field_name,
                    violation_type="low_confidence",
                    message=f"Confidence {field_prov.confidence} is below minimum {self.min_confidence}",
                    severity="warning",
                )
            )

        # Check reliability
        if field_prov.reliability.value < self.min_reliability.value:
            violations.append(
                ProvenanceViolation(
                    field=field_name,
                    violation_type="unverified_source",
                    message=f"Source reliability {field_prov.reliability.name} is below minimum {self.min_reliability.name}",
                    severity="warning",
                )
            )

        # Check staleness
        if field_prov.timestamp:
            # Handle both timezone-aware and naive datetimes
            timestamp = field_prov.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - timestamp
            threshold = STALENESS_THRESHOLDS.get("financial", timedelta(days=365))
            if age > threshold:
                violations.append(
                    ProvenanceViolation(
                        field=field_name,
                        violation_type="stale_data",
                        message=f"Data is {age.days} days old (threshold: {threshold.days})",
                        severity="warning",
                    )
                )

        return violations

    def validate_company(self, company: HasProvenance) -> list[ProvenanceViolation]:
        """Validate all required fields for a company.

        Args:
            company: Company object with provenance

        Returns:
            List of violations found
        """
        violations: list[ProvenanceViolation] = []

        for field_name in self.required_fields:
            value = getattr(company, field_name, None)
            field_violations = self.validate_field(
                field_name,
                value,
                type(value) if value is not None else object,
                company.provenance,
            )
            violations.extend(field_violations)

        return violations

    def validate_or_raise(self, company: HasProvenance) -> None:
        """Validate and raise exception if violations found.

        Args:
            company: Company object with provenance

        Raises:
            ProvenanceError: If violations found in strict mode
        """
        violations = self.validate_company(company)

        if not violations:
            return

        # In strict mode, raise exception
        if self.mode == ValidationMode.STRICT:
            error_msg = f"Provenance validation failed with {len(violations)} violation(s)"
            raise ProvenanceError(
                error_msg,
                violations=violations,
                company_id=getattr(company, "id", None),
            )

        # Log violations in other modes
        for v in violations:
            log_fn = logger.error if v.severity == "error" else logger.warning
            log_fn(
                "Provenance violation",
                field=v.field,
                type=v.violation_type,
                message=v.message,
                severity=v.severity,
            )


def calculate_overall_confidence(provenance: DataProvenance) -> tuple[float, ConfidenceLevel]:
    """Calculate overall confidence from field provenances.

    H3: Aggregates confidence across all fields.

    Args:
        provenance: Data provenance

    Returns:
        Tuple of (confidence_score, confidence_level)
    """
    if not provenance.fields:
        return 0.0, ConfidenceLevel.UNCERTAIN

    # Weight by field importance (simplified - all equal)
    total_confidence = sum(f.confidence for f in provenance.fields.values())
    avg_confidence = total_confidence / len(provenance.fields)

    level = ConfidenceLevel.from_score(avg_confidence)
    return avg_confidence, level


def validate_company_provenance(
    company: HasProvenance,
    mode: ValidationMode = ValidationMode.NORMAL,
) -> list[ProvenanceViolation]:
    """Convenience function to validate company provenance.

    Args:
        company: Company object with provenance
        mode: Validation mode

    Returns:
        List of violations
    """
    validator = ProvenanceValidator(mode=mode)
    return validator.validate_company(company)


def create_field_provenance(
    source: str | None = None,
    confidence: float = 1.0,
    reliability: SourceReliability = SourceReliability.VERIFIED,
    extraction_method: str = "unknown",
    raw_value: Any = None,
) -> FieldProvenance:
    """Factory function to create field provenance.

    Args:
        source: Data source name
        confidence: Confidence score (0.0-1.0)
        reliability: Source reliability level
        extraction_method: Method used to extract data
        raw_value: Original raw value

    Returns:
        FieldProvenance instance
    """
    return FieldProvenance(
        source=source,
        confidence=confidence,
        reliability=reliability,
        extraction_method=extraction_method,
        raw_value=raw_value,
    )
