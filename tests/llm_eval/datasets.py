"""Evaluation datasets for core LLM tasks.

STORY-074: Each dataset has at least 5 test cases with defined inputs,
expected output characteristics, and evaluation criteria.
"""

from __future__ import annotations

from solstein.llm.evaluation import EvalCase, EvalDataset

# ---------------------------------------------------------------------------
# Dataset 1: Research Plan Generation
# ---------------------------------------------------------------------------

RESEARCH_PLAN_DATASET = EvalDataset(
    name="research_plan_generation",
    task_type="research_plan",
    min_scores={"query_count": 0.7, "format_compliance": 1.0, "intent_coverage": 0.5},
    cases=[
        EvalCase(
            name="stripe_fintech",
            input_data={
                "queries": [
                    {"query": "Stripe company website official", "priority": 1, "intent": "website"},
                    {"query": "Stripe funding rounds series valuation", "priority": 1, "intent": "funding"},
                    {"query": "Stripe annual revenue 2025", "priority": 1, "intent": "financials"},
                    {"query": "Stripe employee count headcount", "priority": 2, "intent": "headcount"},
                    {"query": "Stripe news latest 2025", "priority": 2, "intent": "news"},
                    {"query": "Stripe social media presence LinkedIn", "priority": 3, "intent": "social"},
                    {"query": "Stripe competitors payment industry", "priority": 2, "intent": "industry"},
                ],
                "estimated_sources": 10,
            },
            expected={
                "min_queries": 6,
                "max_queries": 8,
                "required_intents": ["website", "funding", "financials", "headcount"],
            },
            tags=["fintech", "well-known"],
        ),
        EvalCase(
            name="unknown_startup",
            input_data={
                "queries": [
                    {"query": "NovaTech AI official website", "priority": 1, "intent": "website"},
                    {"query": "NovaTech AI funding crunchbase", "priority": 1, "intent": "funding"},
                    {"query": "NovaTech AI revenue financials", "priority": 2, "intent": "financials"},
                    {"query": "NovaTech AI team size employees", "priority": 2, "intent": "headcount"},
                    {"query": "NovaTech AI news press releases", "priority": 2, "intent": "news"},
                    {"query": "NovaTech AI LinkedIn company", "priority": 3, "intent": "social"},
                ],
                "estimated_sources": 5,
            },
            expected={
                "min_queries": 6,
                "max_queries": 8,
                "required_intents": ["website", "funding", "financials"],
            },
            tags=["startup", "unknown"],
        ),
        EvalCase(
            name="enterprise_saas",
            input_data={
                "queries": [
                    {"query": "Salesforce official site", "priority": 1, "intent": "website"},
                    {"query": "Salesforce SEC filings 10-K", "priority": 1, "intent": "financials"},
                    {"query": "Salesforce acquisitions 2024 2025", "priority": 1, "intent": "news"},
                    {"query": "Salesforce employee count glassdoor", "priority": 2, "intent": "headcount"},
                    {"query": "Salesforce CRM market share", "priority": 2, "intent": "industry"},
                    {"query": "Salesforce investor relations revenue", "priority": 1, "intent": "funding"},
                    {"query": "Salesforce product portfolio cloud", "priority": 3, "intent": "products"},
                ],
                "estimated_sources": 15,
            },
            expected={
                "min_queries": 6,
                "max_queries": 8,
                "required_intents": ["website", "financials", "industry"],
            },
            tags=["enterprise", "public"],
        ),
        EvalCase(
            name="biotech_company",
            input_data={
                "queries": [
                    {"query": "Moderna official website", "priority": 1, "intent": "website"},
                    {"query": "Moderna clinical pipeline trials", "priority": 1, "intent": "products"},
                    {"query": "Moderna quarterly revenue earnings", "priority": 1, "intent": "financials"},
                    {"query": "Moderna hiring employee growth", "priority": 2, "intent": "headcount"},
                    {"query": "Moderna FDA approvals 2025", "priority": 2, "intent": "news"},
                    {"query": "Moderna vs Pfizer BioNTech mRNA", "priority": 2, "intent": "industry"},
                ],
                "estimated_sources": 8,
            },
            expected={
                "min_queries": 6,
                "max_queries": 8,
                "required_intents": ["website", "financials", "products"],
            },
            tags=["biotech", "public"],
        ),
        EvalCase(
            name="european_fintech",
            input_data={
                "queries": [
                    {"query": "Klarna official website", "priority": 1, "intent": "website"},
                    {"query": "Klarna IPO valuation 2025", "priority": 1, "intent": "funding"},
                    {"query": "Klarna revenue growth BNPL", "priority": 1, "intent": "financials"},
                    {"query": "Klarna employees Stockholm", "priority": 2, "intent": "headcount"},
                    {"query": "Klarna latest news expansion", "priority": 2, "intent": "news"},
                    {"query": "Klarna buy now pay later market", "priority": 2, "intent": "industry"},
                    {"query": "Klarna AI features customer service", "priority": 3, "intent": "products"},
                ],
                "estimated_sources": 10,
            },
            expected={
                "min_queries": 6,
                "max_queries": 8,
                "required_intents": ["website", "funding", "financials", "industry"],
            },
            tags=["fintech", "european"],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Dataset 2: Company Data Extraction
# ---------------------------------------------------------------------------

COMPANY_EXTRACTION_DATASET = EvalDataset(
    name="company_data_extraction",
    task_type="company_extraction",
    min_scores={"field_presence": 0.7, "value_accuracy": 0.6},
    cases=[
        EvalCase(
            name="stripe_extraction",
            input_data={
                "company_name": "Stripe",
                "website": "https://stripe.com",
                "description": "Online payment processing platform for internet businesses",
                "industry": "Financial Technology",
                "headquarters": "San Francisco, CA",
                "founded_year": 2010,
                "employees": 8000,
                "revenue": 14000.0,
                "funding_raised": 8700.0,
                "products": ["Stripe Payments", "Stripe Connect", "Stripe Atlas"],
            },
            expected={
                "required_fields": ["company_name", "industry", "description", "website"],
                "expected_values": {
                    "company_name": "Stripe",
                    "industry": "Financial Technology",
                    "founded_year": 2010,
                },
            },
            tags=["fintech"],
        ),
        EvalCase(
            name="databricks_extraction",
            input_data={
                "company_name": "Databricks",
                "website": "https://databricks.com",
                "description": "Unified analytics platform for big data and AI",
                "industry": "Data & Analytics",
                "headquarters": "San Francisco, CA",
                "founded_year": 2013,
                "employees": 6000,
                "revenue": 1600.0,
                "funding_raised": 4100.0,
                "products": ["Delta Lake", "MLflow", "Unity Catalog"],
            },
            expected={
                "required_fields": ["company_name", "industry", "description"],
                "expected_values": {
                    "company_name": "Databricks",
                    "founded_year": 2013,
                },
            },
            tags=["data", "ai"],
        ),
        EvalCase(
            name="figma_extraction",
            input_data={
                "company_name": "Figma",
                "website": "https://figma.com",
                "description": "Collaborative interface design tool",
                "industry": "Design Software",
                "headquarters": "San Francisco, CA",
                "founded_year": 2012,
                "employees": 1500,
                "revenue": 600.0,
                "funding_raised": 330.0,
                "products": ["Figma Design", "FigJam", "Dev Mode"],
            },
            expected={
                "required_fields": ["company_name", "industry", "website", "products"],
                "expected_values": {
                    "company_name": "Figma",
                    "industry": "Design Software",
                },
            },
            tags=["design", "saas"],
        ),
        EvalCase(
            name="sparse_startup",
            input_data={
                "company_name": "NovaTech AI",
                "description": "AI-powered supply chain optimization",
                "industry": "Artificial Intelligence",
            },
            expected={
                "required_fields": ["company_name", "industry"],
                "expected_values": {
                    "company_name": "NovaTech AI",
                },
            },
            tags=["sparse", "startup"],
        ),
        EvalCase(
            name="public_company_extraction",
            input_data={
                "company_name": "Snowflake",
                "website": "https://snowflake.com",
                "description": "Cloud data platform for analytics and data sharing",
                "industry": "Cloud Computing",
                "headquarters": "Bozeman, MT",
                "founded_year": 2012,
                "employees": 5800,
                "revenue": 2800.0,
                "is_public": True,
                "products": ["Snowflake Data Cloud", "Snowpark", "Cortex"],
            },
            expected={
                "required_fields": ["company_name", "industry", "description", "is_public"],
                "expected_values": {
                    "company_name": "Snowflake",
                    "is_public": True,
                    "founded_year": 2012,
                },
            },
            tags=["public", "data"],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Dataset 3: Business Analysis
# ---------------------------------------------------------------------------

BUSINESS_ANALYSIS_DATASET = EvalDataset(
    name="business_analysis",
    task_type="business_analysis",
    min_scores={"content_length": 0.7, "topic_coverage": 0.5},
    cases=[
        EvalCase(
            name="stripe_analysis",
            input_data={
                "analysis": (
                    "Stripe has established itself as a dominant force in online payment "
                    "processing, serving millions of businesses globally. With estimated "
                    "revenue of $14 billion and over 8,000 employees, the company has "
                    "achieved significant scale. The competitive landscape includes "
                    "Adyen, Square, and PayPal, but Stripe differentiates through "
                    "developer-first APIs and vertical integration. Key growth drivers "
                    "include embedded finance, crypto support, and international expansion. "
                    "Threat level is moderate given regulatory scrutiny and market saturation "
                    "in core payment processing."
                ),
            },
            expected={
                "min_words": 50,
                "max_words": 500,
                "required_topics": ["revenue", "competitive", "growth"],
                "data_markers": ["14 billion", "8,000"],
            },
            tags=["fintech"],
        ),
        EvalCase(
            name="databricks_competitive_threat",
            input_data={
                "analysis": (
                    "Databricks represents a significant competitive threat in the data "
                    "and AI platform space. Revenue growth exceeds 50% year-over-year, "
                    "reaching an estimated $1.6 billion ARR. The company's unified lakehouse "
                    "architecture directly challenges Snowflake's warehouse-first approach. "
                    "With $4.1 billion in funding and a $43 billion valuation, Databricks "
                    "has substantial resources for R&D and acquisitions. The open-source "
                    "strategy (Delta Lake, MLflow) creates ecosystem lock-in that is "
                    "difficult for competitors to replicate. Primary risk: dependence on "
                    "cloud provider partnerships."
                ),
            },
            expected={
                "min_words": 50,
                "max_words": 500,
                "required_topics": ["revenue", "competitive", "risk"],
                "data_markers": ["1.6 billion", "4.1 billion"],
            },
            tags=["data", "ai"],
        ),
        EvalCase(
            name="short_analysis",
            input_data={
                "analysis": (
                    "Acme Corp operates in the widget industry with moderate growth "
                    "prospects. Revenue is approximately $50 million. The company faces "
                    "competition from larger players but has a niche in custom widgets."
                ),
            },
            expected={
                "min_words": 20,
                "max_words": 200,
                "required_topics": ["revenue", "competition"],
            },
            tags=["small", "niche"],
        ),
        EvalCase(
            name="signal_extraction_analysis",
            input_data={
                "analysis": (
                    "Growth signals for TechCo are strongly positive. Employee count has "
                    "increased by 35% over the past year, from 200 to 270 employees. "
                    "Web traffic has grown 42% according to SimilarWeb data. The company "
                    "recently raised a $50 million Series B, suggesting investor confidence. "
                    "Patent filings increased from 3 to 8 in the last 12 months. However, "
                    "customer churn rate of 15% is concerning and above industry average "
                    "of 10%. Financial health score: 7.2/10."
                ),
            },
            expected={
                "min_words": 50,
                "max_words": 500,
                "required_topics": ["growth", "employee", "funding", "churn"],
                "data_markers": ["35%", "42%", "50 million"],
            },
            tags=["signals", "metrics"],
        ),
        EvalCase(
            name="empty_analysis",
            input_data={"analysis": ""},
            expected={
                "min_words": 50,
                "max_words": 500,
                "required_topics": ["revenue"],
            },
            tags=["edge_case", "empty"],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_DATASETS: list[EvalDataset] = [
    RESEARCH_PLAN_DATASET,
    COMPANY_EXTRACTION_DATASET,
    BUSINESS_ANALYSIS_DATASET,
]
