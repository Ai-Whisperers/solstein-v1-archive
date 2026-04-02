"""Tests for STORY-093: Celery Worker Service in docker-compose.

Validates that docker-compose.yml defines the correct service topology
with proper dependencies, health checks, and queue assignments.
"""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def compose_config():
    """Load and parse docker-compose.yml."""
    compose_path = PROJECT_ROOT / "docker-compose.yml"
    assert compose_path.exists(), f"docker-compose.yml not found at {compose_path}"
    with open(compose_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def prod_override():
    """Load and parse docker-compose.prod.yml."""
    prod_path = PROJECT_ROOT / "docker-compose.prod.yml"
    assert prod_path.exists(), f"docker-compose.prod.yml not found at {prod_path}"
    with open(prod_path) as f:
        return yaml.safe_load(f)


class TestWorkerServiceExists:
    """Verify the worker service is defined with correct configuration."""

    def test_worker_service_defined(self, compose_config):
        """Worker service must be present in docker-compose."""
        assert "worker" in compose_config["services"]

    def test_worker_uses_same_build_as_api(self, compose_config):
        """Worker must use the same image as API (single Dockerfile)."""
        services = compose_config["services"]
        # Both should use build: . (same Dockerfile)
        assert services["worker"].get("build") == services["api"].get("build")

    def test_worker_command_includes_all_queues(self, compose_config):
        """Worker command must listen on all 4 queues."""
        worker = compose_config["services"]["worker"]
        command = worker.get("command", "")
        for queue in ["default", "scoring", "export", "enrichment"]:
            assert queue in command, f"Queue '{queue}' missing from worker command"

    def test_worker_command_enables_events(self, compose_config):
        """Worker must have --events flag for Flower monitoring."""
        worker = compose_config["services"]["worker"]
        command = worker.get("command", "")
        assert "--events" in command

    def test_worker_depends_on_db_and_redis(self, compose_config):
        """Worker must depend on db and redis with health check conditions."""
        worker = compose_config["services"]["worker"]
        depends = worker.get("depends_on", {})
        assert "db" in depends
        assert "redis" in depends
        assert depends["db"].get("condition") == "service_healthy"
        assert depends["redis"].get("condition") == "service_healthy"

    def test_worker_has_health_check(self, compose_config):
        """Worker must have a health check using celery inspect ping."""
        worker = compose_config["services"]["worker"]
        healthcheck = worker.get("healthcheck", {})
        assert healthcheck, "Worker must have a healthcheck"
        test_cmd = (
            healthcheck.get("test", [""])[1]
            if isinstance(healthcheck.get("test"), list)
            else healthcheck.get("test", "")
        )
        assert "inspect ping" in str(test_cmd) or "celery" in str(test_cmd)

    def test_worker_restart_policy(self, compose_config):
        """Worker must have unless-stopped restart policy."""
        worker = compose_config["services"]["worker"]
        assert worker.get("restart") == "unless-stopped"

    def test_worker_has_memory_limit(self, compose_config):
        """Worker must have a memory limit to prevent OOM."""
        worker = compose_config["services"]["worker"]
        deploy = worker.get("deploy", {})
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})
        assert "memory" in limits, "Worker must have a memory limit"

    def test_worker_has_distinct_container_name(self, compose_config):
        """Worker must have distinct container name for log filtering."""
        services = compose_config["services"]
        worker_name = services["worker"].get("container_name", "")
        api_name = services["api"].get("container_name", "")
        assert worker_name != api_name
        assert worker_name, "Worker must have an explicit container_name"

    def test_worker_uses_env_file(self, compose_config):
        """Worker must use shared env_file (DRY config)."""
        worker = compose_config["services"]["worker"]
        env_file = worker.get("env_file", [])
        assert env_file, "Worker must use env_file for shared configuration"


class TestBeatServiceExists:
    """Verify the Beat scheduler is defined as a singleton."""

    def test_beat_service_defined(self, compose_config):
        """Beat service must be present in docker-compose."""
        assert "beat" in compose_config["services"]

    def test_beat_is_singleton(self, compose_config):
        """Beat must enforce replicas: 1."""
        beat = compose_config["services"]["beat"]
        deploy = beat.get("deploy", {})
        assert deploy.get("replicas") == 1, "Beat MUST be a singleton (replicas: 1)"

    def test_beat_persists_schedule(self, compose_config):
        """Beat command must use --schedule flag for persistence."""
        beat = compose_config["services"]["beat"]
        command = beat.get("command", "")
        assert "--schedule" in command

    def test_beat_uses_pidfile(self, compose_config):
        """Beat must use pidfile to prevent duplicate starts."""
        beat = compose_config["services"]["beat"]
        command = beat.get("command", "")
        assert "--pidfile" in command


