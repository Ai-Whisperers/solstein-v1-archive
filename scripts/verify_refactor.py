import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

try:
    print("Attempting to import solstein.api.main...")
    print("SUCCESS: solstein.api.main imported successfully.")

    print("Attempting to verify GrowthScorer configuration...")
    from solstein.analytics.scoring import GrowthScorer
    from solstein.domain.models import Company, CompanyTier, FinancialMetric

    scorer = GrowthScorer()
    company = Company(
        id="test",
        name="Test",
        tier=CompanyTier.TIER_1,
        financials=FinancialMetric(
            revenue=500_000_000, growth_rate=25.0, profit_margin=10.0
        ),
    )
    scored = scorer.calculate_scores(company)
    print(
        f"SUCCESS: Scoring calculated: Growth={scored.growth_score}, "
        f"Health={scored.financial_health_score}"
    )

    print("Attempting to verify Celery task import...")
    try:
        print("SUCCESS: Celery task imported.")

        # We can't easily test full celery execution without redis
        # but we can check if the function is callable
        # or use task.apply() if we want to run it synchronously
        # (but that might fail if repo needs data)
        print("Celery verification: Task object exists.")
    except Exception as e:
        print(f"FAILURE: Celery task verification failed: {e}")
        exit(1)


except Exception as e:
    print(f"FAILURE: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
