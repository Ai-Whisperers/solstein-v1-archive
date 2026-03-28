"""Website data gathering agent.

STORY-135: Replaced requests with httpx.AsyncClient for non-blocking HTTP.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import httpx
from loguru import logger

from ..core.url_validator import SSRFError, validate_url
from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent


class WebsiteAgent(BaseDataGatheringAgent):
    def __init__(self) -> None:
        super().__init__("WebsiteAgent", DataSourceType.WEBSITE)

    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        start = datetime.now(timezone.utc)
        result = AgentTaskResult(agent_name=self.agent_name, source_type=self.source_type, success=False)

        url = context.get("website") or context.get("company_website")
        if not url:
            result.coverage_gaps.append("website missing")
            result.error_message = "website missing"
            result.execution_time_seconds = (datetime.now(timezone.utc) - start).total_seconds()
            return result

        try:
            # STORY-070: Validate URL before fetch (SSRF prevention)
            validate_url(str(url))

            async with httpx.AsyncClient() as client:
                resp = await client.get(str(url), timeout=20, headers={"User-Agent": "Solstein-AI"})
            text = resp.text or ""
            excerpt = text[:5000]

            title = None
            m = re.search(r"<title[^>]*>(.*?)</title>", excerpt, re.IGNORECASE | re.DOTALL)
            if m:
                title = re.sub(r"\s+", " ", m.group(1)).strip()

            meta_desc = None
            m = re.search(
                r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"]([^'\"]+)['\"][^>]*>",
                excerpt,
                re.IGNORECASE,
            )
            if m:
                meta_desc = m.group(1).strip()

            raw_source = self._create_raw_source(
                raw_content={
                    "requested_url": str(url),
                    "final_url": str(resp.url),
                    "status_code": resp.status_code,
                    "title": title,
                    "meta_description": meta_desc,
                    "excerpt": excerpt,
                },
                source_name=f"Website: {company_name}",
                url=str(resp.url),
                confidence=0.70,
                extraction_method="http_get",
                metadata={"facts": []},
            )

            if title:
                fact = self._create_fact(
                    fact_type="website_title",
                    value=title,
                    confidence=0.70,
                    sources_used=[str(resp.url)],
                    reasoning="Parsed from HTML <title>",
                )
                result.extracted_facts.append(fact)
                raw_source.metadata["facts"].append(
                    {"type": fact.fact_type, "value": fact.value, "confidence": fact.confidence}
                )

            if meta_desc:
                fact = self._create_fact(
                    fact_type="website_meta_description",
                    value=meta_desc,
                    confidence=0.70,
                    sources_used=[str(resp.url)],
                    reasoning="Parsed from meta description",
                )
                result.extracted_facts.append(fact)
                raw_source.metadata["facts"].append(
                    {"type": fact.fact_type, "value": fact.value, "confidence": fact.confidence}
                )

            result.raw_sources.append(raw_source)
            result.success = True
            return result

        except SSRFError as e:
            logger.warning(f"WebsiteAgent SSRF blocked for {company_name}: {e}")
            result.error_message = f"URL validation failed: {e}"
            result.success = False
            return result
        except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
            logger.warning(f"WebsiteAgent failed for {company_name}: {e}")
            result.error_message = str(e)
            result.success = False
            return result

        finally:
            result.execution_time_seconds = (datetime.now(timezone.utc) - start).total_seconds()
