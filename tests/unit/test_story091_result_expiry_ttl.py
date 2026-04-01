"""Tests for STORY-091: Set Result Expiry TTL to Prevent Redis Bloat.

Verifies that:
1. Default result TTL is 86400s (24 hours), not the old 3600s default
2. CELERY_RESULT_EXPIRES_SECONDS env var overrides the nested config
3. CELERY_TIMING__RESULT_EXPIRES env var still works (backward compat)
4. celery_config.py correctly resolves and applies the TTL
5. TTL is always >= 60s (lower bound enforced by config model)
"""

from __future__ import annotations

import importlib
import inspect
import os
from unittest.mock import patch

from pydantic import ValidationError

import solstein.celery_config as celery_cfg
import solstein.config as cfg_mod
from solstein._config_timeouts import CeleryTimingConfig
from solstein.config import Settings, get_settings


class TestCeleryTimingConfigDefaults:
    """Unit tests for CeleryTimingConfig TTL defaults."""

    def test_default_result_expires_is_24_hours(self) -> None:
        """Default result_expires must be 86400s (24h), not the old 3600s."""
        cfg = CeleryTimingConfig()
        assert cfg.result_expires == 86400, (
            f"Expected 86400 (24h), got {cfg.result_expires}. "
            "STORY-091 requires the default to be 24 hours."
        )

    def test_result_expires_lower_bound_enforced(self) -> None:
        """result_expires must be >= 60s — anything lower is rejected."""
        try:
            CeleryTimingConfig(result_expires=30)
            raise AssertionError("Should have raised ValidationError for result_expires=30")
        except ValidationError:
            pass  # expected

    def test_result_expires_custom_value_accepted(self) -> None:
        """Custom result_expires values within bounds are accepted."""
        cfg = CeleryTimingConfig(result_expires=3600)
        assert cfg.result_expires == 3600

    def test_result_expires_description_mentions_polling_contract(self) -> None:
        """The field description must document the polling deadline contract."""
        schema = CeleryTimingConfig.model_json_schema()
        result_expires_desc = schema.get("properties", {}).get("result_expires", {}).get("description", "")
        assert "poll" in result_expires_desc.lower() or "window" in result_expires_desc.lower(), (
            "result_expires description must mention the polling contract/window"
        )


class TestSettingsCeleryResultExpires:
    """Tests for the top-level CELERY_RESULT_EXPIRES_SECONDS alias in Settings."""

    def test_celery_result_expires_seconds_defaults_to_none(self) -> None:
        """Top-level alias is None by default (no override)."""
        s = Settings()
        assert s.celery_result_expires_seconds is None

    def test_celery_result_expires_seconds_env_var_is_read(self) -> None:
        """CELERY_RESULT_EXPIRES_SECONDS env var populates the field."""
        with patch.dict(os.environ, {"CELERY_RESULT_EXPIRES_SECONDS": "7200"}):
            importlib.reload(cfg_mod)
            s = cfg_mod.Settings()
            assert s.celery_result_expires_seconds == 7200

    def test_celery_result_expires_seconds_lower_bound(self) -> None:
        """CELERY_RESULT_EXPIRES_SECONDS must be >= 60s."""
        try:
            Settings(celery_result_expires_seconds=30)
            raise AssertionError("Should have raised ValidationError")
        except ValidationError:
            pass  # expected


class TestCeleryConfigTTLResolution:
    """Tests for how celery_config.py resolves the effective TTL."""

    def test_default_ttl_is_24_hours_when_no_override(self) -> None:
        """Without any override, effective TTL should be 86400s."""
        s = Settings(celery_timing=CeleryTimingConfig())
        assert s.celery_result_expires_seconds is None
        assert s.celery_timing.result_expires == 86400

        # Simulate the resolution logic in celery_config.py
        effective = (
            s.celery_result_expires_seconds
            if s.celery_result_expires_seconds is not None
            else s.celery_timing.result_expires
        )
        assert effective == 86400

    def test_top_level_override_takes_precedence(self) -> None:
        """CELERY_RESULT_EXPIRES_SECONDS overrides CELERY_TIMING__RESULT_EXPIRES."""
        s = Settings(
            celery_result_expires_seconds=7200,
            celery_timing=CeleryTimingConfig(result_expires=86400),
        )

        effective = (
            s.celery_result_expires_seconds
            if s.celery_result_expires_seconds is not None
            else s.celery_timing.result_expires
        )
        assert effective == 7200, "Top-level override must take precedence over nested config"

    def test_nested_config_used_when_no_top_level_override(self) -> None:
        """When top-level is None, CELERY_TIMING__RESULT_EXPIRES is used."""
        s = Settings(
            celery_result_expires_seconds=None,
            celery_timing=CeleryTimingConfig(result_expires=43200),
        )

        effective = (
            s.celery_result_expires_seconds
            if s.celery_result_expires_seconds is not None
            else s.celery_timing.result_expires
        )
        assert effective == 43200

    def test_celery_app_conf_result_expires_is_set(self) -> None:
        """celery_config.py must apply result_expires to the Celery app conf."""
        assert hasattr(celery_cfg, "celery_app")
        assert hasattr(celery_cfg, "_result_expires")
        assert celery_cfg._result_expires >= 60, (
            f"celery_config._result_expires={celery_cfg._result_expires} must be >= 60"
        )

    def test_result_expires_resolution_variable_exported(self) -> None:
        """celery_config._result_expires is the resolved value actually applied."""
        settings = get_settings()
        expected = (
            settings.celery_result_expires_seconds
            if settings.celery_result_expires_seconds is not None
            else settings.celery_timing.result_expires
        )
        assert celery_cfg._result_expires == expected


class TestCeleryConfigComments:
    """Verify that the celery_config source documents the polling contract."""

    def test_celery_config_source_documents_polling_contract(self) -> None:
        """The celery_config.py module must contain polling contract documentation."""
        source = inspect.getsource(celery_cfg)
        assert "poll" in source.lower() or "window" in source.lower(), (
            "celery_config.py must document the result polling contract"
        )

    def test_celery_config_source_documents_env_var(self) -> None:
        """celery_config.py must mention CELERY_RESULT_EXPIRES_SECONDS."""
        source = inspect.getsource(celery_cfg)
        assert "CELERY_RESULT_EXPIRES_SECONDS" in source, (
            "celery_config.py must document the CELERY_RESULT_EXPIRES_SECONDS env var"
        )
