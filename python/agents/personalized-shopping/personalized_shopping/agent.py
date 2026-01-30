from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools.search import search
from .tools.click import click

from .prompt import personalized_shopping_agent_instruction

root_agent = Agent(
    model="gemini-2.5-flash",
    name="personalized_shopping_agent",
    instruction=personalized_shopping_agent_instruction,
    tools=[
        FunctionTool(
            func=search,
        ),
        FunctionTool(
            func=click,
        ),
    ],
)
