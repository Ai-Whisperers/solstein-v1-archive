from unittest.mock import patch
import pytest
from solstein.worker import run_worker

@pytest.mark.asyncio
@patch("solstein.worker.logger.error")
async def test_run_worker(mock_error_log):
    await run_worker()
    mock_error_log.assert_called_once()
