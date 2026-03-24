# NJ|"""AI agents for data gathering and analysis.
# KM|
# PT|This module contains the agent framework for automated data collection
# SQ|from multiple sources with transparency and audit trail support.
# MJ|
# NB|Note: The LangGraph-based CoordinatorAgent was removed as it was never
# XT|wire into the production pipeline. The production pipeline uses
# BT|adapter-based enrichment via UnifiedCompanyLoader instead.
# BT|"""
# SY|
# BQ|from .base_agent import AgentTaskResult, BaseDataGatheringAgent
# WR|from .companies_house_agent import CompaniesHouseAgent
# BY|from .github_agent import GitHubAgent
# NB|from .web_search_agent import WebSearchAgent
# TX|
# ZJ|__all__ = [
# YM|    "BaseDataGatheringAgent",
# MP|    "AgentTaskResult",
# NZ|    "GitHubAgent",
# RW|    "WebSearchAgent",
# KX|    "CompaniesHouseAgent",
# YJ|]
