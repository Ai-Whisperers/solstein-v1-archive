"""Corporate genealogy analyzer for Epic 3."""

from __future__ import annotations

import re
from datetime import date

from .genealogy_models import (
    CorporateGenealogy,
    CorporateTransaction,
    OwnershipStake,
    SubsidiaryInfo,
    TransactionType,
)

ACQUISITION_SIGNALS = [
    "acquired",
    "acquisition of",
    "bought",
    "purchased",
    "took over",
    "acquires",
    "acquiring",
    "bought out",
    "acquisition",
]

MERGER_SIGNALS = [
    "merged with",
    "merger with",
    "merging with",
    "merger",
    "merges with",
]

DIVESTITURE_SIGNALS = [
    "divested",
    "divestiture",
    "sold",
    "sale of",
    "spin off",
    "spun off",
    "disposed of",
    "divests",
]

SUBSIDIARY_SIGNALS = [
    "subsidiary",
    "subsidiaries",
    "formed",
    "established",
    "founded subsidiary",
]

JOINT_VENTURE_SIGNALS = [
    "joint venture",
    "jv with",
    "partnership with",
    "strategic alliance",
]

OWNERSHIP_SIGNALS = [
    "stake",
    "ownership",
    "acquired stake",
    "bought stake",
    "shareholder",
    "owned by",
    "parent company",
    "parent of",
    "majority stake",
    "minority stake",
]

STRATEGIC_INVESTORS = {
    "shell",
    "bp",
    "total",
    "equinor",
    "eni",
    "enel",
    "edf",
    "eon",
    "rwe",
    "iberdrola",
    "national grid",
    "engie",
    "suez",
    "veolia",
    "siemens",
    "ge",  # General Electric - short but kept for explicit mentions
    "abb",
    "schneider",
    "honeywell",
    "emerson",
    "rockwell",
    "johnson controls",
    "danfoss",
    "vestas",
    "siemens gamesa",
}
ENERGY_UTILITIES = {
    "rwe",
    "eon",
    "enbw",
    "vattenfall",
    "edf",
    "enel",
    "iberdrola",
    "national grid",
    "centrica",
    "sse",
    "scottish power",
    "drax",
    "fortum",
    "statkraft",
    "agder energi",
    "lyse",
}


