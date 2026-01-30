"""marketing_create_agent: for creating marketing strategies"""

from google.adk import Agent

from . import prompt

GOOGLE_MODEL_NAME = "gemini-2.5-pro"

marketing_create_agent = Agent(
    model=GOOGLE_MODEL_NAME,
    name="marketing_create_agent",
    instruction=prompt.MARKETING_CREATE_PROMPT,
    output_key="marketing_create_output",
)
