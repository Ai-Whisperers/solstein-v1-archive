from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IdentifierCandidate:
    value: str
    confidence: float
    source: str


@dataclass(frozen=True)
class LookupResult:
    ticker: str | None
    company_number: str | None
    geography: str | None
    confidence: float
    accepted: bool
    rejection_reason: str | None


class IdentifierLookupService:
    def __init__(self, min_confidence: float = 0.75):
        self.min_confidence: float = min_confidence
        self._cache: dict[str, LookupResult] = {}
        self._authoritative_tickers: dict[str, IdentifierCandidate] = {
            "apple": IdentifierCandidate("AAPL", 0.98, "authoritative-map"),
            "microsoft": IdentifierCandidate("MSFT", 0.98, "authoritative-map"),
            "alphabet": IdentifierCandidate("GOOGL", 0.98, "authoritative-map"),
            "google": IdentifierCandidate("GOOGL", 0.98, "authoritative-map"),
            "amazon": IdentifierCandidate("AMZN", 0.98, "authoritative-map"),
            "meta": IdentifierCandidate("META", 0.98, "authoritative-map"),
            "nvidia": IdentifierCandidate("NVDA", 0.98, "authoritative-map"),
            "tesla": IdentifierCandidate("TSLA", 0.98, "authoritative-map"),
        }
        self._authoritative_company_numbers: dict[str, IdentifierCandidate] = {
            "shell": IdentifierCandidate("04366849", 0.96, "companies-house-map"),
            "bp": IdentifierCandidate("00102498", 0.96, "companies-house-map"),
        }

    def _normalize_name(self, company_name: str) -> str:
        cleaned = re.sub(r"[^a-z0-9\s]", " ", company_name.lower())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        suffixes = {"inc", "corp", "corporation", "ltd", "limited", "plc", "llc", "ag", "sa"}
        tokens = [token for token in cleaned.split(" ") if token and token not in suffixes]
        return " ".join(tokens)

    def _token_confidence_match(self, normalized_name: str, catalog_key: str) -> float:
        if normalized_name == catalog_key:
            return 0.98
        normalized_tokens = set(normalized_name.split())
        key_tokens = set(catalog_key.split())
        if not key_tokens:
            return 0.0
        overlap = len(normalized_tokens.intersection(key_tokens)) / len(key_tokens)
        if overlap >= 1.0:
            return 0.9
        if overlap >= 0.75:
            return 0.78
        return 0.0

    def _lookup_from_catalog(
        self, normalized_name: str, catalog: dict[str, IdentifierCandidate]
    ) -> IdentifierCandidate | None:
        best: IdentifierCandidate | None = None
        best_score = 0.0
        for key, candidate in catalog.items():
            score = self._token_confidence_match(normalized_name, key)
            if score <= 0:
                continue
            effective_confidence = min(candidate.confidence, score)
            if effective_confidence > best_score:
                best_score = effective_confidence
                best = IdentifierCandidate(candidate.value, effective_confidence, candidate.source)
        return best

    def _infer_geography(self, company_name: str, headquarters: str | None) -> str | None:
        text = f"{company_name} {headquarters or ''}".lower()
        if any(token in text for token in {"united states", "usa", "us", "california", "new york"}):
            return "US"
        if any(token in text for token in {"united kingdom", "uk", "england", "london", "scotland"}):
            return "UK"
        if any(token in text for token in {"germany", "france", "spain", "netherlands", "europe"}):
            return "EU"
        return None

    def resolve_identifiers(self, company_name: str, headquarters: str | None = None) -> LookupResult:
        cache_key = f"{company_name}|{headquarters or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        normalized_name = self._normalize_name(company_name)
        ticker_candidate = self._lookup_from_catalog(normalized_name, self._authoritative_tickers)
        company_number_candidate = self._lookup_from_catalog(normalized_name, self._authoritative_company_numbers)

        confidence_candidates = [
            candidate.confidence for candidate in (ticker_candidate, company_number_candidate) if candidate is not None
        ]
        aggregate_confidence = max(confidence_candidates) if confidence_candidates else 0.0
        accepted = aggregate_confidence >= self.min_confidence
        rejection_reason = None
        if not accepted:
            rejection_reason = "identifier confidence below threshold"

        result = LookupResult(
            ticker=ticker_candidate.value if accepted and ticker_candidate else None,
            company_number=company_number_candidate.value if accepted and company_number_candidate else None,
            geography=self._infer_geography(company_name, headquarters),
            confidence=aggregate_confidence,
            accepted=accepted,
            rejection_reason=rejection_reason,
        )
        self._cache[cache_key] = result
        return result

    def lookup_ticker(self, company_name: str) -> str | None:
        return self.resolve_identifiers(company_name).ticker

    def lookup_company_number(self, company_name: str) -> str | None:
        return self.resolve_identifiers(company_name).company_number

    def infer_geography(self, company_name: str, headquarters: str | None = None) -> str | None:
        return self.resolve_identifiers(company_name, headquarters=headquarters).geography
