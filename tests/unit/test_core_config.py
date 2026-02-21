import logging
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from solstein import __version__, InterceptHandler
from solstein.config import (
    DatabaseConfig,
    RedisConfig,
    APIConfig,
    SecurityConfig,
    LoggingConfig,
    DataConfig,
    Settings,
    get_settings,
    configure_logging,
    create_env_template,
)
from solstein.core.repositories import CompanyRepository
from solstein.core.supabase_client import SupabaseConnection, get_supabase

# --- __init__.py logging tests ---
def test_intercept_handler_unknown_level():
    handler = InterceptHandler()
    record = logging.LogRecord(
        name="test", level=999, pathname="test.py", lineno=1,
        msg="Test message", args=(), exc_info=None
    )
    # Should catch ValueError and use levelno
    with patch("solstein.logger.opt") as mock_opt:
        mock_log = MagicMock()
        mock_opt.return_value = mock_log
        handler.emit(record)
        mock_log.log.assert_called_with(999, "Test message")

def test_intercept_handler_depth():
    handler = InterceptHandler()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=logging.__file__, lineno=1,
        msg="Test message", args=(), exc_info=None
    )
    with patch("solstein.logger.opt") as mock_opt:
        mock_log = MagicMock()
        mock_opt.return_value = mock_log
        handler.emit(record)
        # Just asserts it passes through without error, depth should be > 2
        mock_opt.assert_called()

def test_intercept_handler_standard_logging():
    # Calling logging.info directly will put logging.__file__ in the frame stack, 
    # executing the depth-traversal while loop in InterceptHandler.
    with patch("solstein.logger.opt") as mock_opt:
        mock_log = MagicMock()
        mock_opt.return_value = mock_log
        logging.getLogger("test").info("Trigger while loop")
        mock_opt.assert_called()

# --- Config Tests ---
def test_database_config_invalid_url():
    with pytest.raises(Exception, match="empty"):
        DatabaseConfig(url="")

def test_database_config_valid_url():
    db = DatabaseConfig(url="valid")
    assert db.url == "valid"

def test_redis_config_properties():
    redis = RedisConfig(url="redis://localhost:6379/0")
    assert redis.host == "localhost"
    assert redis.port == 6379

    redis_no_port = RedisConfig(url="redis://localhost/0")
    assert redis_no_port.port == 6379

def test_api_config_base_url():
    api = APIConfig(host="127.0.0.1", port=8000, api_prefix="/api/v1")
    assert api.base_url == "http://127.0.0.1:8000/api/v1"

@patch("solstein.config.logger.warning")
def test_security_config_default_warning(mock_warning):
    config = SecurityConfig(secret_key="change-me-in-production")
    mock_warning.assert_called_with("Using default secret key - change in production!")

def test_logging_config_invalid_level():
    with pytest.raises(Exception, match="Log level must be one of"):
        LoggingConfig(level="INVALID")

def test_logging_config_valid_level():
    log = LoggingConfig(level="DeBuG")
    assert log.level == "DEBUG"

def test_data_config_resolve_paths():
    config = DataConfig(data_dir="relative/data", cache_dir=Path("relative/cache"), export_dir="relative/export")
    assert config.data_dir.is_absolute()
    assert config.cache_dir.is_absolute()
    assert config.export_dir.is_absolute()

@patch("solstein.config.logger.warning")
@patch("solstein.config.Path.exists")
def test_settings_load_no_env(mock_exists, mock_warning):
    mock_exists.return_value = False
    settings = Settings.load()
    mock_warning.assert_called_with("No .env file found, using defaults")

def test_settings_get_database_url():
    settings = Settings()
    settings.database.url = "postgresql://user:pass@localhost:5432/solstein"
    assert settings.get_database_url(test=False) == "postgresql://user:pass@localhost:5432/solstein"
    assert settings.get_database_url(test=True) == "postgresql://user:pass@localhost:5432_test/solstein"

@patch("solstein.config.logger.warning")
@patch("solstein.config.Settings.load")
@patch("solstein.config.Path.exists")
def test_get_settings_no_env(mock_exists, mock_load, mock_warning):
    mock_exists.return_value = False
    mock_load.return_value = Settings()
    get_settings.cache_clear()
    settings = get_settings()
    mock_warning.assert_called_with("No .env file found, using defaults")

def test_configure_logging(tmp_path):
    settings = Settings()
    settings.logging.file_path = tmp_path / "test.log"
    settings.logging.level = "DEBUG"
    configure_logging(settings)
    assert settings.logging.file_path.parent.exists()

def test_create_env_template(tmp_path):
    out = tmp_path / ".env.example"
    create_env_template(out)
    assert out.exists()
    assert "ENVIRONMENT=development" in out.read_text()

# --- Core Repositories Tests ---
def test_company_repository_abstract_methods():
    class DummyRepo(CompanyRepository):
        def get_all(self, limit=None, offset=0, filters=None): return super().get_all(limit, offset, filters)
        def get_by_id(self, company_id): return super().get_by_id(company_id)
        def save(self, company): return super().save(company)
        def delete(self, company_id): return super().delete(company_id)
        def search(self, query, field="name"): return super().search(query, field)
    
    # Just calling to cover the `pass` inside the abstract methods
    repo = DummyRepo()
    assert repo.get_all() is None
    assert repo.get_by_id("1") is None
    assert repo.save(None) is None
    assert repo.delete("1") is None
    assert repo.search("query") is None

# --- Supabase Client Tests ---
@patch("solstein.core.supabase_client.create_client")
@patch("solstein.core.supabase_client.get_settings")
def test_get_supabase_client(mock_get_settings, mock_create_client):
    SupabaseConnection._instance = None
    mock_settings = MagicMock()
    mock_settings.supabase.url = "https://test.supabase.co"
    mock_settings.supabase.key = "testkey"
    mock_get_settings.return_value = mock_settings
    
    client = get_supabase()
    mock_create_client.assert_called_once_with("https://test.supabase.co", "testkey")
    
    # Second call should return cached instance
    client2 = get_supabase()
    assert mock_create_client.call_count == 1
    assert client is client2
    SupabaseConnection._instance = None

@patch("solstein.core.supabase_client.get_settings")
def test_get_supabase_client_missing_config(mock_get_settings):
    SupabaseConnection._instance = None
    mock_settings = MagicMock()
    mock_settings.supabase.url = ""
    mock_settings.supabase.key = ""
    mock_get_settings.return_value = mock_settings
    
    with pytest.raises(ValueError, match="Missing Supabase configuration"):
        get_supabase()
