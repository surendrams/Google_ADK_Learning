"""Defines Brand Search Optimization Agent"""

from google.adk.agents.llm_agent import Agent

from .shared_libraries import constants

from .sub_agents.comparison.agent import comparison_root_agent
from .sub_agents.search_results.agent import search_results_agent
from .sub_agents.keyword_finding.agent import keyword_finding_agent

from . import prompt


root_agent = Agent(
    model=constants.GOOGLE_MODEL_NAME,
    name=constants.AGENT_NAME,
    description=constants.DESCRIPTION,
    instruction=prompt.ROOT_PROMPT,
    sub_agents=[
        keyword_finding_agent,
        search_results_agent,
        comparison_root_agent,
    ],
)
