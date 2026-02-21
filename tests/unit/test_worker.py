import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from solstein.worker import run_worker


@pytest.mark.asyncio
@patch("solstein.worker.Worker")
@patch("solstein.worker.TemporalClient.connect")
@patch("solstein.worker.get_settings")
async def test_run_worker(mock_get_settings, mock_connect, mock_worker):
    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.temporal.host_url = "localhost:7233"
    mock_settings.temporal.namespace = "default"
    mock_settings.temporal.api_key = "test_key"
    mock_get_settings.return_value = mock_settings

    mock_client = AsyncMock()
    mock_connect.return_value = mock_client

    mock_worker_instance = AsyncMock()
    mock_worker.return_value = mock_worker_instance

    # Execute
    await run_worker()

    # Verify
    mock_get_settings.assert_called_once()
    mock_connect.assert_called_once_with(
        "localhost:7233",
        namespace="default",
        api_key="test_key",
    )
    mock_worker.assert_called_once()
    mock_worker_instance.run.assert_called_once()