class TestFlowerServiceExists:
    """Verify Flower monitoring service configuration."""

    def test_flower_service_defined(self, compose_config):
        """Flower service must be present in docker-compose."""
        assert "flower" in compose_config["services"]

    def test_flower_has_auth(self, compose_config):
        """Flower must have basic auth configured."""
        flower = compose_config["services"]["flower"]
        env = flower.get("environment", {})
        auth_configured = any("AUTH" in str(k) for k in env)
        assert auth_configured, "Flower must have authentication configured"

    def test_flower_in_monitoring_profile(self, compose_config):
        """Flower should be in the monitoring profile (opt-in)."""
        flower = compose_config["services"]["flower"]
        profiles = flower.get("profiles", [])
        assert "monitoring" in profiles

    def test_flower_depends_on_redis_and_worker(self, compose_config):
        """Flower must depend on redis and worker."""
        flower = compose_config["services"]["flower"]
        depends = flower.get("depends_on", {})
        assert "redis" in depends
        assert "worker" in depends

    def test_flower_has_persistent_db(self, compose_config):
        """Flower must persist task history via volume."""
        flower = compose_config["services"]["flower"]
        volumes = flower.get("volumes", [])
        assert volumes, "Flower must have a volume for persistent task history"


class TestInfrastructureServices:
    """Verify db and redis services."""

    def test_db_service_defined(self, compose_config):
        """PostgreSQL service must be present."""
        assert "db" in compose_config["services"]

    def test_db_has_healthcheck(self, compose_config):
        """DB must have a health check for depends_on conditions."""
        db = compose_config["services"]["db"]
        assert db.get("healthcheck"), "DB must have a healthcheck"

    def test_redis_service_defined(self, compose_config):
        """Redis service must be present."""
        assert "redis" in compose_config["services"]

    def test_redis_has_healthcheck(self, compose_config):
        """Redis must have a health check for depends_on conditions."""
        redis = compose_config["services"]["redis"]
        assert redis.get("healthcheck"), "Redis must have a healthcheck"


class TestProductionOverride:
    """Verify docker-compose.prod.yml overrides."""

    def test_prod_worker_replicas(self, prod_override):
        """Production override should scale workers to 2+."""
        worker = prod_override["services"]["worker"]
        replicas = worker.get("deploy", {}).get("replicas", 1)
        assert replicas >= 2, "Production should scale workers"

    def test_prod_beat_singleton(self, prod_override):
        """Production override must keep beat at replicas: 1."""
        beat = prod_override["services"]["beat"]
        replicas = beat.get("deploy", {}).get("replicas")
        assert replicas == 1, "Beat must be singleton even in production"

    def test_prod_hides_db_port(self, prod_override):
        """Production override should not expose DB port."""
        db = prod_override["services"]["db"]
        assert db.get("ports") == [], "DB port should not be exposed in production"

    def test_prod_hides_redis_port(self, prod_override):
        """Production override should not expose Redis port."""
        redis = prod_override["services"]["redis"]
        assert redis.get("ports") == [], "Redis port should not be exposed in production"


class TestCeleryConfigEvents:
    """Verify celery_config.py has task events enabled."""

    def test_worker_send_task_events_enabled(self):
        """celery_config.py must enable worker_send_task_events."""
        config_path = PROJECT_ROOT / "src" / "solstein" / "celery_config.py"
        content = config_path.read_text()
        assert "worker_send_task_events=True" in content

    def test_task_send_sent_event_enabled(self):
        """celery_config.py must enable task_send_sent_event."""
        config_path = PROJECT_ROOT / "src" / "solstein" / "celery_config.py"
        content = config_path.read_text()
        assert "task_send_sent_event=True" in content


class TestStartCeleryWorkersScript:
    """Verify the shell script has local-dev-only header."""

    def test_script_has_local_dev_warning(self):
        """start_celery_workers.sh must warn it's for local dev only."""
        script_path = PROJECT_ROOT / "scripts" / "services" / "start_celery_workers.sh"
        content = script_path.read_text()
        assert "LOCAL DEVELOPMENT ONLY" in content
        assert "docker compose" in content.lower() or "docker-compose" in content.lower()
