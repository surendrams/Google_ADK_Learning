"""Main file for the Guardian agent."""

import asyncio
from dotenv import load_dotenv, find_dotenv

from absl import app, flags
from google.adk import runners
from google.adk.agents import llm_agent
from google.genai import types

# Load environment variables before loading the plugins.
load_dotenv(find_dotenv())

from .plugins import agent_as_a_judge, model_armor
from . import tools
from . import prompts
from . import util


Agent = llm_agent.LlmAgent
LlmAsAJudge = agent_as_a_judge.LlmAsAJudge
ModelArmorSafetyFilter = model_armor.ModelArmorSafetyFilterPlugin
InMemoryRunner = runners.InMemoryRunner


USER_ID = "user"
APP_NAME = "test_app_with_plugin"
AGENT_GOOGLE_MODEL_NAME = "gemini-2.5-flash"

sub_agent = Agent(
    model=AGENT_GOOGLE_MODEL_NAME,
    instruction=prompts.SUB_AGENT_SI,
    name="sub_agent",
    tools=[tools.fib_tool, tools.io_bound_tool],
)

root_agent = Agent(
    model=AGENT_GOOGLE_MODEL_NAME,
    instruction=prompts.ROOT_AGENT_SI,
    name="main_agent",
    tools=[tools.short_sum_tool, tools.long_sum_tool],
    sub_agents=[sub_agent],
)

# Define the command-line flag using absl.flags.
FLAGS = flags.FLAGS
flags.DEFINE_enum(
    "plugin",
    "none",
    ["llm_judge", "model_armor", "none"],
    "Specify the safety plugin to enable.",
)


async def main():
    """Runs a multiturn conversation with the agent and the attached plugin."""
    # You can now access the flag's value via FLAGS.plugin.
    plugin_name = FLAGS.plugin

    plugins = []
    if plugin_name == "llm_judge":
        plugins.append(LlmAsAJudge())
        print("Using LlmAsAJudge plugin.")
    elif plugin_name == "model_armor":
        plugins.append(ModelArmorSafetyFilter())
        print("Using ModelArmorSafetyFilter plugin.")
    else:
        print("No plugin activated.")

    # Initialize plugins based on the command-line argument.
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=APP_NAME,
        plugins=plugins,
    )
    session = await runner.session_service.create_session(
        user_id=USER_ID,
        app_name=APP_NAME,
    )

    user_input = input(f"[{USER_ID}]: ")

    while user_input != "exit":
        author, message = await util.run_prompt(
            USER_ID,
            APP_NAME,
            runner,
            types.Content(role="user", parts=[types.Part.from_text(text=user_input)]),
            session_id=session.id,
        )
        print(f"[{author}]: {message}")

        user_input = input(f"[{USER_ID}]: ")


if __name__ == "__main__":
    app.run(lambda _: asyncio.run(main()))
