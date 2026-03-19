"""Competitive position scorer: market tier, AI maturity, SaaS adoption, geographic footprint."""

from ...core.scoring_config import ScoringSettings
from ...domain.models import Company, ScoreComponent, ScoringExplanation


class CompetitivePositionScorer:
    """Score company competitive position (0-10)."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def score(self, profile: Company) -> tuple[float, ScoringExplanation]:
        """Calculate competitive position score (0-10) with explanation."""
        cfg = self.config.competitive
        score = cfg.base_score if cfg.base_score is not None else 0.0
        explanation = ScoringExplanation(base_score=score)

        tier_adj = cfg.tier_scores.get(profile.tier, 0.0)
        score += tier_adj
        explanation.components.append(
            ScoreComponent(
                name="Market Tier",
                value=tier_adj,
                formula=f"tier({profile.tier})",
                reasoning=f"Positioned as a {profile.tier} player in the market.",
            )
        )

        ai_adj = cfg.ai_maturity_scores.get(profile.ai_maturity, 0.0)
        score += ai_adj
        explanation.components.append(
            ScoreComponent(
                name="AI Maturity",
                value=ai_adj,
                formula=f"ai_maturity({profile.ai_maturity})",
                reasoning=f"Technological advantage: AI maturity is {profile.ai_maturity}.",
            )
        )

        saas_maturity = profile.saas_maturity
        saas_adj = (saas_maturity - 1) / 9 * 2.0
        score += saas_adj
        explanation.components.append(
            ScoreComponent(
                name="SaaS Maturity",
                value=saas_adj,
                formula=f"({saas_maturity}-1)/9 * 2.0",
                reasoning=f"SaaS transformation index: {saas_maturity}/10.",
            )
        )

        geographic_presence: list[str] = list(profile.geographic_presence or [])
        if len(geographic_presence) > cfg.geo_global_count:
            adj = cfg.geo_global_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Geographic Footprint",
                    value=adj,
                    formula=f"regions({len(geographic_presence)}) > {cfg.geo_global_count}",
                    reasoning="Global presence identified.",
                )
            )
        elif len(geographic_presence) > cfg.geo_regional_count:
            adj = cfg.geo_regional_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Geographic Footprint",
                    value=adj,
                    formula=f"regions({len(geographic_presence)}) > {cfg.geo_regional_count}",
                    reasoning="Regional presence identified.",
                )
            )

        tech_stack: list[str] = list(profile.tech_stack or [])
        if len(tech_stack) > cfg.tech_diverse_count:
            adj = cfg.tech_diverse_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Stack Diversity",
                    value=adj,
                    formula=f"tech_count({len(tech_stack)}) > {cfg.tech_diverse_count}",
                    reasoning="Diverse technical capabilities identified.",
                )
            )

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation
