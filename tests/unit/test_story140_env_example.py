"""Tests for STORY-140: .env.example completeness and validation script correctness.

Regression guard: ensures that .env.example stays in sync with config.py as new
fields are added to the Settings class. The validate_env_example.py script is
the primary CI artifact; these tests verify the script itself behaves correctly.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
CONFIG_PY = PROJECT_ROOT / "src" / "solstein" / "config.py"
VALIDATE_SCRIPT = PROJECT_ROOT / "scripts" / "validate_env_example.py"

# Required variables that must be ACTIVE (not commented) in .env.example
REQUIRED_ACTIVE_VARS = {
    "GITHUB_TOKEN",
    "DATABASE__URL",
    "SECURITY__SECRET_KEY",
    "ENVIRONMENT",
    "DEBUG",
    "DEBUG_ERRORS",
}

# Required variables that must be present (active or commented) — from story AC
REQUIRED_PRESENT_VARS = {
    "GITHUB_TOKEN",
    "GROQ_API_KEY",
    "FIREWORKS_API_KEY",
    "MISTRAL_API_KEY",
    "DEEPINFRA_API_KEY",
    "GEMINI_API_KEY",
    "NVIDIA_NIM_API_KEY",
    "CEREBRAS_API_KEY",
    "KIMI_API_KEY",
    "OLLAMA_URL",
    "OLLAMA_MODEL",
    "COMPANIES_HOUSE_API_KEY",
    "GOOGLE_API_KEY",
    "EXA_API_KEY",
    "SEC_USER_AGENT",
    "CONNECTOR_MAX_ATTEMPTS",
    "CONNECTOR_RETRY_BASE_DELAY",
    "CONNECTOR_RETRY_MAX_DELAY",
    "CONNECTOR_CIRCUIT_FAILURE_THRESHOLD",
    "CONNECTOR_CIRCUIT_COOLDOWN_SECONDS",
    "FEATURE_NEW_CLASSIFIER",
    "FEATURE_NEW_READINESS_GATE",
    "FEATURE_NEW_UNIFIED_LOADER",
}


def _extract_active_vars(env_text: str) -> set[str]:
    """Return env var names from active (non-commented) lines."""
    result = set()
    for line in env_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            result.add(stripped.split("=")[0].strip())
    return result


def _extract_all_vars(env_text: str) -> set[str]:
    """Return env var names from all lines (active and commented-out)."""
    var_re = re.compile(r"^#?\s*([A-Z_][A-Z0-9_]*(?:__[A-Z_][A-Z0-9_]*)*)=", re.MULTILINE)
    return {m.group(1).upper() for m in var_re.finditer(env_text)}


class TestEnvExampleExists:
    def test_env_example_file_exists(self) -> None:
        assert ENV_EXAMPLE.exists(), f".env.example not found at {ENV_EXAMPLE}"

    def test_env_example_is_not_empty(self) -> None:
        content = ENV_EXAMPLE.read_text()
        assert len(content.strip()) > 0, ".env.example is empty"

    def test_env_example_has_no_real_secrets(self) -> None:
        content = ENV_EXAMPLE.read_text()
        # Patterns that look like real secrets (not placeholders)
        suspicious_patterns = [
            r"ghp_[a-zA-Z0-9]{36}",  # Real GitHub token
            r"sk-[a-zA-Z0-9]{48}",  # Real OpenAI key
            r"gsk_[a-zA-Z0-9]{52}",  # Real Groq key
        ]
        for pattern in suspicious_patterns:
            assert not re.search(pattern, content), (
                f".env.example appears to contain a real secret matching pattern: {pattern}"
            )


class TestRequiredVariables:
    """Verify that the acceptance criteria from STORY-140 are met."""

    def setup_method(self) -> None:
        self.content = ENV_EXAMPLE.read_text()
        self.active_vars = _extract_active_vars(self.content)
        self.all_vars = _extract_all_vars(self.content)

    def test_required_active_vars_are_uncommented(self) -> None:
        """Variables critical for startup must be active (not commented out)."""
        missing = REQUIRED_ACTIVE_VARS - self.active_vars
        assert not missing, (
            f"These required variables must be ACTIVE (not commented) in .env.example: {sorted(missing)}"
        )

    def test_all_required_vars_are_present(self) -> None:
        """All vars listed in story acceptance criteria must appear at minimum as comments."""
        missing = REQUIRED_PRESENT_VARS - self.all_vars
        assert not missing, f"These variables are missing from .env.example entirely: {sorted(missing)}"

    def test_github_token_marked_required(self) -> None:
        """GITHUB_TOKEN must be present and ideally flagged as required."""
        assert "GITHUB_TOKEN" in self.all_vars, "GITHUB_TOKEN missing from .env.example"

    def test_ollama_config_present(self) -> None:
        assert "OLLAMA_URL" in self.all_vars, "OLLAMA_URL missing"
        assert "OLLAMA_MODEL" in self.all_vars, "OLLAMA_MODEL missing"

    def test_section_headers_present(self) -> None:
        """Verify that section headers are present for key groups."""
        required_sections = [
            "REQUIRED",
            "DATABASE",
            "LLM",
            "CELERY",
            "FEATURE",
        ]
        for section in required_sections:
            assert section in self.content, f"Section header containing '{section}' missing from .env.example"

    def test_all_llm_provider_keys_present(self) -> None:
        llm_keys = {
            "GROQ_API_KEY",
            "FIREWORKS_API_KEY",
            "MISTRAL_API_KEY",
            "DEEPINFRA_API_KEY",
            "GEMINI_API_KEY",
            "NVIDIA_NIM_API_KEY",
            "CEREBRAS_API_KEY",
            "KIMI_API_KEY",
            "ANTHROPIC_API_KEY",
            "SILICONFLOW_API_KEY",
            "ALIBABA_API_KEY",
        }
        missing = llm_keys - self.all_vars
        assert not missing, f"Missing LLM provider keys: {sorted(missing)}"


class TestValidateScript:
    """Verify that scripts/validate_env_example.py itself is correct."""

    def test_validate_script_exists(self) -> None:
        assert VALIDATE_SCRIPT.exists(), f"Validation script not found at {VALIDATE_SCRIPT}"

    def test_validate_script_passes_against_current_files(self) -> None:
        """The script must exit 0 when run against the current files."""
        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), "--config", str(CONFIG_PY), "--env", str(ENV_EXAMPLE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"validate_env_example.py FAILED:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "OK:" in result.stdout

    def test_validate_script_fails_on_missing_var(self, tmp_path: Path) -> None:
        """Script must exit non-zero when a config.py field is absent from .env.example."""
        # Create a minimal config.py with one extra field not in .env.example
        fake_config = tmp_path / "config.py"
        fake_config.write_text(
            "from pydantic_settings import BaseSettings\n"
            "from pydantic import Field\n\n"
            "class Settings(BaseSettings):\n"
            "    my_new_secret_key: str | None = Field(default=None)\n"
        )
        # Use the real .env.example which won't have MY_NEW_SECRET_KEY
        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), "--config", str(fake_config), "--env", str(ENV_EXAMPLE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Script should fail when a field is missing from .env.example"
        assert "MY_NEW_SECRET_KEY" in result.stdout or "MISSING" in result.stdout

    def test_validate_script_help_works(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATE_SCRIPT), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "config" in result.stdout
        assert "env" in result.stdout
