"""AI-Native Assessment Engine for Epic 6."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class AISignalLevel(Enum):
    NATIVE = "native"
    ADOPTED = "adopted"
    EXPERIMENTAL = "experimental"
    ABSENT = "absent"


class AICapabilityType(Enum):
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    OPTIMIZATION = "optimization"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECASTING = "forecasting"
    AUTOMATION = "automation"
    RECOMMENDATION = "recommendation"


@dataclass
class AICapability:
    capability_type: AICapabilityType
    signal_level: AISignalLevel
    confidence: float
    evidence: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)


@dataclass
class AIAssessment:
    company_name: str
    overall_score: float
    signal_level: AISignalLevel

    capabilities: list[AICapability] = field(default_factory=list)

    ai_native_score: float = 0.0
    ai_adoption_score: float = 0.0

    primary_use_cases: list[str] = field(default_factory=list)
    competitive_advantage: str = ""
    ai_maturity_narrative: str = ""

    evidence_quality: str = "low"
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "overall_score": self.overall_score,
            "signal_level": self.signal_level.value,
            "ai_native_score": self.ai_native_score,
            "ai_adoption_score": self.ai_adoption_score,
            "primary_use_cases": self.primary_use_cases,
            "competitive_advantage": self.competitive_advantage,
            "ai_maturity_narrative": self.ai_maturity_narrative,
            "evidence_quality": self.evidence_quality,
            "gaps": self.gaps,
            "recommendations": self.recommendations,
            "capabilities": [
                {
                    "type": c.capability_type.value,
                    "level": c.signal_level.value,
                    "confidence": c.confidence,
                    "evidence": c.evidence[:3],
                    "use_cases": c.use_cases[:3],
                }
                for c in self.capabilities
            ],
        }


AI_NATIVE_SIGNALS = {
    "core": [
        "ai-native",
        "ai first",
        "ai-first",
        "machine learning platform",
        "ml-powered",
        "deep learning platform",
        "neural network",
    ],
    "strong": [
        "predictive analytics",
        "intelligent automation",
        "cognitive computing",
        "ai-powered",
        "ml-driven",
        "algorithmic",
        "autonomous",
    ],
    "moderate": [
        "data-driven",
        "analytics",
        "smart",
        "intelligent",
        "automated",
        "optimization",
        "forecasting",
        "pattern recognition",
    ],
}

CAPABILITY_SIGNALS = {
    AICapabilityType.PREDICTIVE_ANALYTICS: [
        "predictive",
        "prediction",
        "forecast",
        "anticipate",
        "trend analysis",
        "demand forecasting",
        "predictive maintenance",
        "risk prediction",
    ],
    AICapabilityType.NLP: [
        "nlp",
        "natural language",
        "text analysis",
        "sentiment analysis",
        "chatbot",
        "virtual assistant",
        "document processing",
        "text mining",
    ],
    AICapabilityType.COMPUTER_VISION: [
        "computer vision",
        "image recognition",
        "visual inspection",
        "object detection",
        "video analytics",
        "image processing",
        "ocr",
    ],
    AICapabilityType.OPTIMIZATION: [
        "optimization",
        "optimizer",
        "optimal",
        "efficiency",
        "resource allocation",
        "scheduling optimization",
        "load balancing",
    ],
    AICapabilityType.ANOMALY_DETECTION: [
        "anomaly detection",
        "fraud detection",
        "outlier detection",
        "anomaly",
        "unusual pattern",
        "deviation detection",
        "fault detection",
    ],
    AICapabilityType.FORECASTING: [
        "forecasting",
        "time series",
        "trend forecasting",
        "demand prediction",
        "price forecasting",
        "load forecasting",
    ],
    AICapabilityType.AUTOMATION: [
        "automation",
        "automated",
        "intelligent automation",
        "robotic process automation",
        "rpa",
        "self-learning",
        "adaptive",
    ],
    AICapabilityType.RECOMMENDATION: [
        "recommendation",
        "recommender",
        "suggestion",
        "personalization",
        "recommendation engine",
        "next best action",
    ],
}

ENERGY_SPECIFIC_AI = {
    "trading": ["algorithmic trading", "trading bot", "price optimization", "bid optimization"],
    "grid": ["grid optimization", "demand response", "load forecasting", "renewable forecasting"],
    "assets": ["predictive maintenance", "asset optimization", "condition monitoring"],
    "market": ["market forecasting", "price prediction", "market analysis"],
}


class AIAssessmentEngine:
    def __init__(self):
        self.ai_signals = AI_NATIVE_SIGNALS
        self.capability_signals = CAPABILITY_SIGNALS
        self.energy_ai = ENERGY_SPECIFIC_AI

    def analyze(
        self,
        company_name: str,
        company_description: str = "",
        recent_news: list[str] | None = None,
    ) -> AIAssessment:
        all_text = self._combine_text_sources(company_description, recent_news)

        signal_level, signal_confidence = self._assess_signal_level(all_text)

        capabilities = self._detect_capabilities(all_text)

        native_score = self._calculate_native_score(signal_level, capabilities)
        adoption_score = self._calculate_adoption_score(capabilities)

        overall = (native_score * 0.6) + (adoption_score * 0.4)

        assessment = AIAssessment(
            company_name=company_name,
            overall_score=round(overall, 1),
            signal_level=signal_level,
            capabilities=capabilities,
            ai_native_score=round(native_score, 1),
            ai_adoption_score=round(adoption_score, 1),
        )

        assessment.primary_use_cases = self._identify_use_cases(capabilities)
        assessment.competitive_advantage = self._assess_competitive_advantage(assessment)
        assessment.ai_maturity_narrative = self._generate_narrative(assessment)
        assessment.evidence_quality = self._assess_evidence_quality(all_text, capabilities)
        assessment.gaps = self._identify_gaps(capabilities)
        assessment.recommendations = self._generate_recommendations(assessment)

        return assessment

    def _combine_text_sources(
        self,
        description: str,
        news: list[str] | None,
    ) -> str:
        parts = [description.lower()]
        if news:
            parts.extend(n.lower() for n in news if isinstance(n, str))
        return " ".join(parts)

    def _assess_signal_level(self, text: str) -> tuple[AISignalLevel, float]:
        core_count = sum(1 for signal in self.ai_signals["core"] if signal in text)
        strong_count = sum(1 for signal in self.ai_signals["strong"] if signal in text)
        moderate_count = sum(1 for signal in self.ai_signals["moderate"] if signal in text)

        weighted_score = (core_count * 3) + (strong_count * 2) + (moderate_count * 1)

        if core_count >= 2 or weighted_score >= 8:
            return AISignalLevel.NATIVE, min(0.95, 0.7 + (core_count * 0.1))
        elif core_count >= 1 or strong_count >= 3 or weighted_score >= 5:
            return AISignalLevel.ADOPTED, min(0.9, 0.6 + (strong_count * 0.1))
        elif moderate_count >= 2 or weighted_score >= 3:
            return AISignalLevel.EXPERIMENTAL, min(0.8, 0.5 + (moderate_count * 0.1))
        else:
            return AISignalLevel.ABSENT, 0.3

    def _detect_capabilities(self, text: str) -> list[AICapability]:
        capabilities = []

        for cap_type, signals in self.capability_signals.items():
            evidence = []
            for signal in signals:
                if signal in text:
                    sentences = re.split(r"[.!?]+", text)
                    for sentence in sentences:
                        if signal in sentence:
                            evidence.append(sentence.strip()[:150])
                            break

            if evidence:
                confidence = min(0.95, 0.5 + (len(evidence) * 0.15))
                signal_level = self._capability_signal_level(len(evidence))

                use_cases = self._extract_use_cases(text, cap_type)

                capabilities.append(
                    AICapability(
                        capability_type=cap_type,
                        signal_level=signal_level,
                        confidence=round(confidence, 2),
                        evidence=evidence[:5],
                        use_cases=use_cases[:3],
                    )
                )

        return sorted(capabilities, key=lambda x: x.confidence, reverse=True)

    def _capability_signal_level(self, evidence_count: int) -> AISignalLevel:
        if evidence_count >= 4:
            return AISignalLevel.NATIVE
        elif evidence_count >= 2:
            return AISignalLevel.ADOPTED
        elif evidence_count >= 1:
            return AISignalLevel.EXPERIMENTAL
        return AISignalLevel.ABSENT

    def _extract_use_cases(
        self,
        text: str,
        cap_type: AICapabilityType,
    ) -> list[str]:
        use_cases = []

        energy_signals = self.energy_ai.get(cap_type.value, [])

        for signal in energy_signals:
            if signal in text:
                use_cases.append(signal)

        if cap_type == AICapabilityType.FORECASTING:
            use_cases.extend(["demand forecasting", "renewable generation forecasting"])
        elif cap_type == AICapabilityType.OPTIMIZATION:
            use_cases.extend(["energy trading optimization", "asset optimization"])
        elif cap_type == AICapabilityType.PREDICTIVE_ANALYTICS:
            use_cases.extend(["predictive maintenance", "failure prediction"])

        return list(set(use_cases))[:5]

    def _calculate_native_score(
        self,
        signal_level: AISignalLevel,
        capabilities: list[AICapability],
    ) -> float:
        base_scores = {
            AISignalLevel.NATIVE: 9.0,
            AISignalLevel.ADOPTED: 7.0,
            AISignalLevel.EXPERIMENTAL: 4.0,
            AISignalLevel.ABSENT: 1.0,
        }

        base = base_scores.get(signal_level, 1.0)

        native_caps = sum(1 for c in capabilities if c.signal_level == AISignalLevel.NATIVE)
        adopted_caps = sum(1 for c in capabilities if c.signal_level == AISignalLevel.ADOPTED)

        bonus = (native_caps * 0.5) + (adopted_caps * 0.3)

        return min(10.0, base + bonus)

    def _calculate_adoption_score(self, capabilities: list[AICapability]) -> float:
        if not capabilities:
            return 0.0

        total_confidence = sum(c.confidence for c in capabilities)
        avg_confidence = total_confidence / len(capabilities)

        diversity_bonus = min(2.0, len(capabilities) * 0.3)

        score = (avg_confidence * 8) + diversity_bonus
        return min(10.0, score)

    def _identify_use_cases(self, capabilities: list[AICapability]) -> list[str]:
        all_cases = []
        for cap in capabilities:
            all_cases.extend(cap.use_cases)
        return list(set(all_cases))[:5]

    def _assess_competitive_advantage(self, assessment: AIAssessment) -> str:
        if assessment.signal_level == AISignalLevel.NATIVE:
            return (
                "AI-native architecture provides sustainable competitive advantage. "
                "Difficult for legacy competitors to replicate without fundamental redesign."
            )
        elif assessment.signal_level == AISignalLevel.ADOPTED:
            return (
                "Strong AI adoption creates meaningful differentiation. "
                "Competitive moat depends on continued investment and data accumulation."
            )
        elif assessment.signal_level == AISignalLevel.EXPERIMENTAL:
            return (
                "Early-stage AI exploration provides limited competitive advantage. "
                "Vulnerable to disruption by more mature AI competitors."
            )
        else:
            return (
                "Absence of AI capabilities creates competitive disadvantage. "
                "At risk of being displaced by AI-enabled competitors."
            )

    def _generate_narrative(self, assessment: AIAssessment) -> str:
        parts = [
            f"{assessment.company_name} demonstrates {assessment.signal_level.value} "
            f"AI signal with an overall assessment score of {assessment.overall_score}/10."
        ]

        if assessment.capabilities:
            cap_names = [c.capability_type.value.replace("_", " ").title() for c in assessment.capabilities[:3]]
            parts.append(f"Key AI capabilities identified: {', '.join(cap_names)}.")

        if assessment.ai_native_score >= 7:
            parts.append("AI-native foundation suggests architecture built around machine learning from inception.")
        elif assessment.ai_adoption_score >= 6:
            parts.append("Strong AI adoption indicates successful integration of intelligence into operations.")
        elif assessment.overall_score >= 4:
            parts.append("Experimental AI usage suggests early-stage exploration without strategic integration.")
        else:
            parts.append("Limited AI evidence suggests minimal or no artificial intelligence deployment.")

        return " ".join(parts)

    def _assess_evidence_quality(
        self,
        text: str,
        capabilities: list[AICapability],
    ) -> str:
        text_length = len(text)

        if text_length < 100:
            return "insufficient"
        elif len(capabilities) >= 3 and text_length > 500:
            return "high"
        elif len(capabilities) >= 1 and text_length > 200:
            return "medium"
        else:
            return "low"

    def _identify_gaps(self, capabilities: list[AICapability]) -> list[str]:
        all_types = set(AICapabilityType)
        detected = set(c.capability_type for c in capabilities)
        missing = all_types - detected

        gaps = []
        gap_descriptions = {
            AICapabilityType.PREDICTIVE_ANALYTICS: "No predictive analytics capability detected",
            AICapabilityType.NLP: "No natural language processing capability",
            AICapabilityType.COMPUTER_VISION: "No computer vision or image analysis",
            AICapabilityType.OPTIMIZATION: "No optimization algorithms identified",
            AICapabilityType.ANOMALY_DETECTION: "No anomaly detection systems",
            AICapabilityType.FORECASTING: "No forecasting or time-series analysis",
            AICapabilityType.AUTOMATION: "No intelligent automation identified",
            AICapabilityType.RECOMMENDATION: "No recommendation systems detected",
        }

        for gap in missing:
            if gap in gap_descriptions:
                gaps.append(gap_descriptions[gap])

        return gaps[:4]

    def _generate_recommendations(self, assessment: AIAssessment) -> list[str]:
        recs = []

        if assessment.signal_level == AISignalLevel.ABSENT:
            recs.append("Establish AI strategy and identify high-ROI use cases for initial deployment")
            recs.append("Consider partnerships with AI vendors to accelerate capability building")
        elif assessment.signal_level == AISignalLevel.EXPERIMENTAL:
            recs.append("Move from experimental to production AI with dedicated ML engineering resources")
            recs.append("Invest in data infrastructure to support scaled AI deployment")
        elif assessment.signal_level == AISignalLevel.ADOPTED:
            recs.append("Deepen AI integration into core business processes")
            recs.append("Develop proprietary data assets to strengthen competitive moat")
        else:
            recs.append("Maintain AI-native advantage through continued R&D investment")
            recs.append("Explore advanced techniques like reinforcement learning for optimization")

        if len(assessment.capabilities) < 3:
            recs.append("Diversify AI capabilities across multiple domains")

        return recs[:3]