class GenealogyAnalyzer:
    def __init__(self):
        self.acquisition_signals = ACQUISITION_SIGNALS
        self.merger_signals = MERGER_SIGNALS
        self.divestiture_signals = DIVESTITURE_SIGNALS
        self.subsidiary_signals = SUBSIDIARY_SIGNALS
        self.jv_signals = JOINT_VENTURE_SIGNALS
        self.ownership_signals = OWNERSHIP_SIGNALS
        self.strategic_investors = STRATEGIC_INVESTORS
        self.energy_utilities = ENERGY_UTILITIES

    def analyze(
        self,
        company_name: str,
        company_description: str = "",
        recent_news: list[str] | None = None,
        competitors: list[dict] | None = None,
    ) -> CorporateGenealogy:
        genealogy = CorporateGenealogy(company_name=company_name)

        all_text = self._combine_text_sources(company_description, recent_news)

        transactions = self._detect_transactions(all_text, company_name)
        genealogy.transactions = transactions

        ownership = self._detect_ownership(all_text, company_name)
        genealogy.ownership_history = ownership

        subsidiaries = self._detect_subsidiaries(all_text, company_name)
        genealogy.subsidiaries = subsidiaries

        genealogy = self._calculate_metrics(genealogy)
        genealogy = self._determine_ownership_type(genealogy)
        genealogy = self._generate_narrative(genealogy)
        genealogy = self._identify_integration_risks(genealogy)

        return genealogy

    def _combine_text_sources(
        self,
        description: str,
        news: list[str] | None,
    ) -> str:
        parts = [description.lower()]
        if news:
            parts.extend(n.lower() for n in news if isinstance(n, str))
        return " ".join(parts)

    def _detect_transactions(
        self,
        text: str,
        company_name: str,
    ) -> list[CorporateTransaction]:
        transactions = []
        sentences = re.split(r"[.!?]+", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            trans_type = self._classify_transaction_type(sentence)
            if not trans_type:
                continue

            trans_date = self._extract_date(sentence)
            target, acquirer = self._extract_parties(sentence, company_name, trans_type)
            value = self._extract_value(sentence)

            transactions.append(
                CorporateTransaction(
                    transaction_type=trans_type,
                    date=trans_date,
                    target_name=target or "Unknown",
                    acquirer_name=acquirer,
                    value_eur_millions=value,
                    description=sentence[:200],
                )
            )

        return self._deduplicate_transactions(transactions)

    def _classify_transaction_type(self, text: str) -> TransactionType | None:
        text_lower = text.lower()

        for signal in self.acquisition_signals:
            if signal in text_lower:
                return TransactionType.ACQUISITION

        for signal in self.merger_signals:
            if signal in text_lower:
                return TransactionType.MERGER

        for signal in self.divestiture_signals:
            if signal in text_lower:
                return TransactionType.DIVESTITURE

        for signal in self.jv_signals:
            if signal in text_lower:
                return TransactionType.JOINT_VENTURE

        return None

    def _extract_date(self, text: str) -> date | None:
        year_patterns = [
            r"\b(20\d{2})\b",
            r"\b(19\d{2})\b",
        ]

        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                year = int(match.group(1))
                if 1990 <= year <= 2030:
                    return date(year, 1, 1)

        return None

    def _extract_parties(
        self,
        text: str,
        company_name: str,
        trans_type: TransactionType,
    ) -> tuple[str | None, str | None]:
        target = None
        acquirer = None

        acquisition_patterns = [
            rf"{company_name.lower()} acquired ([A-Za-z][A-Za-z\s]+?)(?:\s+(?:for|in|\.))",
            rf"([A-Za-z][A-Za-z\s]+?) acquired by {company_name.lower()}",
            rf"{company_name.lower()} buys ([A-Za-z][A-Za-z\s]+?)(?:\s+(?:for|in|\.))",
        ]

        for pattern in acquisition_patterns:
            match = re.search(pattern, text.lower())
            if match:
                other_party = match.group(1).strip().title()
                if trans_type == TransactionType.ACQUISITION:
                    target = other_party
                    acquirer = company_name
                break

        if not target and not acquirer:
            words = text.split()
            for i, word in enumerate(words):
                if word.lower() in ["acquired", "bought", "purchased"]:
                    if i + 1 < len(words):
                        potential_target = words[i + 1 : i + 4]
                        target = " ".join(potential_target).title()
                        acquirer = company_name
                        break

        return target, acquirer

    def _extract_value(self, text: str) -> float | None:
        value_patterns = [
            r"€(\d+(?:\.\d+)?)\s*million",
            r"€(\d+(?:\.\d+)?)\s*mn",
            r"eur\s*(\d+(?:\.\d+)?)\s*million",
            r"\$(\d+(?:\.\d+)?)\s*million",
            r"(\d+(?:\.\d+)?)\s*million\s*(?:euros?|eur)",
        ]

        for pattern in value_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))

        return None

    def _deduplicate_transactions(
        self,
        transactions: list[CorporateTransaction],
    ) -> list[CorporateTransaction]:
        seen = set()
        unique = []

        for t in transactions:
            key = (t.transaction_type.value, t.target_name.lower(), t.date)
            if key not in seen:
                seen.add(key)
                unique.append(t)

        return sorted(unique, key=lambda x: x.date or date.min, reverse=True)

    def _detect_ownership(
        self,
        text: str,
        company_name: str,
    ) -> list[OwnershipStake]:
        stakes = []
        text_lower = text.lower()

        for investor in self.strategic_investors:
            # Use word boundary matching to avoid false positives
            # e.g., 'ge' should not match inside 'management' or 'energy'
            pattern = rf'\b{re.escape(investor.lower())}\b'
            if re.search(pattern, text_lower):
                percentage = self._extract_ownership_percentage(text, investor)
                stakes.append(
                    OwnershipStake(
                        owner_name=investor.title(),
                        percentage=percentage,
                        acquisition_date=None,
                    )
                )

        for utility in self.energy_utilities:
            pattern = rf'\b{re.escape(utility.lower())}\b'
            if re.search(pattern, text_lower) and utility not in [s.owner_name.lower() for s in stakes]:
                percentage = self._extract_ownership_percentage(text, utility)
                stakes.append(
                    OwnershipStake(
                        owner_name=utility.title(),
                        percentage=percentage,
                        acquisition_date=None,
                    )
                )
        parent_pattern = r"(?:subsidiary|owned|part)\s+of\s+([A-Za-z][A-Za-z\s]+?)(?:\.|,|\s)"
        match = re.search(parent_pattern, text.lower())
        if match:
            parent = match.group(1).strip().title()
            if parent.lower() != company_name.lower():
                stakes.append(
                    OwnershipStake(
                        owner_name=parent,
                        percentage=None,
                        acquisition_date=None,
                    )
                )

        return stakes

    def _extract_ownership_percentage(
        self,
        text: str,
        owner: str,
    ) -> float | None:
        owner_pos = text.lower().find(owner)
        if owner_pos == -1:
            return None

        surrounding_text = text[max(0, owner_pos - 100) : min(len(text), owner_pos + 100)]

        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%", surrounding_text)
        if percent_match:
            return float(percent_match.group(1))

        majority_patterns = ["majority stake", "majority interest", "controlling stake"]
        for pattern in majority_patterns:
            if pattern in surrounding_text.lower():
                return 51.0

        minority_patterns = ["minority stake", "minority interest"]
        for pattern in minority_patterns:
            if pattern in surrounding_text.lower():
                return 25.0

        return None

    def _detect_subsidiaries(
        self,
        text: str,
        company_name: str,
    ) -> list[SubsidiaryInfo]:
        subsidiaries = []

        patterns = [
            rf"{company_name.lower()}.*?subsidiary\s+([A-Za-z][A-Za-z\s]+?)(?:\.|,|\s)",
            rf"([A-Za-z][A-Za-z\s]+?),?\s+a\s+subsidiary\s+of\s+{company_name.lower()}",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text.lower()):
                name = match.group(1).strip().title()
                if len(name) > 2 and name.lower() != company_name.lower():
                    subsidiaries.append(
                        SubsidiaryInfo(
                            name=name,
                            relationship_type="subsidiary",
                            formation_date=None,
                        )
                    )

        return subsidiaries[:10]

    def _calculate_metrics(self, genealogy: CorporateGenealogy) -> CorporateGenealogy:
        genealogy.acquisition_count = sum(
            1 for t in genealogy.transactions if t.transaction_type == TransactionType.ACQUISITION
        )
        genealogy.divestiture_count = sum(
            1 for t in genealogy.transactions if t.transaction_type == TransactionType.DIVESTITURE
        )
        genealogy.merger_count = sum(1 for t in genealogy.transactions if t.transaction_type == TransactionType.MERGER)

        acquisition_values = [
            t.value_eur_millions
            for t in genealogy.transactions
            if t.transaction_type == TransactionType.ACQUISITION and t.value_eur_millions
        ]
        if acquisition_values:
            genealogy.total_acquisition_value = sum(acquisition_values)

        divestiture_values = [
            t.value_eur_millions
            for t in genealogy.transactions
            if t.transaction_type == TransactionType.DIVESTITURE and t.value_eur_millions
        ]
        if divestiture_values:
            genealogy.total_divestiture_value = sum(divestiture_values)

        current_stakes = [s for s in genealogy.ownership_history if s.current]
        if current_stakes:
            genealogy.current_owner = current_stakes[0].owner_name

        return genealogy

    def _determine_ownership_type(self, genealogy: CorporateGenealogy) -> CorporateGenealogy:
        if genealogy.current_owner:
            owner_lower = genealogy.current_owner.lower()

            if any(util in owner_lower for util in self.energy_utilities):
                genealogy.ownership_type = "utility_subsidiary"
            elif any(inv in owner_lower for inv in self.strategic_investors):
                genealogy.ownership_type = "strategic_subsidiary"
            else:
                genealogy.ownership_type = "corporate_subsidiary"
        elif genealogy.acquisition_count > 0:
            genealogy.ownership_type = "acquisitive_independent"
        else:
            genealogy.ownership_type = "independent"

        return genealogy

    def _generate_narrative(self, genealogy: CorporateGenealogy) -> CorporateGenealogy:
        parts = []

        if genealogy.current_owner:
            parts.append(
                f"{genealogy.company_name} is a {genealogy.ownership_type.replace('_', ' ')} "
                f"owned by {genealogy.current_owner}."
            )
        else:
            parts.append(f"{genealogy.company_name} operates as an independent entity.")

        if genealogy.acquisition_count > 0:
            acq_text = f"has completed {genealogy.acquisition_count} acquisition"
            if genealogy.acquisition_count > 1:
                acq_text += "s"
            if genealogy.total_acquisition_value:
                acq_text += f" totaling €{genealogy.total_acquisition_value:.1f}M"
            parts.append(acq_text)

        if genealogy.merger_count > 0:
            parts.append(f"participated in {genealogy.merger_count} merger")

        if genealogy.divestiture_count > 0:
            parts.append(f"executed {genealogy.divestiture_count} divestiture")

        if genealogy.subsidiaries:
            parts.append(f"operates {len(genealogy.subsidiaries)} subsidiary entities")

        genealogy.genealogy_narrative = " ".join(parts) + "."

        implications = []
        if genealogy.ownership_type == "utility_subsidiary":
            implications.append(
                "Utility ownership provides access to customer base and regulatory expertise "
                "but may limit strategic flexibility."
            )
        elif genealogy.ownership_type == "strategic_subsidiary":
            implications.append(
                "Strategic corporate ownership suggests technology integration synergies "
                "and potential preferential market access."
            )
        elif genealogy.acquisition_count >= 3:
            implications.append(
                "Active M&A history indicates growth-through-acquisition strategy. "
                "Integration capabilities should be assessed."
            )
        elif genealogy.acquisition_count == 0 and genealogy.divestiture_count == 0:
            implications.append(
                "No significant M&A activity suggests organic growth focus or "
                "limited strategic flexibility for inorganic expansion."
            )

        genealogy.strategic_implications = " ".join(implications)

        return genealogy

    def _identify_integration_risks(self, genealogy: CorporateGenealogy) -> CorporateGenealogy:
        risks = []

        if genealogy.ownership_type == "utility_subsidiary":
            risks.append("Parent utility priorities may override subsidiary commercial strategy")
            risks.append("Regulatory constraints from parent may limit market expansion")

        if genealogy.acquisition_count >= 3 and not genealogy.total_acquisition_value:
            risks.append("Multiple acquisitions with undisclosed values - integration success unclear")

        if genealogy.merger_count > 0:
            risks.append("Post-merger integration challenges may persist")

        if len(genealogy.subsidiaries) > 5:
            risks.append("Complex subsidiary structure may create governance challenges")

        if genealogy.divestiture_count > genealogy.acquisition_count:
            risks.append("More divestitures than acquisitions suggests portfolio rationalization")

        if not genealogy.current_owner and genealogy.acquisition_count == 0:
            risks.append("Standalone position without strategic backing may limit growth capital")

        genealogy.integration_risks = risks[:5]
        return genealogy
