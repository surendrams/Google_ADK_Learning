from google.adk.agents import Agent

from .prompt import agent_instruction
from .tools.tools import (
    get_current_date,
    langchain_tool,
    mcp_tools,
    search_tool,
    toolbox_tools,
)


# Build tools list, filtering out empty/None values
tools = [get_current_date, search_tool, langchain_tool]
if toolbox_tools:  # Only add if not empty list
    tools.extend(toolbox_tools)
if mcp_tools is not None:  # Only add if not None
    tools.append(mcp_tools)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="software_assistant",
    instruction=agent_instruction,
    tools=tools,
)
