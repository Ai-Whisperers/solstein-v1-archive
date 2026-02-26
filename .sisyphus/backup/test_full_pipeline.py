"""
Task 20: Full Pipeline Integration Test

Tests the complete end-to-end pipeline:
1. Data load
2. Scoring
3. Classification
"""

import pytest
from solstein.analytics.scoring import GrowthScorer
from solstein.data.loaders import CompetitorDataLoader


class TestFullPipelineIntegration:
    """Full end-to-end pipeline integration tests."""
    
    def test_pipeline_data_load(self):
        """Step 1: Data load - verify all companies load without errors."""
        loader = CompetitorDataLoader()
        companies = loader.load_companies()
        assert len(companies) > 0, "No companies loaded"
        print(f"Loaded {len(companies)} companies")
    
    def test_pipeline_scoring(self):
        """Step 2: Scoring - verify all companies score without errors."""
        loader = CompetitorDataLoader()
        companies = loader.load_companies()
        scorer = GrowthScorer()
        
        scored_companies = []
        for company in companies:
            company_copy = company.model_copy(deep=True)
            scored = scorer.calculate_scores(company_copy)
            scored_companies.append(scored)
            
            # Verify all score fields are populated
            assert scored.composite_score is not None
            assert scored.growth_score is not None
            assert scored.financial_health_score is not None
            assert scored.competitive_position_score is not None
            assert scored.classification is not None
        
        assert len(scored_companies) == len(companies)
    
    def test_pipeline_classification(self):
        """Step 3: Classification - verify all companies classified correctly."""
        loader = CompetitorDataLoader()
        companies = loader.load_companies()
        scorer = GrowthScorer()
        
        classifications = {"Phoenix": 0, "Salt": 0, "Lead": 0}
        
        for company in companies:
            company_copy = company.model_copy(deep=True)
            scored = scorer.calculate_scores(company_copy)
            
            # Verify classification is valid
            assert scored.classification in ["Phoenix", "Salt", "Lead"]
            classifications[scored.classification] += 1
        
        # Verify we have at least some classifications
        total = sum(classifications.values())
        assert total > 0, "No companies classified"
        print(f"Classifications: Phoenix={classifications['Phoenix']}, Salt={classifications['Salt']}, Lead={classifications['Lead']}")
    
    def test_pipeline_scoring_consistency(self):
        """Step 4: Verify scoring is deterministic."""
        loader = CompetitorDataLoader()
        companies = loader.load_companies()
        
        if len(companies) == 0:
            pytest.skip("No companies to test")
        
        company = companies[0]
        scorer = GrowthScorer()
        
        # Score the same company 3 times
        scores = []
        for _ in range(3):
            company_copy = company.model_copy(deep=True)
            scored = scorer.calculate_scores(company_copy)
            scores.append({
                "composite": scored.composite_score,
                "growth": scored.growth_score,
                "financial": scored.financial_health_score,
                "competitive": scored.competitive_position_score,
                "classification": scored.classification
            })
        
        # Verify all scores are identical
        for i in range(1, len(scores)):
            assert scores[i]["composite"] == scores[0]["composite"]
            assert scores[i]["growth"] == scores[0]["growth"]
            assert scores[i]["financial"] == scores[0]["financial"]
            assert scores[i]["competitive"] == scores[0]["competitive"]
            assert scores[i]["classification"] == scores[0]["classification"]
    
    def test_pipeline_end_to_end(self):
        """Full E2E test: Load → Score → Classify."""
        # Step 1: Load
        loader = CompetitorDataLoader()
        companies = loader.load_companies()
        assert len(companies) > 0
        
        # Step 2: Score
        scorer = GrowthScorer()
        scored_companies = []
        for company in companies:
            company_copy = company.model_copy(deep=True)
            scored = scorer.calculate_scores(company_copy)
            scored_companies.append(scored)
        
        # Step 3: Verify classifications
        classifications = {"Phoenix": 0, "Salt": 0, "Lead": 0}
        for company in scored_companies:
            classifications[company.classification] += 1
        
        total = sum(classifications.values())
        assert total == len(scored_companies)
        
        print(f"\n✓ Full pipeline E2E test passed")
        print(f"  - Companies loaded: {len(companies)}")
        print(f"  - Companies scored: {len(scored_companies)}")
        print(f"  - Classifications: Phoenix={classifications['Phoenix']}, Salt={classifications['Salt']}, Lead={classifications['Lead']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
