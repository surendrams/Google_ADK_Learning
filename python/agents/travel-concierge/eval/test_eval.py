"""Basic evaluation of the travel concierge agent."""

import pathlib

import dotenv
from google.adk.evaluation import AgentEvaluator
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv(find_dotenv())


@pytest.mark.asyncio
async def test_inspire():
    """Test the agent's basic ability on a few examples."""
    await AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/inspire.test.json"),
        num_runs=4,
    )


@pytest.mark.asyncio
async def test_pretrip():
    """Test the agent's basic ability on a few examples."""
    await AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/pretrip.test.json"),
        num_runs=4,
    )


@pytest.mark.asyncio
async def test_intrip():
    """Test the agent's basic ability on a few examples."""
    await AgentEvaluator.evaluate(
        "travel_concierge",
        str(pathlib.Path(__file__).parent / "data/intrip.test.json"),
        num_runs=4,
    )
