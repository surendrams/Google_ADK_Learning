"""Analytics Agent: generate nl2py and use code interpreter to run the code."""

import os

from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor

from .prompts import return_instructions_analytics

analytics_agent = Agent(
    model=os.getenv("ANALYTICS_AGENT_GOOGLE_MODEL_NAME", ""),
    name="analytics_agent",
    instruction=return_instructions_analytics(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)
