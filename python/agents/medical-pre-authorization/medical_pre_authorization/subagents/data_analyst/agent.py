from google.genai import types
from google.adk import Agent

from .prompt import DATA_ANALYST_INSTRUCTION
from .tools.tools import store_pdf

data_analyst = Agent(
    model="gemini-2.5-flash",
    name="data_analyst",
    description="""Agent that analyzes the details on user insurance policy and 
   medical necessity for a pre-authorization request and creates a report on
   the same.""",
    instruction=DATA_ANALYST_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[store_pdf],
)
