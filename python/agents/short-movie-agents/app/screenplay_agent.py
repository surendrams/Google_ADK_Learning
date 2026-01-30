import logging

from google.adk.agents import Agent

from .utils.utils import load_prompt_from_file

# Set logging
logger = logging.getLogger(__name__)

# Configuration constants
GOOGLE_MODEL_NAME = "gemini-2.5-flash"
DESCRIPTION = "Agent responsible for writing a screenplay based on a story"

# --- Screenplay Agent ---
screenplay_agent = None
try:
    screenplay_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=GOOGLE_MODEL_NAME,
        name="screenplay_agent",
        description=(DESCRIPTION),
        instruction=load_prompt_from_file("screenplay_agent.txt"),
        output_key="screenplay",
    )
    logger.info(f"✅ Agent '{screenplay_agent.name}' created using model '{GOOGLE_MODEL_NAME}'.")
except Exception as e:
    logger.error(
        f"❌ Could not create Screenplay agent. Check API Key ({GOOGLE_MODEL_NAME}). Error: {e}"
    )
