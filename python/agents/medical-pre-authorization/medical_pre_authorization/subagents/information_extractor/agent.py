from google import genai
from google.adk.agents import Agent
from google.genai import types

from .prompt import INFORMATION_EXTRACTOR_INSTRUCTION
from .tools.tools import (
    extract_treatment_name,
    extract_policy_information,
    extract_medical_details,
)


information_extractor = Agent(
    model="gemini-2.5-flash",
    name="information_extractor",
    description="""Agent that extracts the details on user insurance policy and
   medical necessity for a pre-authorization request from documents provided 
   by the user.""",
    instruction=INFORMATION_EXTRACTOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[extract_treatment_name, extract_policy_information, extract_medical_details],
)
