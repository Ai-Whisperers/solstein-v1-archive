"""Growth vector detector for Epic 2.

Identifies growth vectors: AI/ML, SaaS scaling, geographic expansion, M&A.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .financial_models import GrowthVector, GrowthVectorType

# AI/ML signal keywords
AI_ML_SIGNALS = {
    "strong": [
        "machine learning",
        "deep learning",
        "neural network",
        "ai-native",
        "artificial intelligence platform",
        "predictive analytics",
        "ml-powered",
        "autonomous",
        "computer vision",
        "nlp",
        "natural language processing",
    ],
    "moderate": [
        "ai-powered",
        "artificial intelligence",
        "machine intelligence",
        "cognitive computing",
        "intelligent automation",
        "smart algorithms",
    ],
    "weak": [
        "data-driven",
        "analytics",
        "intelligent",
        "smart",
        "automated",
    ],
}

# SaaS scaling signals
SAAS_SIGNALS = {
    "strong": [
        "cloud-native",
        "saas platform",
        "subscription model",
        "multi-tenant",
        "api-first",
        "platform as a service",
        "paas",
        "saas",
    ],
    "moderate": [
        "cloud-based",
        "web platform",
        "hosted solution",
        "software platform",
        "digital platform",
        "online platform",
    ],
    "weak": [
        "web-based",
        "internet platform",
        "digital solution",
    ],
}

# Geographic expansion signals
GEO_SIGNALS = {
    "strong": [
        "global presence",
        "international expansion",
        "new markets",
        "geographic expansion",
        "regional expansion",
        "market expansion",
        "entered ",
        "expanded to",
        "new country",
        "new region",
    ],
    "moderate": [
        "international",
        "global",
        "worldwide",
        "multi-country",
        "cross-border",
        "overseas",
        "foreign markets",
    ],
}

# M&A signals
MA_SIGNALS = {
    "strong": [
        "acquired ",
        "acquisition of",
        "merger with",
        "merged with",
        "bought ",
        "purchased ",
        "took over",
        "consolidated",
    ],
    "moderate": [
        "acquisition strategy",
        "inorganic growth",
        "buy-and-build",
        "bolt-on acquisition",
        "strategic acquisition",
    ],
}

# Product line expansion signals
PRODUCT_SIGNALS = {
    "strong": [
        "new product line",
        "product expansion",
        "extended offering",
        "new module",
        "new capability",
        "enhanced platform",
    ],
    "moderate": [
        "product development",
        "innovation pipeline",
        "new features",
        "enhanced capabilities",
        "product roadmap",
    ],
}

# Channel expansion signals
CHANNEL_SIGNALS = {
    "strong": [
        "new channel",
        "channel expansion",
        "partner ecosystem",
        "indirect sales",
        "reseller network",
        "distribution network",
    ],
    "moderate": [
        "partnership strategy",
        "channel partners",
        "go-to-market",
        "sales channel",
        "partner program",
    ],
}


@dataclass
class VectorDetectionResult:
    """Result of growth vector detection."""

    vectors: list[GrowthVector] = field(default_factory=list)
    primary_vector: GrowthVectorType | None = None
    confidence_scores: dict[str, float] = field(default_factory=dict)
    summary: str = ""


class GrowthVectorDetector:
    """Detect growth vectors from company data and signals."""

    def __init__(self):
        self.ai_signals = AI_ML_SIGNALS
        self.saas_signals = SAAS_SIGNALS
        self.geo_signals = GEO_SIGNALS
        self.ma_signals = MA_SIGNALS
        self.product_signals = PRODUCT_SIGNALS
        self.channel_signals = CHANNEL_SIGNALS

    def detect(
        self,
        company_description: str = "",
        recent_news: list[str] = None,
        funding_rounds: list[dict] = None,
        employees: int | None = None,
        growth_rate: float | None = None,
        ai_score: float | None = None,
        saas_maturity: float | None = None,
    ) -> VectorDetectionResult:
        """Detect growth vectors from company data.

        Args:
            company_description: Company description text
            recent_news: Recent news headlines/articles
            funding_rounds: Funding round data
            employees: Employee count
            growth_rate: Current growth rate
            ai_score: AI maturity score (0-10)
            saas_maturity: SaaS maturity score (0-10)

        Returns:
            VectorDetectionResult with identified vectors
        """
        vectors = []
        confidence_scores = {}

        # Combine all text sources
        all_text = company_description.lower()
        if recent_news:
            all_text += " " + " ".join(n.lower() for n in recent_news)

        # Detect AI/ML vector
        ai_vector = self._detect_ai_vector(all_text, ai_score)
        if ai_vector.confidence > 0.3:
            vectors.append(ai_vector)
            confidence_scores["ai_ml"] = ai_vector.confidence

        # Detect SaaS scaling vector
        saas_vector = self._detect_saas_vector(all_text, saas_maturity)
        if saas_vector.confidence > 0.3:
            vectors.append(saas_vector)
            confidence_scores["saas_scaling"] = saas_vector.confidence

        # Detect geographic expansion
        geo_vector = self._detect_geo_vector(all_text, funding_rounds)
        if geo_vector.confidence > 0.3:
            vectors.append(geo_vector)
            confidence_scores["geographic_expansion"] = geo_vector.confidence

        # Detect M&A activity
        ma_vector = self._detect_ma_vector(all_text, funding_rounds)
        if ma_vector.confidence > 0.3:
            vectors.append(ma_vector)
            confidence_scores["mergers_acquisitions"] = ma_vector.confidence

        # Detect product line expansion
        product_vector = self._detect_product_vector(all_text)
        if product_vector.confidence > 0.3:
            vectors.append(product_vector)
            confidence_scores["product_line_expansion"] = product_vector.confidence

        # Detect channel expansion
        channel_vector = self._detect_channel_vector(all_text)
        if channel_vector.confidence > 0.3:
            vectors.append(channel_vector)
            confidence_scores["channel_expansion"] = channel_vector.confidence

        # Sort by confidence
        vectors.sort(key=lambda x: x.confidence, reverse=True)

        # Determine primary vector
        primary = vectors[0].vector_type if vectors else None

        # Generate summary
        summary = self._generate_summary(vectors, growth_rate)

        return VectorDetectionResult(
            vectors=vectors,
            primary_vector=primary,
            confidence_scores=confidence_scores,
            summary=summary,
        )

    def _detect_ai_vector(self, text: str, ai_score: float | None) -> GrowthVector:
        """Detect AI/ML growth vector."""
        evidence = []
        confidence = 0.0

        # Check signals
        for signal in self.ai_signals["strong"]:
            if signal in text:
                evidence.append(f"Strong AI signal: '{signal}'")
                confidence += 0.25

        for signal in self.ai_signals["moderate"]:
            if signal in text:
                evidence.append(f"Moderate AI signal: '{signal}'")
                confidence += 0.15

        # Use ai_score if available
        if ai_score is not None:
            if ai_score >= 7:
                evidence.append(f"High AI maturity score: {ai_score}/10")
                confidence += 0.3
            elif ai_score >= 5:
                evidence.append(f"Moderate AI maturity score: {ai_score}/10")
                confidence += 0.15

        # Cap confidence
        confidence = min(0.95, confidence)

        # Determine impact
        impact = "high" if confidence >= 0.7 else "medium" if confidence >= 0.5 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.AI_ML,
            name="AI/ML Capability Expansion",
            confidence=round(confidence, 2),
            evidence=evidence[:5],  # Top 5 evidence items
            estimated_impact=impact,
        )

    def _detect_saas_vector(self, text: str, saas_maturity: float | None) -> GrowthVector:
        """Detect SaaS scaling vector."""
        evidence = []
        confidence = 0.0

        # Check signals
        for signal in self.saas_signals["strong"]:
            if signal in text:
                evidence.append(f"Strong SaaS signal: '{signal}'")
                confidence += 0.25

        for signal in self.saas_signals["moderate"]:
            if signal in text:
                evidence.append(f"Moderate SaaS signal: '{signal}'")
                confidence += 0.15

        # Use saas_maturity if available
        if saas_maturity is not None:
            if saas_maturity >= 7:
                evidence.append(f"High SaaS maturity: {saas_maturity}/10")
                confidence += 0.3
            elif saas_maturity >= 5:
                evidence.append(f"Moderate SaaS maturity: {saas_maturity}/10")
                confidence += 0.15

        # Cap confidence
        confidence = min(0.95, confidence)

        impact = "high" if confidence >= 0.7 else "medium" if confidence >= 0.5 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.SAAS_SCALING,
            name="SaaS Product Scaling",
            confidence=round(confidence, 2),
            evidence=evidence[:5],
            estimated_impact=impact,
        )

    def _detect_geo_vector(self, text: str, funding_rounds: list[dict] | None) -> GrowthVector:
        """Detect geographic expansion vector."""
        evidence = []
        confidence = 0.0

        # Check signals in text
        for signal in self.geo_signals["strong"]:
            if signal in text:
                evidence.append(f"Expansion signal: '{signal}'")
                confidence += 0.25

        for signal in self.geo_signals["moderate"]:
            if signal in text:
                evidence.append(f"Geographic signal: '{signal}'")
                confidence += 0.1

        # Check funding for expansion mentions
        if funding_rounds:
            for round_data in funding_rounds[:3]:  # Check recent rounds
                round_text = str(round_data).lower()
                if any(term in round_text for term in ["expansion", "international", "growth"]):
                    evidence.append("Funding round mentions expansion/growth")
                    confidence += 0.15
                    break

        # Cap confidence
        confidence = min(0.9, confidence)

        impact = "high" if confidence >= 0.7 else "medium" if confidence >= 0.5 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.GEOGRAPHIC_EXPANSION,
            name="Geographic Market Expansion",
            confidence=round(confidence, 2),
            evidence=evidence[:5],
            estimated_impact=impact,
        )

    def _detect_ma_vector(self, text: str, funding_rounds: list[dict] | None) -> GrowthVector:
        """Detect M&A growth vector."""
        evidence = []
        confidence = 0.0

        # Check M&A signals
        for signal in self.ma_signals["strong"]:
            if signal in text:
                evidence.append(f"M&A activity: '{signal}'")
                confidence += 0.3

        for signal in self.ma_signals["moderate"]:
            if signal in text:
                evidence.append(f"M&A strategy: '{signal}'")
                confidence += 0.15

        # Check for acquisition mentions in news/rounds
        acquisition_pattern = re.compile(
            r"(?:acquired|acquisition|bought|purchased)\s+(?:[A-Z][a-zA-Z]+\s+)+", re.IGNORECASE
        )
        if acquisition_pattern.search(text):
            evidence.append("Specific acquisition identified in text")
            confidence += 0.2

        # Cap confidence
        confidence = min(0.95, confidence)

        impact = "high" if confidence >= 0.7 else "medium" if confidence >= 0.5 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.M_A,
            name="Mergers & Acquisitions",
            confidence=round(confidence, 2),
            evidence=evidence[:5],
            estimated_impact=impact,
        )

    def _detect_product_vector(self, text: str) -> GrowthVector:
        """Detect product line expansion vector."""
        evidence = []
        confidence = 0.0

        for signal in self.product_signals["strong"]:
            if signal in text:
                evidence.append(f"Product expansion: '{signal}'")
                confidence += 0.2

        for signal in self.product_signals["moderate"]:
            if signal in text:
                evidence.append(f"Product development: '{signal}'")
                confidence += 0.1

        confidence = min(0.85, confidence)

        impact = "high" if confidence >= 0.6 else "medium" if confidence >= 0.4 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.PRODUCT_LINE,
            name="Product Line Expansion",
            confidence=round(confidence, 2),
            evidence=evidence[:5],
            estimated_impact=impact,
        )

    def _detect_channel_vector(self, text: str) -> GrowthVector:
        """Detect channel expansion vector."""
        evidence = []
        confidence = 0.0

        for signal in self.channel_signals["strong"]:
            if signal in text:
                evidence.append(f"Channel expansion: '{signal}'")
                confidence += 0.2

        for signal in self.channel_signals["moderate"]:
            if signal in text:
                evidence.append(f"Channel strategy: '{signal}'")
                confidence += 0.1

        confidence = min(0.8, confidence)

        impact = "high" if confidence >= 0.6 else "medium" if confidence >= 0.4 else "low"

        return GrowthVector(
            vector_type=GrowthVectorType.CHANNEL,
            name="Channel & Partnership Expansion",
            confidence=round(confidence, 2),
            evidence=evidence[:5],
            estimated_impact=impact,
        )

    def _generate_summary(self, vectors: list[GrowthVector], growth_rate: float | None) -> str:
        """Generate summary of growth vectors."""
        if not vectors:
            return "No clear growth vectors identified from available data."

        parts = []

        # Primary vector
        primary = vectors[0]
        parts.append(
            f"Primary growth driver: {primary.name} "
            f"(confidence: {primary.confidence:.0%}, impact: {primary.estimated_impact})."
        )

        # Additional vectors
        if len(vectors) > 1:
            secondary = [v.name for v in vectors[1:3]]
            parts.append(f"Secondary vectors: {', '.join(secondary)}.")

        # Growth rate context
        if growth_rate is not None:
            if growth_rate >= 50:
                parts.append(f"Exceptional growth rate of {growth_rate}% supports aggressive expansion strategy.")
            elif growth_rate >= 20:
                parts.append(f"Strong growth rate of {growth_rate}% indicates healthy market traction.")
            elif growth_rate >= 10:
                parts.append(f"Steady growth rate of {growth_rate}% suggests sustainable expansion.")
            else:
                parts.append(f"Modest growth rate of {growth_rate}% - focus on core markets likely.")

        return " ".join(parts)
