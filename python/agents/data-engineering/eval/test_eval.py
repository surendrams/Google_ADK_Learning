"""Basic evaluation for Financial Advisor"""

import pathlib

import dotenv
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv(find_dotenv())


@pytest.mark.asyncio
async def test_all():
    """Test the agent's basic ability on a few examples."""
    print("Running evaluate")
    await AgentEvaluator.evaluate(
        "data_engineering_agent",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=5,
    )
