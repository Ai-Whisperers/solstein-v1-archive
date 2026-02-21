"""Tests for configuration validation.

Tests verify that Settings.check_configuration() properly validates required
and optional API keys, warns appropriately, and raises ConfigurationError
when critical configuration is missing.
"""

import os
import pytest
from unittest.mock import patch
from loguru import logger

from solstein.config import Settings, ConfigurationError


class TestConfigurationValidation:
    """Test suite for Settings.check_configuration()."""

    def test_check_configuration_passes_with_all_keys(self, caplog):
        """Verify validation passes when all keys are present."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "ghp_valid_token",
                "COMPANIES_HOUSE_API_KEY": "ch_valid_key",
                "GOOGLE_API_KEY": "google_valid_key",
            },
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="INFO")
            try:
                settings = Settings()
                settings.check_configuration()

                assert any(
                    "Configuration validation passed" in log for log in captured_logs
                )
            finally:
                logger.remove(handler_id)

    def test_check_configuration_requires_github_token(self):
        """Verify that GITHUB_TOKEN is required and raises ConfigurationError."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            with pytest.raises(ConfigurationError) as exc_info:
                settings.check_configuration()

            assert "GITHUB_TOKEN environment variable is required" in str(
                exc_info.value
            )
            assert "https://github.com/settings/tokens" in str(exc_info.value)

    def test_check_configuration_warns_missing_companies_house_key(self):
        """Verify that missing COMPANIES_HOUSE_API_KEY triggers a warning, not error."""
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "ghp_valid_token"},
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="WARNING")
            try:
                settings = Settings()
                settings.check_configuration()

                assert any(
                    "COMPANIES_HOUSE_API_KEY not configured" in log
                    for log in captured_logs
                )
            finally:
                logger.remove(handler_id)

    def test_check_configuration_warns_missing_google_api_key(self):
        """Verify that missing GOOGLE_API_KEY triggers a warning, not error."""
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "ghp_valid_token"},
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="WARNING")
            try:
                settings = Settings()
                settings.check_configuration()

                assert any(
                    "GOOGLE_API_KEY not configured" in log for log in captured_logs
                )
            finally:
                logger.remove(handler_id)

    def test_check_configuration_warns_missing_both_optional_keys(self):
        """Verify that both optional keys can be missing simultaneously (only warns)."""
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "ghp_valid_token"},
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="DEBUG")
            try:
                settings = Settings()
                settings.check_configuration()

                log_text = " ".join(captured_logs)
                assert "COMPANIES_HOUSE_API_KEY not configured" in log_text
                assert "GOOGLE_API_KEY not configured" in log_text
                assert "Configuration validation passed" in log_text
            finally:
                logger.remove(handler_id)

    def test_check_configuration_github_token_empty_string_fails(self):
        """Verify that empty GITHUB_TOKEN string is treated as missing."""
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": ""},
            clear=True,
        ):
            settings = Settings()
            with pytest.raises(ConfigurationError) as exc_info:
                settings.check_configuration()

            assert "GITHUB_TOKEN environment variable is required" in str(
                exc_info.value
            )

    def test_check_configuration_github_token_whitespace_only(self):
        """Verify that whitespace-only GITHUB_TOKEN is treated as valid.

        Note: os.getenv returns the raw value including whitespace.
        This is acceptable because the actual API call will fail with a whitespace token.
        """
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "   "},
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="INFO")
            try:
                settings = Settings()
                settings.check_configuration()

                assert any(
                    "Configuration validation passed" in log for log in captured_logs
                )
            finally:
                logger.remove(handler_id)

    def test_check_configuration_idempotent(self):
        """Verify that check_configuration can be called multiple times safely."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "ghp_valid_token",
                "COMPANIES_HOUSE_API_KEY": "ch_valid_key",
                "GOOGLE_API_KEY": "google_valid_key",
            },
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="INFO")
            try:
                settings = Settings()
                settings.check_configuration()
                settings.check_configuration()
                settings.check_configuration()

                passed_count = sum(
                    1
                    for log in captured_logs
                    if "Configuration validation passed" in log
                )
                assert passed_count == 3
            finally:
                logger.remove(handler_id)

    def test_check_configuration_with_partial_optional_keys(self):
        """Verify validation with some optional keys present and some missing."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "ghp_valid_token",
                "COMPANIES_HOUSE_API_KEY": "ch_valid_key",
            },
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="DEBUG")
            try:
                settings = Settings()
                settings.check_configuration()

                log_text = " ".join(captured_logs)
                assert "COMPANIES_HOUSE_API_KEY not configured" not in log_text
                assert "GOOGLE_API_KEY not configured" in log_text
                assert "Configuration validation passed" in log_text
            finally:
                logger.remove(handler_id)

    def test_check_configuration_error_message_is_actionable(self):
        """Verify that ConfigurationError message provides actionable guidance."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            with pytest.raises(ConfigurationError) as exc_info:
                settings.check_configuration()

            error_message = str(exc_info.value)
            # Error must include:
            # 1. What's wrong
            assert "GITHUB_TOKEN" in error_message
            # 2. Why it matters (implicit in the error)
            # 3. Where to get help
            assert "https://github.com/settings/tokens" in error_message
            # 4. What to do (implicit in "Please set it")
            assert "set it before starting" in error_message.lower()

    def test_check_configuration_logs_at_info_level_on_success(self):
        """Verify that successful validation is logged at INFO level."""
        with patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "ghp_valid_token"},
            clear=True,
        ):
            captured_logs = []

            def log_sink(message):
                captured_logs.append(message.record["message"])

            handler_id = logger.add(log_sink, level="INFO")
            try:
                settings = Settings()
                settings.check_configuration()

                assert any(
                    "Configuration validation passed" in log for log in captured_logs
                )
            finally:
                logger.remove(handler_id)

    def test_check_configuration_does_not_modify_settings(self):
        """Verify that check_configuration is read-only and doesn't modify the instance."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "ghp_valid_token",
                "COMPANIES_HOUSE_API_KEY": "ch_valid_key",
            },
            clear=True,
        ):
            settings = Settings()
            original_environment = settings.environment
            original_debug = settings.debug

            settings.check_configuration()

            # Settings should be unchanged
            assert settings.environment == original_environment
            assert settings.debug == original_debug
