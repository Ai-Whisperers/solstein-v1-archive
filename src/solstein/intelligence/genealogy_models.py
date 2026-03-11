"""Corporate genealogy tracker for Epic 3.

Tracks M&A history, ownership changes, subsidiaries, and corporate structure evolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    ACQUISITION = "acquisition"
    MERGER = "merger"
    DIVESTITURE = "divestiture"
    SPIN_OFF = "spin_off"
    SUBSIDIARY_FORMATION = "subsidiary_formation"
    OWNERSHIP_CHANGE = "ownership_change"
    JOINT_VENTURE = "joint_venture"
    STRATEGIC_PARTNERSHIP = "strategic_partnership"


class TransactionStatus(Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    RUMORED = "rumored"


@dataclass
class CorporateTransaction:
    transaction_type: TransactionType
    date: Optional[date]
    target_name: str
    acquirer_name: Optional[str]
    value_eur_millions: Optional[float] = None
    status: TransactionStatus = TransactionStatus.COMPLETED
    description: str = ""
    strategic_rationale: str = ""
    source: str = ""


@dataclass
class OwnershipStake:
    owner_name: str
    percentage: Optional[float]
    acquisition_date: Optional[date]
    current: bool = True


@dataclass
class SubsidiaryInfo:
    name: str
    relationship_type: str
    formation_date: Optional[date]
    geography: str = ""
    business_focus: str = ""


@dataclass
class CorporateGenealogy:
    company_name: str
    transactions: list[CorporateTransaction] = field(default_factory=list)
    ownership_history: list[OwnershipStake] = field(default_factory=list)
    subsidiaries: list[SubsidiaryInfo] = field(default_factory=list)
    parent_companies: list[OwnershipStake] = field(default_factory=list)

    acquisition_count: int = 0
    divestiture_count: int = 0
    merger_count: int = 0

    total_acquisition_value: Optional[float] = None
    total_divestiture_value: Optional[float] = None

    current_owner: Optional[str] = None
    ownership_type: str = "independent"

    genealogy_narrative: str = ""
    strategic_implications: str = ""
    integration_risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "acquisition_count": self.acquisition_count,
            "divestiture_count": self.divestiture_count,
            "merger_count": self.merger_count,
            "total_acquisition_value": self.total_acquisition_value,
            "total_divestiture_value": self.total_divestiture_value,
            "current_owner": self.current_owner,
            "ownership_type": self.ownership_type,
            "transactions": [
                {
                    "type": t.transaction_type.value,
                    "date": t.date.isoformat() if t.date else None,
                    "target": t.target_name,
                    "acquirer": t.acquirer_name,
                    "value_eur_millions": t.value_eur_millions,
                    "status": t.status.value,
                    "description": t.description,
                }
                for t in self.transactions
            ],
            "subsidiaries": [
                {
                    "name": s.name,
                    "relationship": s.relationship_type,
                    "formation_date": s.formation_date.isoformat() if s.formation_date else None,
                    "geography": s.geography,
                    "business_focus": s.business_focus,
                }
                for s in self.subsidiaries
            ],
            "genealogy_narrative": self.genealogy_narrative,
            "strategic_implications": self.strategic_implications,
            "integration_risks": self.integration_risks,
        }
