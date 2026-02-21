from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.worker import run_worker


@pytest.mark.asyncio
@patch("solstein.worker.Worker")
@patch("solstein.worker.TemporalClient.connect", new_callable=AsyncMock)
async def test_run_worker(mock_connect, mock_worker):
    mock_w_inst = MagicMock()
    mock_w_inst.run = AsyncMock()
    mock_worker.return_value = mock_w_inst

    await run_worker()

    mock_connect.assert_called_once()
    mock_w_inst.run.assert_awaited_once()
