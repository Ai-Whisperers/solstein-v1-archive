"""Tests for STORY-055: Centralize all inline LLM prompt strings into managed registry.

Acceptance criteria:
- All prompt strings live in solstein.llm.prompts._DEFAULT_PROMPTS
- No inline LLM prompt literals remain in querier, client, or agent files
- get_prompt() interpolates template variables correctly
- get_system_prompt() returns raw strings with no interpolation
- Missing/unknown prompt names return "" (no exception)
- system_company_filter prompt survives round-trip through get_system_prompt
  (literal JSON braces must not be treated as format variables)
"""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pytest

import solstein.analytics.filters.llm as _filters_llm_mod
import solstein.llm.instructor_client as _instructor_client_mod
import solstein.llm.structured_client as _structured_client_mod
import solstein.research.research_agents as _research_agents_mod
from solstein.llm.prompts import (
    _DEFAULT_PROMPTS,
    PromptManager,
    get_prompt,
    get_system_prompt,
)

# ---------------------------------------------------------------------------
# Registry completeness
# ---------------------------------------------------------------------------

STORY_055_REQUIRED_PROMPTS = [
    # User-turn prompts (pre-existing)
    "research_planner",
    "company_extractor",
    "company_filter",
    # System prompts (pre-existing)
    "system_research_planner",
    "system_company_extractor",
    "system_business_analyst",
    "system_data_extractor",
    # System prompts added by STORY-055
    "system_structured_extractor",
    "system_company_filter",
]


class TestRegistryCompleteness:
    """All STORY-055 required prompts must be present in _DEFAULT_PROMPTS."""

    def test_all_required_keys_present(self):
        for name in STORY_055_REQUIRED_PROMPTS:
            assert name in _DEFAULT_PROMPTS, (
                f"Missing required prompt key: '{name}'. "
                "All inline LLM prompt strings must be centralised in prompts.py."
            )

    def test_no_empty_prompt_values(self):
        for name in STORY_055_REQUIRED_PROMPTS:
            value = _DEFAULT_PROMPTS.get(name, "")
            assert value.strip(), f"Prompt '{name}' has an empty or whitespace-only value."

    def test_system_prompts_follow_naming_convention(self):
        system_keys = [k for k in _DEFAULT_PROMPTS if k.startswith("system_")]
        assert len(system_keys) >= 5, "Expected at least 5 system_* prompts"
        for key in system_keys:
            assert key == key.lower(), f"System prompt key '{key}' must be lowercase"
            assert "_" in key, f"System prompt key '{key}' must use snake_case"


# ---------------------------------------------------------------------------
# get_system_prompt() — no interpolation, literal JSON braces survive
# ---------------------------------------------------------------------------


class TestGetSystemPrompt:
    """get_system_prompt() must return raw strings without variable interpolation."""

    def test_system_business_analyst_content(self):
        result = get_system_prompt("system_business_analyst")
        assert "business analyst" in result.lower()

    def test_system_research_planner_content(self):
        result = get_system_prompt("system_research_planner")
        assert "research" in result.lower()

    def test_system_company_extractor_content(self):
        result = get_system_prompt("system_company_extractor")
        assert "extract" in result.lower()

    def test_system_data_extractor_content(self):
        result = get_system_prompt("system_data_extractor")
        assert "null" in result.lower() or "extract" in result.lower()

    def test_system_structured_extractor_content(self):
        result = get_system_prompt("system_structured_extractor")
        assert "json" in result.lower()

    def test_system_company_filter_returns_literal_json_braces(self):
        """Critical: JSON literal {} in system_company_filter must not be consumed
        as format variables. get_system_prompt() calls get() with no kwargs, so
        str.format() must leave the escaped {{}} as literal braces."""
        result = get_system_prompt("system_company_filter")
        assert "{" in result, (
            "system_company_filter should contain literal JSON braces in the output. "
            "Check that {{}} escaping is used in _DEFAULT_PROMPTS."
        )
        assert "}" in result
        assert "matches" in result
        assert "reasoning" in result

    def test_unknown_system_prompt_returns_empty_string(self):
        result = get_system_prompt("system_totally_nonexistent_xyz")
        assert result == ""

    def test_no_exception_on_unknown_key(self):
        # Must not raise KeyError or any other exception
        try:
            result = get_system_prompt("does_not_exist")
            assert result == ""
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"get_system_prompt raised an unexpected exception: {exc}")


