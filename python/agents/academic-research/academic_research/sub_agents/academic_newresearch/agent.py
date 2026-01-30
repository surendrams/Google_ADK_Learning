"""Academic_newresearch_agent for finding new research lines"""

from google.adk import Agent

from . import prompt

GOOGLE_MODEL_NAME = "gemini-2.5-pro"

academic_newresearch_agent = Agent(
    model=GOOGLE_MODEL_NAME,
    name="academic_newresearch_agent",
    instruction=prompt.ACADEMIC_NEWRESEARCH_PROMPT,
)
