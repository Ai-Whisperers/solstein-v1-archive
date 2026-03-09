from __future__ import annotations

import pathlib
from typing import Generator

import pytest
from loguru import logger

from solstein.config import ConfigurationError, SecurityConfig, Settings


class _LogCapture:
    """Minimal in-memory loguru sink for assertions in tests."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def write(self, message: str) -> None:
        self.messages.append(message)

    def __contains__(self, text: str) -> bool:
        return any(text in m for m in self.messages)


@pytest.fixture()
def log_capture() -> Generator[_LogCapture, None, None]:
    sink = _LogCapture()
    sink_id = logger.add(sink.write, format="{message}", level="DEBUG")
    try:
        yield sink
    finally:
        logger.remove(sink_id)

import pathlib

import pytest

from solstein.config import ConfigurationError, SecurityConfig, Settings


def test_change_me_in_production_absent_from_source() -> None:
    src_root = pathlib.Path(__file__).parents[2] / "src"
    for path in src_root.rglob("*.py"):
        content = path.read_text(errors="ignore")
        assert "change-me-in-production" not in content, f"Hardcoded insecure secret found in {path}"


def test_secret_key_empty_by_default() -> None:
    cfg = SecurityConfig()
    assert cfg.secret_key == ""


def test_secret_key_explicitly_set() -> None:
    cfg = SecurityConfig(secret_key="my-strong-test-secret-32chars!")
    assert cfg.secret_key == "my-strong-test-secret-32chars!"


def test_check_configuration_raises_without_github_token() -> None:
    settings = Settings().model_copy(update={"github_token": None})
    with pytest.raises(ConfigurationError, match="GITHUB_TOKEN"):
        settings.check_configuration()


def test_check_configuration_warns_without_security_key(log_capture: _LogCapture) -> None:
    no_key_security = Settings().security.model_copy(update={"secret_key": ""})
    settings = Settings().model_copy(update={"github_token": "gh_test_token_123", "security": no_key_security})
    settings.check_configuration()
    assert "SECURITY__SECRET_KEY" in log_capture


def test_check_configuration_warns_without_llm_providers(log_capture: _LogCapture) -> None:
    settings = Settings().model_copy(
        update={
            "github_token": "gh_test_token_123",
            "openai_api_key": None,
            "anthropic_api_key": None,
            "groq_api_key": None,
            "gemini_api_key": None,
            "fireworks_api_key": None,
            "mistral_api_key": None,
            "deepinfra_api_key": None,
            "cerebras_api_key": None,
            "kimi_api_key": None,
            "siliconflow_api_key": None,
            "alibaba_api_key": None,
            "nvidia_nim_api_key": None,
            "perplexity_api_key": None,
        }
    )
    settings.check_configuration()
    assert "LLM provider" in log_capture


def test_check_configuration_logs_summary_with_llm_key(log_capture: _LogCapture) -> None:
    settings = Settings().model_copy(
        update={"github_token": "gh_test_token_123", "openai_api_key": "sk-test-openai-key"}
    )
    settings.check_configuration()
    assert "Configuration validation passed" in log_capture
