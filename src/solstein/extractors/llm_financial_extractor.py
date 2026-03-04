"""LLM-based financial data extraction from prose text."""

import json
import re
from typing import Any

from loguru import logger


class LLMFinancialExtractor:
    """Extract financial metrics from prose text using LLM."""

    def __init__(self, llm_client=None):
        """Initialize with optional LLM client."""
        self.llm_client = llm_client
        self._use_llm = llm_client is not None

    def extract_financial_metrics(self, prose_text: str) -> dict[str, Any]:
        """Extract financial metrics from prose text.

        Returns dict with keys: revenue, growth_rate, employees, profit_margin, funding, valuation
        """
        if not prose_text or not prose_text.strip():
            return {}

        if self._use_llm:
            return self._extract_with_llm(prose_text)
        else:
            return self._extract_with_regex(prose_text)

    def _extract_with_llm(self, prose_text: str) -> dict[str, Any]:
        """Extract financial metrics using LLM."""
        try:
            prompt = f"""Extract financial metrics from the following text. Return a JSON object with these fields (use null for missing values):
- revenue (in millions, as number)
- growth_rate (as percentage number, e.g., 25 for 25%)
- employees (as number)
- profit_margin (as percentage number)
- funding (in millions, as number)
- valuation (in millions, as number)

Text:
{prose_text}

Return ONLY valid JSON, no other text."""

            response = self.llm_client.invoke(prompt)

            # Parse JSON response
            try:
                result = json.loads(response.content if hasattr(response, "content") else str(response))
                return {k: v for k, v in result.items() if v is not None}
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON, falling back to regex")
                return self._extract_with_regex(prose_text)
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}, falling back to regex")
            return self._extract_with_regex(prose_text)

    def _extract_with_regex(self, prose_text: str) -> dict[str, Any]:
        """Extract financial metrics using regex patterns."""
        result = {}

        # Revenue patterns: "$100M", "100 million", "$100M revenue"
        revenue_match = re.search(
            r"\$?([\d.]+)\s*(?:million|M|bn|billion)(?:\s+(?:in\s+)?revenue)?", prose_text, re.IGNORECASE
        )
        if revenue_match:
            result["revenue"] = float(revenue_match.group(1))

        # Growth rate patterns: "25% growth", "growing at 25%"
        growth_match = re.search(r"(?:growth|growing|growth rate).*?([\d.]+)%", prose_text, re.IGNORECASE)
        if growth_match:
            result["growth_rate"] = float(growth_match.group(1))

        # Employee patterns: "500 employees", "has 500 staff"
        employee_match = re.search(r"([\d,]+)\s+(?:employees?|staff|headcount)", prose_text, re.IGNORECASE)
        if employee_match:
            result["employees"] = int(employee_match.group(1).replace(",", ""))

        # Profit margin patterns: "20% profit margin", "20% margin"
        margin_match = re.search(r"([\d.]+)%\s+(?:profit\s+)?margin", prose_text, re.IGNORECASE)
        if margin_match:
            result["profit_margin"] = float(margin_match.group(1))

        # Funding patterns: "raised $50M", "$50M in funding"
        funding_match = re.search(r"(?:raised|funding).*?\$?([\d.]+)\s*(?:million|M)", prose_text, re.IGNORECASE)
        if funding_match:
            result["funding"] = float(funding_match.group(1))

        # Valuation patterns: "valued at $1B", "$1B valuation"
        valuation_match = re.search(
            r"(?:valued\s+at|valuation).*?\$?([\d.]+)\s*(?:billion|B|million|M)", prose_text, re.IGNORECASE
        )
        if valuation_match:
            value = float(valuation_match.group(1))
            # Convert billions to millions if needed
            if "billion" in prose_text[valuation_match.start() : valuation_match.end()].lower():
                value *= 1000
            result["valuation"] = value

        return result
