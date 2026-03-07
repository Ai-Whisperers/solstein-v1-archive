"""Evidence graph repositories.

EPIC-022: Modularized Neo4j evidence graph operations.

Each entity type has its own repository for clean separation of concerns.
"""

from .base import EvidenceGraphRepository
from .claim import ClaimRepository
from .company import CompanyRepository
from .contradiction import ContradictionRepository
from .source import SourceRepository

__all__ = [
    "EvidenceGraphRepository",
    "CompanyRepository",
    "SourceRepository",
    "ClaimRepository",
    "ContradictionRepository",
]
