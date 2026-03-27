"""Capability overlap matrix for comparing company capabilities against Eneve.

Epic 1: Deep Analysis Intelligence Module - Capability comparison engine.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class OverlapLevel(str, Enum):
    """Level of capability overlap with Eneve."""

    NONE = "none"  # No overlap
    LOW = "low"  # Minimal overlap
    MEDIUM = "medium"  # Partial overlap
    HIGH = "high"  # Significant overlap
    VERY_HIGH = "very_high"  # Core capability match


class EneveCapability(BaseModel):
    """Definition of an Eneve capability for comparison."""

    code: str  # e.g., "time_series_mgmt"
    name: str  # Display name
    description: str
    keywords: list[str]  # Keywords to search for in competitor data
    weight: float = Field(default=1.0, ge=0.0, le=1.0)  # Importance weight


class CapabilityMatch(BaseModel):
    """A match between competitor and Eneve capability."""

    capability_code: str
    overlap_level: OverlapLevel
    evidence: list[str]  # Text snippets showing evidence
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    # Detailed scoring
    keyword_matches: dict[str, int] = Field(default_factory=dict)  # Keyword -> count


def get_eneve_capabilities() -> list[EneveCapability]:
    """Get the standard Eneve capability definitions.

    These are the core capabilities that Eneve's eBase platform provides.
    Used for comparing competitors against Eneve.
    """
    return [
        EneveCapability(
            code="time_series_mgmt",
            name="Time Series Management",
            description="Smart meter data management, linked time series, aggregation",
            keywords=[
                "time series",
                "smart meter",
                "meter data",
                "aggregation",
                "linked series",
                "data historian",
            ],
            weight=1.0,
        ),
        EneveCapability(
            code="balancing_settlement",
            name="Balancing & Settlement",
            description="Power allocation, imbalance management, settlement processing",
            keywords=[
                "balancing",
                "settlement",
                "imbalance",
                "allocation",
                "power allocation",
                "balancing group",
            ],
            weight=1.0,
        ),
        EneveCapability(
            code="nominations_scheduling",
            name="Nominations & Scheduling",
            description="TSO/DSO communication, schedule submission, nominations",
            keywords=[
                "nomination",
                "scheduling",
                "TSO",
                "DSO",
                "schedule",
                "transmission",
                "distribution",
            ],
            weight=0.9,
        ),
        EneveCapability(
            code="message_processing",
            name="Message Processing",
            description="EDI messages, validation, notification processing",
            keywords=[
                "EDI",
                "message processing",
                "validation",
                "notification",
                "AS4",
                "APERAK",
            ],
            weight=0.8,
        ),
        EneveCapability(
            code="market_operations",
            name="Market Operations",
            description="Market participant management, grid area management, EAN codes",
            keywords=[
                "market participant",
                "grid area",
                "EAN",
                "market communication",
                "participant management",
            ],
            weight=0.9,
        ),
        EneveCapability(
            code="commodities_electricity",
            name="Commodities - Electricity",
            description="Electricity/power market focus",
            keywords=[
                "electricity",
                "power",
                "energy",
                "kwh",
                "megawatt",
                "grid",
            ],
            weight=0.85,
        ),
        EneveCapability(
            code="commodities_gas",
            name="Commodities - Gas",
            description="Natural gas market focus",
            keywords=[
                "gas",
                "natural gas",
                "lng",
                "gas balancing",
                "gas nomination",
            ],
            weight=0.75,
        ),
        EneveCapability(
            code="cloud_native",
            name="Cloud-Native Platform",
            description="SaaS/cloud architecture vs on-premise",
            keywords=[
                "cloud",
                "saas",
                "cloud-native",
                "api",
                "microservices",
                "aws",
                "azure",
            ],
            weight=0.7,
        ),
    ]


class CapabilityOverlapMatrix(BaseModel):
    """Matrix comparing a competitor's capabilities to Eneve."""

    entity_id: str
    entity_name: str

    # Individual capability matches
    matches: dict[str, CapabilityMatch] = Field(default_factory=dict)

    # Aggregate scores
    overall_overlap_score: float = Field(default=0.0, ge=0.0, le=1.0)
    matching_capabilities: int = 0
    high_overlap_capabilities: int = 0

    # Comparison summary
    strongest_matches: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)

    def add_match(self, match: CapabilityMatch) -> None:
        """Add a capability match to the matrix."""
        self.matches[match.capability_code] = match
        self._recalculate_scores()

    def _recalculate_scores(self) -> None:
        """Recalculate aggregate scores from matches."""
        if not self.matches:
            return

        # Count matches by level
        level_scores = {
            OverlapLevel.NONE: 0.0,
            OverlapLevel.LOW: 0.25,
            OverlapLevel.MEDIUM: 0.5,
            OverlapLevel.HIGH: 0.75,
            OverlapLevel.VERY_HIGH: 1.0,
        }

        total_score = 0.0
        total_weight = 0.0
        self.matching_capabilities = 0
        self.high_overlap_capabilities = 0
        self.strongest_matches = []
        self.gaps = []

        capabilities = get_eneve_capabilities()

        for cap in capabilities:
            match = self.matches.get(cap.code)
            if match:
                score = level_scores.get(match.overlap_level, 0.0)
                weighted_score = score * cap.weight
                total_score += weighted_score
                total_weight += cap.weight

                if match.overlap_level in [OverlapLevel.HIGH, OverlapLevel.VERY_HIGH]:
                    self.matching_capabilities += 1
                    self.strongest_matches.append(cap.name)

                if match.overlap_level == OverlapLevel.VERY_HIGH:
                    self.high_overlap_capabilities += 1
            else:
                self.gaps.append(cap.name)

        if total_weight > 0:
            self.overall_overlap_score = round(total_score / total_weight, 2)


