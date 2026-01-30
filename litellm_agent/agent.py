import os
import random

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # Keep LiteLlm as OpenRouter is a LiteLLM provider

# --- IMPORTANT ---
# 1. OPENROUTER_API_KEY: Ensure this is your key from openrouter.ai
# 2. Model String: Verify on openrouter.ai/models for the exact "gemini-2.5-flash" identifier
#                  It's often prefixed, e.g., "gemini/gemini-2.5-flash" or "google/gemini-2.5-flash"
# -----------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY environment variable not set. "
          "Please set it or replace os.getenv('OPENROUTER_API_KEY') with your actual key.")

# --- FIX: Specify OpenRouter's base URL ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Initialize the LiteLlm model via OpenRouter
# You specify the model identifier provided by OpenRouter for Gemini 2.5 Flash Lite.
model = LiteLlm(
    # This is the model identifier as listed on OpenRouter.ai for Gemini 2.5 Flash.
    # ALWAYS VERIFY THIS STRING ON OPENROUTER.AI/MODELS
    model="openrouter/google/gemini-2.5-flash", # Common identifier, but best to confirm!
    api_key=OPENROUTER_API_KEY,
    # --- This is the crucial part ---
    base_url=OPENROUTER_BASE_URL
)


def get_dad_joke():
    """
    Returns a random dad joke from a predefined list.
    """
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a fish with no eyes? Fsh!",
        "Why did the bicycle fall over? Because it was two tired!",
        "What do you get when you cross a snowman and a vampire? Frostbite!",
        "I'm reading a book about anti-gravity. It's impossible to put down!",
        "Why was the math book sad? Because it had too many problems.",
        "What's a sad strawberry called? A blueberry."
    ]
    return random.choice(jokes)


# Define the root agent
root_agent = Agent(
    name="openrouter_gemini_dad_joke_agent",
    model=model,
    description="A simple agent that tells dad jokes using Gemini 2.5 Flash Lite via OpenRouter.",
    instruction="""
    You are a helpful assistant who specializes in telling dad jokes.
    Your only capability is to tell dad jokes.
    To tell a joke, you MUST use the `get_dad_joke` tool. Always use it when asked for a joke.
    Be enthusiastic and friendly!
    """,
    tools=[get_dad_joke],
)