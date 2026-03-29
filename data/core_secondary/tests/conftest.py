import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio coroutine")


@pytest.fixture(autouse=True)
def mock_arq_create_pool():
    """Mocks arq.create_pool to prevent actual Redis connection during tests."""
    mock_pool = AsyncMock()
    mock_pool.enqueue_job.return_value = MagicMock() # Mock enqueue_job too
    mock_pool.ping.return_value = True # Mock ping to indicate connectivity
    mock_pool.close.return_value = None # Mock close
    with patch('orchestrator.src.core.orchestrator.create_pool', return_value=mock_pool), \
         patch('orchestrator.src.core.api.create_pool', return_value=mock_pool):
        yield mock_pool