class OverlapAnalyzer:
    """Analyze capability overlap between a competitor and Eneve."""

    def __init__(self):
        """Initialize with Eneve capability definitions."""
        self.eneve_capabilities = get_eneve_capabilities()
        self.capability_map = {cap.code: cap for cap in self.eneve_capabilities}

    def analyze(
        self,
        entity_id: str,
        entity_name: str,
        source_texts: list[str],
    ) -> CapabilityOverlapMatrix:
        """Analyze capability overlap from source texts.

        Args:
            entity_id: The entity/competitor ID
            entity_name: The entity/competitor name
            source_texts: List of text sources to analyze (website, docs, etc.)

        Returns:
            CapabilityOverlapMatrix with overlap analysis
        """
        matrix = CapabilityOverlapMatrix(
            entity_id=entity_id,
            entity_name=entity_name,
        )

        # HS|        # Combine all source texts (filter out None values)
        filtered_texts = [str(t) if t is not None else "" for t in source_texts]
        combined_text = " ".join(filtered_texts).lower()

        # Analyze each capability
        for capability in self.eneve_capabilities:
            match = self._analyze_capability(capability, combined_text)
            matrix.add_match(match)

        return matrix

    def _analyze_capability(self, capability: EneveCapability, text: str) -> CapabilityMatch:
        """Analyze overlap for a single capability.

        Args:
            capability: The Eneve capability to check
            text: Combined source text

        Returns:
            CapabilityMatch with overlap assessment
        """
        keyword_matches = {}
        evidence_snippets = []

        # Count keyword matches
        for keyword in capability.keywords:
            count = text.count(keyword.lower())
            if count > 0:
                keyword_matches[keyword] = count

        # Determine overlap level based on keyword presence
        total_matches = sum(keyword_matches.values())
        unique_matches = len(keyword_matches)

        if unique_matches >= 3 and total_matches >= 5:
            overlap_level = OverlapLevel.VERY_HIGH
        elif unique_matches >= 2 and total_matches >= 3:
            overlap_level = OverlapLevel.HIGH
        elif unique_matches >= 1 and total_matches >= 2:
            overlap_level = OverlapLevel.MEDIUM
        elif unique_matches >= 1:
            overlap_level = OverlapLevel.LOW
        else:
            overlap_level = OverlapLevel.NONE

        # Calculate confidence based on evidence strength
        if total_matches >= 10:
            confidence = 0.95
        elif total_matches >= 5:
            confidence = 0.85
        elif total_matches >= 2:
            confidence = 0.7
        elif total_matches >= 1:
            confidence = 0.5
        else:
            confidence = 0.0

        # Extract evidence snippets (find sentences containing keywords)
        sentences = text.split(".")
        for sentence in sentences:
            for keyword in keyword_matches.keys():
                if keyword.lower() in sentence:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 20 and clean_sentence not in evidence_snippets:
                        evidence_snippets.append(clean_sentence)
                        break
            if len(evidence_snippets) >= 3:
                break

        return CapabilityMatch(
            capability_code=capability.code,
            overlap_level=overlap_level,
            evidence=evidence_snippets[:3],  # Top 3 snippets
            confidence=confidence,
            keyword_matches=keyword_matches,
        )

    def get_overlap_description(self, level: OverlapLevel) -> str:
        """Get human-readable description of overlap level."""
        descriptions = {
            OverlapLevel.NONE: "No capability overlap detected",
            OverlapLevel.LOW: "Minimal overlap - tangential capability",
            OverlapLevel.MEDIUM: "Moderate overlap - partial capability match",
            OverlapLevel.HIGH: "High overlap - significant capability match",
            OverlapLevel.VERY_HIGH: "Very high overlap - core capability match",
        }
        return descriptions.get(level, "Unknown")

    def compare_competitors(
        self,
        matrices: list[CapabilityOverlapMatrix],
    ) -> dict[str, any]:
        """Compare multiple competitors' capability overlap.

        Args:
            matrices: List of capability matrices to compare

        Returns:
            Comparison summary with rankings
        """
        if not matrices:
            return {}

        # Sort by overall overlap score
        sorted_matrices = sorted(
            matrices,
            key=lambda m: m.overall_overlap_score,
            reverse=True,
        )

        # Calculate statistics
        scores = [m.overall_overlap_score for m in matrices]
        avg_score = sum(scores) / len(scores)

        # Find top competitor for each capability
        top_by_capability = {}
        capabilities = get_eneve_capabilities()

        for cap in capabilities:
            best_match = None
            best_score = -1

            for matrix in matrices:
                match = matrix.matches.get(cap.code)
                if match:
                    level_scores = {
                        OverlapLevel.NONE: 0,
                        OverlapLevel.LOW: 1,
                        OverlapLevel.MEDIUM: 2,
                        OverlapLevel.HIGH: 3,
                        OverlapLevel.VERY_HIGH: 4,
                    }
                    score = level_scores.get(match.overlap_level, 0) * match.confidence
                    if score > best_score:
                        best_score = score
                        best_match = matrix

            if best_match:
                top_by_capability[cap.name] = best_match.entity_name

        return {
            "rankings": [
                {
                    "rank": i + 1,
                    "entity_name": m.entity_name,
                    "overlap_score": m.overall_overlap_score,
                    "matching_capabilities": m.matching_capabilities,
                }
                for i, m in enumerate(sorted_matrices)
            ],
            "average_overlap": round(avg_score, 2),
            "top_competitor": sorted_matrices[0].entity_name if sorted_matrices else None,
            "top_by_capability": top_by_capability,
            "total_competitors": len(matrices),
        }
