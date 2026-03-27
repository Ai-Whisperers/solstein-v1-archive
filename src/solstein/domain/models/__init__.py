"""Domain models package.

EPIC-021: Modularized domain models.

NOTE: For backward compatibility, all models are re-exported from the original
monolithic models.py file. In a future phase, the models will be migrated to
individual files within this package.

This approach maintains:
- Backward compatibility with existing code
- Pydantic model integrity
- No risk of circular import issues
- Gradual migration path
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class CompanyClassification(StrEnum):
    PHOENIX = "Phoenix"
    SALT = "Salt"
    LEAD = "Lead"


# Import directly from models.py to avoid circular import with package
_spec = importlib.util.spec_from_file_location("_models_module", Path(__file__).parent.parent / "models.py")
if _spec is None or _spec.loader is None:
    raise ImportError("Unable to load legacy domain models module")

_models_module = importlib.util.module_from_spec(_spec)
sys.modules["_models_module"] = _models_module
_spec.loader.exec_module(_models_module)

# Re-export all models from the original location for backward compatibility
ConfidenceLevel = _models_module.ConfidenceLevel
AIMaturity = _models_module.AIMaturity
ThreatLevel = _models_module.ThreatLevel
CompanyTier = _models_module.CompanyTier
ErrorCategory = _models_module.ErrorCategory
ErrorSeverity = _models_module.ErrorSeverity
DataSourceType = _models_module.DataSourceType
FinancialMetric = _models_module.FinancialMetric
Company = _models_module.Company
MarketAnalysis = _models_module.MarketAnalysis
ScoreComponent = _models_module.ScoreComponent
ScoringExplanation = _models_module.ScoringExplanation
CompetitiveOverlap = _models_module.CompetitiveOverlap
RawDataSource = _models_module.RawDataSource
RawDataRecord = _models_module.RawDataRecord
AggregatedFact = _models_module.AggregatedFact
AggregatedDataRecord = _models_module.AggregatedDataRecord
SignalExtraction = _models_module.SignalExtraction
SignalExtractionRecord = _models_module.SignalExtractionRecord
GatheringBatch = _models_module.GatheringBatch
CompanyAnalysisAuditTrail = _models_module.CompanyAnalysisAuditTrail
ApiKeyScope = _models_module.ApiKeyScope  # EPIC-019 STORY-065
ApiKey = _models_module.ApiKey  # EPIC-019 STORY-065

__all__ = [
    # Enums
    "ConfidenceLevel",
    "AIMaturity",
    "ThreatLevel",
    "CompanyClassification",
    "CompanyTier",
    "ErrorCategory",
    "ErrorSeverity",
    "DataSourceType",
    # Financial
    "FinancialMetric",
    # Company
    "Company",
    # Market
    "MarketAnalysis",
    # Scoring
    "ScoreComponent",
    "ScoringExplanation",
    # Competitive
    "CompetitiveOverlap",
    # Research
    "RawDataSource",
    "RawDataRecord",
    "AggregatedFact",
    "AggregatedDataRecord",
    "SignalExtraction",
    "SignalExtractionRecord",
    "GatheringBatch",
    "CompanyAnalysisAuditTrail",
    # API Key Management (EPIC-019)
    "ApiKeyScope",
    "ApiKey",
]
