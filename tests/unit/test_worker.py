from unittest.mock import MagicMock, patch
import pytest
from solstein.worker import run_worker

@pytest.mark.asyncio
@patch("solstein.worker.logger.error")
@patch("solstein.worker.get_settings")
async def test_run_worker(mock_get_settings, mock_error_log):
    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.environment = "test"
    mock_get_settings.return_value = mock_settings

    # Execute
    await run_worker()

    # Verify
    mock_get_settings.assert_called_once()
    mock_error_log.assert_called_once_with("Temporal worker disabled - Replaced by LangGraph Native StateMachine")
