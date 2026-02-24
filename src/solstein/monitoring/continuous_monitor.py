"""Continuous monitoring system for market intelligence updates.

Watches for critical signals (funding, M&A, hiring, product launches)
and automatically updates company profiles when material events occur.
"""

import asyncio
from collections.abc import Callable
from datetime import timezone, datetime

from loguru import logger

from ..agents import GitHubAgent, WebSearchAgent
from ..domain.models import Company


class ContinuousMonitor:
    """Monitors for critical signals across companies."""

    def __init__(self, on_signal_callback: Callable | None = None):
        """Initialize continuous monitor.

        Args:
            on_signal_callback: Optional callback when critical signal detected
        """
        self.logger = logger.bind(service="ContinuousMonitor")
        self.github_agent = GitHubAgent()
        self.web_search_agent = WebSearchAgent()
        self.on_signal_callback = on_signal_callback
        self.is_running = False
        self.last_checks: dict[str, datetime] = {}

    async def start_monitoring(
        self,
        companies: list[Company],
        check_interval_hours: int = 24,
    ) -> None:
        """Start continuous monitoring loop.

        Args:
            companies: List of companies to monitor
            check_interval_hours: Hours between checks per company
        """
        self.logger.info(f"Starting monitoring of {len(companies)} companies (check interval: {check_interval_hours}h)")
        self.is_running = True

        while self.is_running:
            for company in companies:
                await self._check_company(company, check_interval_hours)

            await asyncio.sleep(3600)

    async def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        self.logger.info("Stopping continuous monitoring")
        self.is_running = False

    async def _check_company(self, company: Company, check_interval_hours: int) -> None:
        """Check a single company for updates."""
        last_check = self.last_checks.get(company.id)

        if last_check and (datetime.now(timezone.utc) - last_check).total_seconds() < (check_interval_hours * 3600):
            return

        try:
            signals = await self._detect_critical_signals(company)

            if signals:
                self.logger.warning(f"Critical signals detected for {company.name}: {signals}")
                if self.on_signal_callback:
                    await self.on_signal_callback(company, signals)

            self.last_checks[company.id] = datetime.now(timezone.utc)

        except Exception as e:
            self.logger.error(f"Error monitoring {company.name}: {e}")

    async def _detect_critical_signals(self, company: Company) -> list[dict]:
        """Detect critical signals for a company.

        Returns:
            List of signal dicts with signal_type, description, severity
        """
        signals = []

        funding_signal = await self._detect_funding_news(company.name)
        if funding_signal:
            signals.append(funding_signal)

        ma_signal = await self._detect_ma_activity(company.name)
        if ma_signal:
            signals.append(ma_signal)

        hiring_signal = await self._detect_hiring_surge(company.name)
        if hiring_signal:
            signals.append(hiring_signal)

        product_signal = await self._detect_product_launch(company.name)
        if product_signal:
            signals.append(product_signal)

        exec_signal = await self._detect_executive_changes(company.name)
        if exec_signal:
            signals.append(exec_signal)

        return signals

    async def _detect_funding_news(self, company_name: str) -> dict | None:
        """Detect new funding announcements."""
        self.logger.debug(f"Checking funding news for {company_name}")

        result = await self.web_search_agent.gather(
            company_name,
            context={"include_queries": ["funding", "Series", "round"]},
        )

        if result.success and result.raw_sources:
            return {
                "signal_type": "funding_announcement",
                "description": f"New funding news found: {len(result.raw_sources)} sources",
                "severity": "high",
                "sources": len(result.raw_sources),
            }

        return None

    async def _detect_ma_activity(self, company_name: str) -> dict | None:
        """Detect merger/acquisition news."""
        self.logger.debug(f"Checking M&A activity for {company_name}")

        result = await self.web_search_agent.gather(
            company_name,
            context={"include_queries": ["acquisition", "merger", "acquires"]},
        )

        if result.success and result.raw_sources:
            return {
                "signal_type": "ma_activity",
                "description": f"M&A news found: {len(result.raw_sources)} sources",
                "severity": "critical",
                "sources": len(result.raw_sources),
            }

        return None

    async def _detect_hiring_surge(self, company_name: str) -> dict | None:
        """Detect rapid hiring (via job postings or news)."""
        self.logger.debug(f"Checking hiring activity for {company_name}")

        result = await self.web_search_agent.gather(
            company_name,
            context={"include_queries": ["hiring", "jobs", "careers", "expanding team"]},
        )

        if result.success and len(result.raw_sources) > 10:
            return {
                "signal_type": "hiring_surge",
                "description": f"Multiple hiring signals: {len(result.raw_sources)} sources",
                "severity": "medium",
                "sources": len(result.raw_sources),
            }

        return None

    async def _detect_product_launch(self, company_name: str) -> dict | None:
        """Detect product launches or major updates."""
        self.logger.debug(f"Checking product launches for {company_name}")

        result = await self.web_search_agent.gather(
            company_name,
            context={"include_queries": ["product launch", "announces", "released"]},
        )

        if result.success and result.raw_sources:
            return {
                "signal_type": "product_launch",
                "description": f"Product news found: {len(result.raw_sources)} sources",
                "severity": "medium",
                "sources": len(result.raw_sources),
            }

        return None

    async def _detect_executive_changes(self, company_name: str) -> dict | None:
        """Detect CEO changes, departures, or key hires."""
        self.logger.debug(f"Checking executive changes for {company_name}")

        result = await self.web_search_agent.gather(
            company_name,
            context={"include_queries": ["CEO", "founder", "CTO", "joins", "departs"]},
        )

        if result.success and result.raw_sources:
            return {
                "signal_type": "executive_change",
                "description": f"Executive news found: {len(result.raw_sources)} sources",
                "severity": "high",
                "sources": len(result.raw_sources),
            }

        return None


class ScheduledRefresh:
    """Orchestrates periodic full refreshes of company data."""

    def __init__(self, refresh_interval_days: int = 30):
        """Initialize scheduled refresh.

        Args:
            refresh_interval_days: Days between full refreshes
        """
        self.logger = logger.bind(service="ScheduledRefresh")
        self.refresh_interval_days = refresh_interval_days
        self.last_refresh: dict[str, datetime] = {}

    async def refresh_company_if_needed(
        self,
        company_id: str,
        refresh_func: Callable,
    ) -> bool:
        """Refresh company data if last refresh was N days ago.

        Returns:
            True if refresh was performed, False if skipped
        """
        last = self.last_refresh.get(company_id)

        if last and (datetime.now(timezone.utc) - last).days < self.refresh_interval_days:
            return False

        self.logger.info(f"Performing scheduled refresh for {company_id}")
        await refresh_func(company_id)
        self.last_refresh[company_id] = datetime.now(timezone.utc)
        return True

    async def refresh_all(
        self,
        company_ids: list[str],
        refresh_func: Callable,
    ) -> int:
        """Refresh all companies that need it.

        Returns:
            Count of companies refreshed
        """
        refreshed = 0
        for company_id in company_ids:
            if await self.refresh_company_if_needed(company_id, refresh_func):
                refreshed += 1

        self.logger.info(f"Refreshed {refreshed}/{len(company_ids)} companies")
        return refreshed
