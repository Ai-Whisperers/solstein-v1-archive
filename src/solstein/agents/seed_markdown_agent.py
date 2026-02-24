from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

from ..domain.models import DataSourceType
from ..extractors.markdown_extractor import MarkdownExtractor
from .base_agent import AgentTaskResult, BaseDataGatheringAgent


class SeedMarkdownAgent(BaseDataGatheringAgent):
    def __init__(self) -> None:
        super().__init__("SeedMarkdownAgent", DataSourceType.PRESS_RELEASE)
        self.extractor = MarkdownExtractor()

    async def gather(self, company_name: str, context: dict[str, Any]) -> AgentTaskResult:
        start_ts = self._now()
        result = AgentTaskResult(agent_name=self.agent_name, source_type=self.source_type, success=False)

        try:
            md_path_raw = context.get("seed_markdown_path")
            if not md_path_raw:
                result.coverage_gaps.append("seed_markdown_path missing")
                result.error_message = "seed_markdown_path missing"
                return result

            md_path = Path(str(md_path_raw))
            if not md_path.exists():
                result.coverage_gaps.append(f"seed markdown not found: {md_path}")
                result.error_message = f"seed markdown not found: {md_path}"
                return result

            content = md_path.read_text(encoding="utf-8")
            extracted = self.extractor._parse_content(content, str(md_path))

            raw_source = self._create_raw_source(
                raw_content={"path": str(md_path), "content": content},
                source_name=f"Seed Markdown: {md_path.name}",
                url=None,
                confidence=0.90,
                extraction_method="local_markdown_seed",
                metadata={"facts": []},
            )

            for fact_type, key in [
                ("revenue", "revenue"),
                ("growth_rate", "growth_rate"),
                ("employees", "employees"),
                ("profit_margin", "profit_margin"),
                ("funding_raised", "funding"),
                ("valuation", "valuation"),
                ("ai_maturity", "ai_maturity"),
                ("threat_level", "threat_level"),
                ("tier", "tier"),
            ]:
                val = extracted.get(key)
                if val is None:
                    continue
                conf_label = (extracted.get("confidence") or {}).get(key, "Unknown").lower()
                conf = 0.95 if conf_label == "confirmed" else 0.70 if conf_label == "estimated" else 0.55

                result.extracted_facts.append(
                    self._create_fact(
                        fact_type=fact_type,
                        value=val,
                        confidence=conf,
                        sources_used=[str(md_path)],
                        reasoning=f"Seeded from local markdown ({conf_label})",
                    )
                )

                raw_source.metadata.setdefault("facts", []).append(
                    {"type": fact_type, "value": val, "confidence": conf}
                )

            for fact_type, key in [
                ("geographic_presence", "geographic_presence"),
                ("tech_stack", "tech_stack"),
                ("description", "description"),
            ]:
                val = extracted.get(key)
                if not val:
                    continue
                conf = 0.80
                result.extracted_facts.append(
                    self._create_fact(
                        fact_type=fact_type,
                        value=val,
                        confidence=conf,
                        sources_used=[str(md_path)],
                        reasoning="Seeded from local markdown",
                    )
                )
                raw_source.metadata.setdefault("facts", []).append(
                    {"type": fact_type, "value": val, "confidence": conf}
                )

            result.raw_sources.append(raw_source)
            result.success = True
            return result

        except Exception as e:
            logger.error(f"SeedMarkdownAgent failed: {e}")
            result.error_message = str(e)
            result.success = False
            return result

        finally:
            result.execution_time_seconds = self._now() - start_ts

    @staticmethod
    def _now() -> float:
        import time

        return time.time()
