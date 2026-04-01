"""Tests for STORY-096: Multi-Stage Dockerfile for Production.

Validates the Dockerfile uses multi-stage build, runs as non-root user,
uses exec form CMD, and the .dockerignore excludes non-runtime files.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def dockerfile_content():
    """Read the production Dockerfile."""
    path = PROJECT_ROOT / "Dockerfile"
    assert path.exists(), f"Dockerfile not found at {path}"
    return path.read_text()


@pytest.fixture
def dockerignore_content():
    """Read the .dockerignore file."""
    path = PROJECT_ROOT / ".dockerignore"
    assert path.exists(), f".dockerignore not found at {path}"
    return path.read_text()


class TestMultiStageBuild:
    """Verify the Dockerfile uses multi-stage build pattern."""

    def test_has_builder_stage(self, dockerfile_content):
        """Dockerfile must have a builder stage."""
        assert "AS builder" in dockerfile_content or "as builder" in dockerfile_content

    def test_has_runtime_stage(self, dockerfile_content):
        """Dockerfile must have a runtime stage."""
        assert "AS runtime" in dockerfile_content or "as runtime" in dockerfile_content

    def test_copies_from_builder(self, dockerfile_content):
        """Runtime stage must COPY --from=builder."""
        assert "--from=builder" in dockerfile_content

    def test_uses_slim_base(self, dockerfile_content):
        """Both stages should use slim base images."""
        assert "slim" in dockerfile_content

    def test_builder_has_build_deps(self, dockerfile_content):
        """Builder stage must install build-essential and gcc."""
        # Extract builder stage content (between first FROM and second FROM)
        lines = dockerfile_content.split("\n")
        builder_lines = []
        in_builder = False
        for line in lines:
            if "AS builder" in line:
                in_builder = True
                continue
            if "AS runtime" in line:
                break
            if in_builder:
                builder_lines.append(line)
        builder_content = "\n".join(builder_lines)
        assert "build-essential" in builder_content or "gcc" in builder_content


class TestNonRootUser:
    """Verify the container runs as a non-root user."""

    def test_creates_user(self, dockerfile_content):
        """Dockerfile must create a non-root user."""
        assert "useradd" in dockerfile_content or "adduser" in dockerfile_content

    def test_switches_to_nonroot(self, dockerfile_content):
        """Dockerfile must switch to non-root user via USER directive."""
        assert "USER solstein" in dockerfile_content

    def test_user_before_cmd(self, dockerfile_content):
        """USER directive must appear before CMD."""
        user_pos = dockerfile_content.index("USER solstein")
        cmd_pos = dockerfile_content.rindex("CMD ")
        assert user_pos < cmd_pos, "USER must appear before CMD"


class TestExecFormCMD:
    """Verify CMD uses exec form for proper signal handling."""

    def test_cmd_uses_exec_form(self, dockerfile_content):
        """CMD must use JSON array (exec) form, not shell form."""
        # Find the last CMD line
        lines = dockerfile_content.strip().split("\n")
        cmd_lines = [line for line in lines if line.strip().startswith("CMD ")]
        assert cmd_lines, "Dockerfile must have a CMD instruction"
        last_cmd = cmd_lines[-1].strip()
        assert last_cmd.startswith("CMD ["), f"CMD must use exec form (JSON array), got: {last_cmd}"


class TestRuntimeClean:
    """Verify the runtime image doesn't contain build tools."""

    def test_no_build_tools_in_runtime(self, dockerfile_content):
        """Runtime stage should not install build tools."""
        # Extract runtime stage RUN commands (not comments)
        lines = dockerfile_content.split("\n")
        runtime_run_lines = []
        in_runtime = False
        in_run = False
        for line in lines:
            if "AS runtime" in line:
                in_runtime = True
                continue
            if in_runtime:
                stripped = line.strip()
                # Skip comments
                if stripped.startswith("#"):
                    continue
                if stripped.startswith("RUN ") and "apt-get install" in stripped:
                    in_run = True
                if in_run:
                    runtime_run_lines.append(stripped)
                    if not stripped.endswith("\\"):
                        in_run = False
        apt_content = " ".join(runtime_run_lines)
        # Runtime apt-get install should NOT include build tools
        assert "build-essential" not in apt_content, "Runtime must not install build-essential"
        assert " gcc" not in apt_content, "Runtime must not install gcc"

    def test_uses_venv_from_builder(self, dockerfile_content):
        """Runtime should use venv copied from builder, not install packages."""
        assert "COPY --from=builder /opt/venv" in dockerfile_content


class TestPythonPath:
    """Verify PYTHONPATH is set for the source directory."""

    def test_pythonpath_set(self, dockerfile_content):
        """PYTHONPATH must include /app/src."""
        assert "PYTHONPATH=/app/src" in dockerfile_content


class TestHealthCheck:
    """Verify health check is configured."""

    def test_healthcheck_present(self, dockerfile_content):
        """Dockerfile must have a HEALTHCHECK instruction."""
        assert "HEALTHCHECK" in dockerfile_content

    def test_healthcheck_uses_curl(self, dockerfile_content):
        """Health check should use curl (installed in runtime stage)."""
        assert "curl" in dockerfile_content


class TestDockerIgnore:
    """Verify .dockerignore excludes non-runtime files."""

    def test_excludes_git(self, dockerignore_content):
        """Must exclude .git directory."""
        assert ".git" in dockerignore_content

    def test_excludes_tests(self, dockerignore_content):
        """Must exclude tests directory."""
        assert "tests/" in dockerignore_content

    def test_excludes_docs(self, dockerignore_content):
        """Must exclude docs directory."""
        assert "docs/" in dockerignore_content

    def test_excludes_backlog(self, dockerignore_content):
        """Must exclude backlog directory."""
        assert "backlog/" in dockerignore_content

    def test_excludes_env_files(self, dockerignore_content):
        """Must exclude .env files."""
        assert ".env" in dockerignore_content

    def test_excludes_pycache(self, dockerignore_content):
        """Must exclude __pycache__."""
        assert "__pycache__" in dockerignore_content

    def test_excludes_venv(self, dockerignore_content):
        """Must exclude .venv."""
        assert ".venv" in dockerignore_content

    def test_excludes_markdown(self, dockerignore_content):
        """Must exclude .md files (except LICENSE)."""
        assert "*.md" in dockerignore_content

    def test_keeps_license(self, dockerignore_content):
        """Must keep LICENSE.md."""
        assert "!LICENSE.md" in dockerignore_content


class TestServiceCompatibility:
    """Verify the Dockerfile works for all three service roles."""

    def test_default_cmd_is_api(self, dockerfile_content):
        """Default CMD must start the API server (uvicorn)."""
        lines = dockerfile_content.strip().split("\n")
        cmd_lines = [line for line in lines if line.strip().startswith("CMD ")]
        last_cmd = cmd_lines[-1]
        assert "uvicorn" in last_cmd

    def test_exposes_api_port(self, dockerfile_content):
        """Must EXPOSE the API port."""
        assert "EXPOSE 8000" in dockerfile_content

    def test_data_dir_exists(self, dockerfile_content):
        """Must create /app/data directory for celerybeat-schedule and logs."""
        assert "/app/data" in dockerfile_content
        assert "mkdir" in dockerfile_content

    def test_data_dir_owned_by_user(self, dockerfile_content):
        """Data dir must be owned by non-root user."""
        assert "chown" in dockerfile_content and "solstein" in dockerfile_content
