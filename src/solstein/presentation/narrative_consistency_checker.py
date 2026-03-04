"""
Task 15: Fix Contradictory Narrative Generation

Validates report narratives for contradictions and ensures consistency
between data, classification, and narrative tone.
"""

from solstein.domain.models import AIMaturity, Company


class NarrativeConsistencyChecker:
    """Validate report narratives for contradictions and consistency."""

    # AI maturity to score mapping (expected ranges)
    AI_MATURITY_SCORE_RANGES = {
        AIMaturity.NONE: (0, 2),  # None: 0-2
        AIMaturity.LOW: (2, 4),  # Low: 2-4
        AIMaturity.MODERATE: (4, 6),  # Moderate: 4-6
        AIMaturity.STRONG: (6, 8),  # Strong: 6-8
        AIMaturity.VERY_STRONG: (8, 10),  # Very Strong: 8-10
    }

    # Classification to score mapping
    CLASSIFICATION_SCORE_RANGES = {
        "Phoenix": (7.0, 10.0),  # High-growth: 7.0+
        "Salt": (4.0, 7.0),  # Stable: 4.0-7.0
        "Lead": (0.0, 4.0),  # Legacy: <4.0
    }

    # Classification to narrative tone
    CLASSIFICATION_TONE = {
        "Phoenix": ["high-growth", "exceptional", "strong", "rapid", "leading"],
        "Salt": ["stable", "mature", "consistent", "established", "solid"],
        "Lead": ["legacy", "transformation", "modernization", "opportunity", "potential"],
    }

    @staticmethod
    def check_ai_consistency(company: Company) -> list[str]:
        """Check for AI maturity and score contradictions."""
        contradictions = []

        if company.ai_maturity is None or company.ai_score is None:
            return contradictions

        # Get expected range for this maturity level
        maturity_enum = None
        for enum_val in AIMaturity:
            if enum_val.value == company.ai_maturity:
                maturity_enum = enum_val
                break

        if maturity_enum is None:
            return contradictions

        expected_min, expected_max = NarrativeConsistencyChecker.AI_MATURITY_SCORE_RANGES[maturity_enum]

        # Check if score is within expected range
        if not (expected_min <= company.ai_score <= expected_max):
            contradictions.append(
                f"AI Contradiction: Maturity is '{company.ai_maturity}' (expected score {expected_min}-{expected_max}) "
                f"but AI score is {company.ai_score}/10"
            )

        return contradictions

    @staticmethod
    def check_classification_consistency(company: Company) -> list[str]:
        """Check for classification and score contradictions."""
        contradictions = []

        if company.classification is None or company.composite_score is None:
            return contradictions

        # Get expected range for this classification
        if company.classification not in NarrativeConsistencyChecker.CLASSIFICATION_SCORE_RANGES:
            return contradictions

        expected_min, expected_max = NarrativeConsistencyChecker.CLASSIFICATION_SCORE_RANGES[company.classification]

        # Check if score is within expected range
        if not (expected_min <= company.composite_score < expected_max):
            contradictions.append(
                f"Classification Contradiction: Classification is '{company.classification}' "
                f"(expected score {expected_min}-{expected_max}) but composite score is {company.composite_score}"
            )

        return contradictions

    @staticmethod
    def check_narrative_tone_consistency(company: Company, narrative: str) -> list[str]:
        """Check if narrative tone matches classification."""
        contradictions = []

        if company.classification is None or not narrative:
            return contradictions

        # Get expected tone words for this classification
        expected_tones = NarrativeConsistencyChecker.CLASSIFICATION_TONE.get(company.classification, [])
        narrative_lower = narrative.lower()

        # Check if any expected tone words appear in narrative
        has_expected_tone = any(tone in narrative_lower for tone in expected_tones)

        if not has_expected_tone:
            contradictions.append(
                f"Narrative Tone Mismatch: Classification is '{company.classification}' "
                f"(expected tone: {', '.join(expected_tones)}) but narrative doesn't reflect this"
            )

        # Check for contradictory tones
        # Check for contradictory tones
        phoenix_tones = NarrativeConsistencyChecker.CLASSIFICATION_TONE["Phoenix"]

        if company.classification == "Salt":
            # Salt should not have Phoenix-level praise
            phoenix_count = sum(1 for tone in phoenix_tones if tone in narrative_lower)
            if phoenix_count >= 2:
                contradictions.append(
                    "Narrative Contradiction: Classification is 'Salt' (stable) "
                    "but narrative uses Phoenix-level language (high-growth, exceptional, etc.)"
                )

        elif company.classification == "Lead":
            # Lead should not have Phoenix-level praise
            phoenix_count = sum(1 for tone in phoenix_tones if tone in narrative_lower)
            if phoenix_count >= 2:
                contradictions.append(
                    "Narrative Contradiction: Classification is 'Lead' (legacy) "
                    "but narrative uses Phoenix-level language (high-growth, exceptional, etc.)"
                )

        return contradictions

    @staticmethod
    def check_all_contradictions(company: Company, narrative: str | None = None) -> list[str]:
        """Check all types of contradictions."""
        all_contradictions = []

        # Check AI consistency
        all_contradictions.extend(NarrativeConsistencyChecker.check_ai_consistency(company))

        # Check classification consistency
        all_contradictions.extend(NarrativeConsistencyChecker.check_classification_consistency(company))

        # Check narrative tone consistency
        if narrative:
            all_contradictions.extend(NarrativeConsistencyChecker.check_narrative_tone_consistency(company, narrative))

        return all_contradictions

    @staticmethod
    def is_consistent(company: Company, narrative: str | None = None) -> bool:
        """Check if company data and narrative are consistent."""
        contradictions = NarrativeConsistencyChecker.check_all_contradictions(company, narrative)
        return len(contradictions) == 0

    @staticmethod
    def get_consistency_report(company: Company, narrative: str | None = None) -> str:
        """Generate a consistency report for a company."""
        contradictions = NarrativeConsistencyChecker.check_all_contradictions(company, narrative)

        if not contradictions:
            return f"✓ {company.name}: All narratives are consistent with data"

        report = f"✗ {company.name}: Found {len(contradictions)} contradiction(s):\n"
        for i, contradiction in enumerate(contradictions, 1):
            report += f"  {i}. {contradiction}\n"

        return report

    @staticmethod
    def validate_ai_maturity_score_alignment(company: Company) -> bool:
        """Validate that AI maturity and score are aligned."""
        if company.ai_maturity is None or company.ai_score is None:
            return True  # No contradiction if either is missing

        # Get expected range
        maturity_enum = None
        for enum_val in AIMaturity:
            if enum_val.value == company.ai_maturity:
                maturity_enum = enum_val
                break

        if maturity_enum is None:
            return False  # Invalid maturity value

        expected_min, expected_max = NarrativeConsistencyChecker.AI_MATURITY_SCORE_RANGES[maturity_enum]
        return expected_min <= company.ai_score <= expected_max

    @staticmethod
    def validate_classification_score_alignment(company: Company) -> bool:
        """Validate that classification and score are aligned."""
        if company.classification is None or company.composite_score is None:
            return True  # No contradiction if either is missing

        if company.classification not in NarrativeConsistencyChecker.CLASSIFICATION_SCORE_RANGES:
            return False  # Invalid classification

        expected_min, expected_max = NarrativeConsistencyChecker.CLASSIFICATION_SCORE_RANGES[company.classification]
        return expected_min <= company.composite_score < expected_max

    @staticmethod
    def fix_ai_score_for_maturity(company: Company) -> int | None:
        """Suggest a corrected AI score based on maturity level."""
        if company.ai_maturity is None:
            return None

        # Get expected range
        maturity_enum = None
        for enum_val in AIMaturity:
            if enum_val.value == company.ai_maturity:
                maturity_enum = enum_val
                break

        if maturity_enum is None:
            return None

        expected_min, expected_max = NarrativeConsistencyChecker.AI_MATURITY_SCORE_RANGES[maturity_enum]

        # Return midpoint of expected range
        return int((expected_min + expected_max) / 2)

    @staticmethod
    def fix_classification_for_score(company: Company) -> str | None:
        """Suggest a corrected classification based on score."""
        if company.composite_score is None:
            return None

        score = company.composite_score

        # Determine classification based on score
        if score >= 7.0:
            return "Phoenix"
        elif score >= 4.0:
            return "Salt"
        else:
            return "Lead"
