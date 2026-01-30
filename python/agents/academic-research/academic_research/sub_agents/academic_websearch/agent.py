"""Academic_websearch_agent for finding research papers using search tools."""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

GOOGLE_MODEL_NAME = "gemini-2.5-pro"


academic_websearch_agent = Agent(
    model=GOOGLE_MODEL_NAME,
    name="academic_websearch_agent",
    instruction=prompt.ACADEMIC_WEBSEARCH_PROMPT,
    output_key="recent_citing_papers",
    tools=[google_search],
)
