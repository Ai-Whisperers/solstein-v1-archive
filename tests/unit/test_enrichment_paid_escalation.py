from solstein.data.enrichment_config import UnifiedCompanyLoaderConfig
from solstein.data.enrichment_orchestrator import EnrichmentSource
from solstein.data.enrichment_service import EnrichmentService
from solstein.data.source_policy import SourcePolicy, SourceTier
from solstein.data.unified_loader import UnifiedCompany


def test_paid_escalation_budget_guard() -> None:
    config = UnifiedCompanyLoaderConfig(
        enrichment_enabled=True,
        allow_paid_escalation=True,
        paid_escalation_max_attempts=0,
    )
    service = EnrichmentService(config=config)
    service.orchestrator.source_policies = {
        EnrichmentSource.NEWS_SIGNALS.value: SourcePolicy(
            source_name=EnrichmentSource.NEWS_SIGNALS.value,
            tier=SourceTier.PAID,
            authority=0.7,
            required_identifiers=set(),
            field_coverage={"growth_rate"},
        )
    }

    company = UnifiedCompany(id="c1", name="ACME")
    company.ticker = "ACME"
    company.metric_justifications = {}
    company.enrichment_sources = []
    company.enrichment_timestamps = {}

    service._enrich_from_sec = lambda c: c
    service._enrich_from_companies_house = lambda c: c
    service._enrich_from_news_signals = lambda c: c

    _, _, errors = service.enrich_company(company)

    assert any("Paid escalation attempt budget exceeded" in err for err in errors)
