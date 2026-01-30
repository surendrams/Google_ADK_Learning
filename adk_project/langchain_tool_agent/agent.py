import os
import sys

sys.path.append("..")
import google.cloud.logging
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent
from google.adk.tools.langchain_tool import LangchainTool  # import
from google.adk.agents.callback_context import CallbackContext

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

root_agent = Agent(
    name="lanchgain_tool_agent",
    model=os.getenv("GOOGLE_MODEL_NAME"),
    description="Answers questions using Wikipedia.",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    instruction="""Research the topic suggested by the user.
    Share the information you have found with the user.""",
    # Add the LangChain Wikipedia tool below
)
