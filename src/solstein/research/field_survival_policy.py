"""Field survival policy for the pipeline.

STORY-351: Defines which fact types are intentionally excluded from the Company
output model. Every other fact type produced by aggregate.py MUST reach
Company.model_dump() — enforced by the regression gate in
tests/unit/test_pipeline_field_survival.py.

Adding a fact type here without a clear reason is not acceptable. If you don't
know what to do with a fact, wire it into Company or FinancialMetric.
"""

from __future__ import annotations

# Fact types that are intentionally NOT mapped to Company fields.
# Key: fact_type string
# Value: reason for exclusion (required — "I don't know" is not a valid reason)
INTENTIONALLY_EXCLUDED_FACTS: dict[str, str] = {
    # aggregation/metadata signals — not business facts
    "ai_signal_strength": (
        "String enum signal ('strong', 'moderate', etc.) surfaced via ai_signal_level "
        "on Company. The raw string doesn't map cleanly to a scalar field and is "
        "captured in signal_confidences."
    ),
    "valuation": (
        "Crunchbase valuation is captured via the 'valuation' signal which maps to "
        "Company.financials.valuation. This raw fact key is consumed by _signal_valuation."
    ),
    "market_cap": (
        "Consumed by _signal_company_size and _signal_valuation. The aggregated value "
        "lands in Company.financials.valuation (preferred over raw funding valuation)."
    ),
    "positive_article_count": (
        "Consumed by _signal_market_sentiment to derive sentiment score. The derived "
        "score lands in Company.news_sentiment. Raw article counts are ephemeral."
    ),
    "negative_article_count": (
        "Consumed by _signal_market_sentiment to derive sentiment score. The derived "
        "score lands in Company.news_sentiment. Raw article counts are ephemeral."
    ),
    "investors": (
        "String/list value extracted by _extract_lead_investors() and mapped to "
        "Company.lead_investors directly in build_company_entity_from_signals()."
    ),
    "tech_stack": (
        "List value extracted by _build_tech_stack() and mapped to Company.tech_stack "
        "directly in build_company_entity_from_signals()."
    ),
    # Descriptive string facts handled via _extract_descriptive_fields() direct mapping
    "name": "Direct mapping: Company.name via _extract_descriptive_fields().",
    "description": "Direct mapping: Company.description via _extract_descriptive_fields().",
    "website": "Direct mapping: Company.website via _extract_descriptive_fields().",
    "headquarters": "Direct mapping: Company.headquarters via _extract_descriptive_fields().",
    "founded_year": "Direct mapping: Company.founded_year via _extract_descriptive_fields().",
    "industry": "Direct mapping: Company.industry via _extract_descriptive_fields().",
    "total_funding_raised": (
        "Numeric funding fact consumed by _signal_funding() — mapped to "
        "Company.financials.funding_raised via the funding signal."
    ),
    "ai_related_patents": (
        "Consumed by _signal_innovation() to compute ai_ratio annotation. Not stored "
        "as a standalone Company field; captured in signal reasoning."
    ),
}
