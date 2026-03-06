import json
import importlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from loguru import logger


class IdentifierLookupService:
    def __init__(self, cache_path: Path | None = None) -> None:
        self.cache_path = cache_path or Path("data/output/identifier_cache.json")
        self._ddg_available = False
        self._ddg_client: Any = None
        self._openfigi_available = False
        self._openfigi_api_key = os.getenv("OPENFIGI_API_KEY")
        self._opencorporates_api_key = os.getenv("OPENCORPORATES_API_KEY")
        self._cache: dict[str, dict[str, Any]] = {}

        self._load_cache()

        try:
            ddgs_module = importlib.import_module("ddgs")
            self._ddg_client = getattr(ddgs_module, "DDGS")
            self._ddg_available = True
        except Exception:
            try:
                ddgs_module = importlib.import_module("duckduckgo_search")
                self._ddg_client = getattr(ddgs_module, "DDGS")
                self._ddg_available = True
            except Exception as exc:
                logger.warning("DDG search client unavailable", error=str(exc))

        try:
            import requests as _requests  # noqa: F401

            self._openfigi_available = bool(self._openfigi_api_key)
        except Exception as exc:
            logger.warning("requests unavailable for OpenFIGI", error=str(exc))

    async def _search_opencorporates(self, company_name: str) -> dict[str, Any]:
        if not self._opencorporates_api_key:
            return {}

        import requests

        params = {
            "q": company_name,
            "api_token": self._opencorporates_api_key,
            "per_page": 3,
        }
        try:
            response = requests.get(
                "https://api.opencorporates.com/v0.4/companies/search",
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("OpenCorporates lookup failed", company=company_name, error=str(exc))
            return {}

        companies_block = payload.get("results", {}).get("companies", []) if isinstance(payload, dict) else []
        if not companies_block:
            return {}

        first = companies_block[0]
        company_data = first.get("company", {}) if isinstance(first, dict) else {}
        company_number = company_data.get("company_number")
        jurisdiction = company_data.get("jurisdiction_code")
        legal_name = company_data.get("name")

        if not isinstance(company_number, str) or not company_number:
            return {}

        return {
            "company_number": company_number,
            "jurisdiction": jurisdiction if isinstance(jurisdiction, str) else None,
            "legal_name": legal_name if isinstance(legal_name, str) else None,
            "opencorporates_confidence": 0.9,
            "opencorporates_source": "opencorporates",
        }

    def _cache_opencorporates_result(self, key: str, result: dict[str, Any]) -> None:
        record: dict[str, Any] = {}
        company_number = result.get("company_number")
        if isinstance(company_number, str) and company_number:
            record["company_number"] = company_number
            record["company_number_confidence"] = result.get("opencorporates_confidence", 0.9)
            record["company_number_source"] = result.get("opencorporates_source", "opencorporates")
        jurisdiction = result.get("jurisdiction")
        if isinstance(jurisdiction, str) and jurisdiction:
            record["opencorporates_jurisdiction"] = jurisdiction
        legal_name = result.get("legal_name")
        if isinstance(legal_name, str) and legal_name:
            record["opencorporates_legal_name"] = legal_name

        if record:
            self._set_cached_record(key, record)

    async def _search_openfigi(self, company_name: str) -> dict[str, Any]:
        if not self._openfigi_available:
            return {}

        import requests

        headers = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": str(self._openfigi_api_key),
        }
        payload = {"query": company_name}

        try:
            response = requests.post(
                "https://api.openfigi.com/v3/search",
                headers=headers,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.warning("OpenFIGI lookup failed", company=company_name, error=str(exc))
            return {}

        if not isinstance(data, list) or not data:
            return {}
        first = data[0]
        if not isinstance(first, dict):
            return {}

        ticker = first.get("ticker")
        exch_code = first.get("exchCode")
        security_desc = first.get("securityDescription")

        inferred_company_number = None
        if isinstance(security_desc, str):
            company_match = re.search(r"\b([0-9]{6,8})\b", security_desc)
            if company_match:
                inferred_company_number = company_match.group(1)

        return {
            "ticker": ticker if isinstance(ticker, str) and ticker else None,
            "company_number": inferred_company_number,
            "isin": first.get("securityID") if isinstance(first.get("securityID"), str) else None,
            "exchange": exch_code if isinstance(exch_code, str) else None,
            "openfigi_confidence": 0.92,
            "openfigi_source": "openfigi",
        }

    def _cache_openfigi_result(self, key: str, result: dict[str, Any]) -> None:
        record: dict[str, Any] = {}
        if isinstance(result.get("ticker"), str):
            record["ticker"] = result["ticker"]
            record["ticker_confidence"] = result.get("openfigi_confidence", 0.92)
            record["ticker_source"] = result.get("openfigi_source", "openfigi")
        if isinstance(result.get("company_number"), str):
            record["company_number"] = result["company_number"]
            record["company_number_confidence"] = result.get("openfigi_confidence", 0.92)
            record["company_number_source"] = result.get("openfigi_source", "openfigi")
        if isinstance(result.get("isin"), str) and re.match(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$", result["isin"]):
            record["isin"] = result["isin"]
            record["isin_confidence"] = result.get("openfigi_confidence", 0.92)
            record["isin_source"] = result.get("openfigi_source", "openfigi")

        if record:
            self._set_cached_record(key, record)

    def _normalize_key(self, company_name: str) -> str:
        return re.sub(r"\s+", " ", company_name.strip().lower())

    def _load_cache(self) -> None:
        if not self.cache_path.exists():
            self._cache = {}
            return
        try:
            payload = json.loads(self.cache_path.read_text())
            if isinstance(payload, dict):
                self._cache = payload
            else:
                self._cache = {}
        except Exception as exc:
            logger.warning("Failed to load identifier cache", error=str(exc), path=str(self.cache_path))
            self._cache = {}

    def _save_cache(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self._cache, indent=2, sort_keys=True))
        except Exception as exc:
            logger.warning("Failed to save identifier cache", error=str(exc), path=str(self.cache_path))

    def _get_cached_record(self, key: str) -> dict[str, Any]:
        cached = self._cache.get(key)
        if isinstance(cached, dict):
            return cached
        return {}

    def _set_cached_record(self, key: str, record: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        existing = self._get_cached_record(key)
        merged = dict(existing)
        merged.update(record)
        merged["updated_at"] = now
        self._cache[key] = merged
        self._save_cache()

    def _search_text(self, query: str) -> str:
        if not self._ddg_available:
            return ""
        try:
            with self._ddg_client() as ddgs:
                results = list(ddgs.text(query, max_results=8))
        except Exception as exc:
            logger.warning("Lookup query failed", query=query, error=str(exc))
            return ""
        return " ".join((item.get("title", "") + " " + item.get("body", "")) for item in results)

    def _score_match(self, text: str, pattern: re.Pattern[str]) -> tuple[Optional[str], float]:
        match = pattern.search(text)
        if not match:
            return None, 0.0
        return match.group(1), 0.85

    def lookup_ticker(self, company_name: str) -> Optional[str]:
        key = self._normalize_key(company_name)
        cached = self._get_cached_record(key)
        ticker = cached.get("ticker")
        if isinstance(ticker, str) and ticker:
            return ticker

        text = self._search_text(f"{company_name} ticker symbol")
        if not text:
            return None

        ticker_value: Optional[str] = None
        confidence = 0.0

        exchange_pattern = re.compile(r"\b(?:NASDAQ|NYSE|AMEX|LSE|OTC)\s*[:\-]\s*([A-Z]{1,6})\b")
        ticker_value, confidence = self._score_match(text, exchange_pattern)
        if ticker_value is None:
            alt = re.search(r"\b\(([A-Z]{1,5})\)\s*(?:Stock|NASDAQ|NYSE)\b", text)
            if alt:
                ticker_value = alt.group(1)
                confidence = 0.65

        if ticker_value:
            self._set_cached_record(
                key,
                {
                    "ticker": ticker_value,
                    "ticker_confidence": confidence,
                    "ticker_source": "duckduckgo_search",
                },
            )
        return ticker_value

    def lookup_company_number(self, company_name: str) -> Optional[str]:
        key = self._normalize_key(company_name)
        cached = self._get_cached_record(key)
        company_number = cached.get("company_number")
        if isinstance(company_number, str) and company_number:
            return company_number

        text = self._search_text(f"{company_name} company number Companies House")
        if not text:
            return None

        company_number_value: Optional[str] = None
        confidence = 0.0

        match = re.search(r"company number\s*([0-9]{6,8})", text, flags=re.IGNORECASE)
        if match:
            company_number_value = match.group(1)
            confidence = 0.8
        else:
            generic = re.search(r"\b([0-9]{6,8})\b", text)
            if generic:
                company_number_value = generic.group(1)
                confidence = 0.55

        if company_number_value:
            self._set_cached_record(
                key,
                {
                    "company_number": company_number_value,
                    "company_number_confidence": confidence,
                    "company_number_source": "duckduckgo_search",
                },
            )
        return company_number_value

    def lookup_isin(self, company_name: str) -> Optional[str]:
        key = self._normalize_key(company_name)
        cached = self._get_cached_record(key)
        isin = cached.get("isin")
        if isinstance(isin, str) and isin:
            return isin

        text = self._search_text(f"{company_name} ISIN")
        if not text:
            return None

        match = re.search(r"\b([A-Z]{2}[A-Z0-9]{9}[0-9])\b", text)
        if not match:
            return None
        isin_value = match.group(1)
        self._set_cached_record(
            key,
            {
                "isin": isin_value,
                "isin_confidence": 0.75,
                "isin_source": "duckduckgo_search",
            },
        )
        return isin_value

    def infer_geography(self, company_name: str, headquarters: Optional[str] = None) -> Optional[str]:
        key = self._normalize_key(company_name)
        cached = self._get_cached_record(key)
        geo = cached.get("geography")
        if isinstance(geo, str) and geo:
            return geo

        haystack = f"{company_name} {headquarters or ''}".lower()
        if any(token in haystack for token in ["uk", "united kingdom", "london"]):
            result = "UK"
        elif any(token in haystack for token in ["us", "united states", "california", "new york"]):
            result = "US"
        elif any(token in haystack for token in ["china", "beijing", "shanghai"]):
            result = "CN"
        elif any(token in haystack for token in ["india", "bangalore", "delhi"]):
            result = "IN"
        elif any(token in haystack for token in ["germany", "france", "sweden", "eu", "europe"]):
            result = "EU"
        else:
            result = None

        if result is not None:
            self._set_cached_record(
                key,
                {
                    "geography": result,
                    "geography_confidence": 0.6,
                    "geography_source": "heuristic",
                },
            )
        return result

    def resolve_identifiers(self, company_name: str, headquarters: Optional[str] = None) -> dict[str, Any]:
        key = self._normalize_key(company_name)

        openfigi_result = self._search_openfigi(company_name)
        if openfigi_result:
            self._cache_openfigi_result(key, openfigi_result)

        opencorporates_result = self._search_opencorporates(company_name)
        if opencorporates_result:
            self._cache_opencorporates_result(key, opencorporates_result)

        ticker = self.lookup_ticker(company_name)
        company_number = self.lookup_company_number(company_name)
        isin = self.lookup_isin(company_name)
        geography = self.infer_geography(company_name, headquarters)

        record = self._get_cached_record(key)
        confidences = [
            value
            for value in [
                record.get("ticker_confidence"),
                record.get("company_number_confidence"),
                record.get("isin_confidence"),
                record.get("geography_confidence"),
            ]
            if isinstance(value, (int, float))
        ]
        overall_confidence = float(sum(confidences) / len(confidences)) if confidences else 0.0

        resolved = {
            "ticker": ticker,
            "company_number": company_number,
            "isin": isin,
            "geography": geography,
            "overall_confidence": overall_confidence,
            "cache_record": record,
        }
        self._set_cached_record(key, {"identifier_confidence": overall_confidence})
        return resolved