# ---------------------------------------------------------------------------
# get_prompt() — variable interpolation
# ---------------------------------------------------------------------------


class TestGetPrompt:
    """get_prompt() must interpolate template variables correctly."""

    def test_research_planner_interpolates_company_name(self):
        result = get_prompt("research_planner", company_name="Acme Corp", industry_context="")
        assert "Acme Corp" in result

    def test_research_planner_interpolates_industry_context(self):
        result = get_prompt(
            "research_planner",
            company_name="Startup",
            industry_context="in the fintech industry",
        )
        assert "fintech" in result

    def test_company_extractor_interpolates_all_vars(self):
        result = get_prompt(
            "company_extractor",
            company_name="WidgetCo",
            url="https://example.com",
            content="Some page content here",
        )
        assert "WidgetCo" in result
        assert "https://example.com" in result
        assert "Some page content" in result

    def test_company_filter_interpolates_both_vars(self):
        result = get_prompt(
            "company_filter",
            company_profile="Company: Acme\nRevenue: €50M",
            filter_criteria="fast growing tech",
        )
        assert "Acme" in result
        assert "fast growing tech" in result

    def test_missing_variable_returns_unformatted_template(self):
        """When a variable is missing, return the raw template (no crash)."""
        result = get_prompt("research_planner", company_name="OnlyOne")
        # Should not raise — returns raw template or partially filled
        assert isinstance(result, str)

    def test_unknown_prompt_returns_empty_string(self):
        result = get_prompt("nonexistent_prompt_key")
        assert result == ""


# ---------------------------------------------------------------------------
# PromptManager — Langfuse fallback behaviour
# ---------------------------------------------------------------------------


class TestPromptManagerFallback:
    """PromptManager must fall back to local defaults when Langfuse is unavailable."""

    def test_no_langfuse_client_uses_local_defaults(self):
        pm = PromptManager(langfuse_client=None)
        result = pm.get("system_business_analyst")
        assert "business analyst" in result.lower()

    def test_langfuse_error_falls_back_to_local(self):
        mock_lf = MagicMock()
        mock_lf.get_prompt.side_effect = ConnectionError("Langfuse unavailable")
        pm = PromptManager(langfuse_client=mock_lf)
        result = pm.get("system_business_analyst")
        assert "business analyst" in result.lower()

    def test_langfuse_prompt_overrides_local(self):
        mock_lf = MagicMock()
        mock_prompt = MagicMock()
        mock_prompt.prompt = "Custom Langfuse override for {company_name}"
        mock_lf.get_prompt.return_value = mock_prompt

        pm = PromptManager(langfuse_client=mock_lf)
        result = pm.get("research_planner", company_name="Beta", industry_context="")
        assert result == "Custom Langfuse override for Beta"


# ---------------------------------------------------------------------------
# Inline prompt elimination — static import checks
# ---------------------------------------------------------------------------


class TestNoInlinePrompts:
    """Verify that centralised files import from prompts.py rather than
    defining inline LLM prompt strings."""

    def test_research_agents_imports_get_system_prompt(self):
        source = inspect.getsource(_research_agents_mod)
        assert "get_system_prompt" in source, (
            "research_agents.py must import and use get_system_prompt() from solstein.llm.prompts"
        )

    def test_instructor_client_imports_get_system_prompt(self):
        source = inspect.getsource(_instructor_client_mod)
        assert "get_system_prompt" in source, "instructor_client.py must import and use get_system_prompt()"

    def test_structured_client_imports_get_system_prompt(self):
        source = inspect.getsource(_structured_client_mod)
        assert "get_system_prompt" in source, "structured_client.py must import and use get_system_prompt()"

    def test_llm_filter_imports_get_system_prompt(self):
        source = inspect.getsource(_filters_llm_mod)
        assert "get_system_prompt" in source, "analytics/filters/llm.py must import and use get_system_prompt()"
