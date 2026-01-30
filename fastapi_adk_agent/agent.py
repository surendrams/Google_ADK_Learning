from dotenv import load_dotenv, find_dotenv
from google.adk.agents import Agent

load_dotenv(find_dotenv())

# Define your simple ADK agent
root_agent = Agent(
    name="Learner_Assistant",
    # Use a lightweight Gemini model
    model="gemini-2.5-flash",
    description="A friendly assistant for new ADK developers.",
    instruction="""
        You are a cheerful and concise AI assistant that exclusively helps 
        new developers learn the Google Agent Development Kit (ADK) and FastAPI. 
        Keep your answers brief and encouraging.
    """,
    # The 'root_agent' name is required by the ADK CLI/FastAPI wrapper
)

# Export the agent to be found by the server
__all__ = ["root_agent"]
