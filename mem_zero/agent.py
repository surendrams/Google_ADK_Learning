import asyncio
import warnings
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mem0 import MemoryClient
from dotenv import load_dotenv

# 1. Suppress the internal library deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

# Initialize Mem0 client
mem0 = MemoryClient()

# Define memory function tools
def search_memory(query: str, user_id: str) -> dict:
    """Search through past conversations and memories"""
    filters = {"user_id": user_id}
    memories = mem0.search(query, filters=filters)
    if memories.get('results', []):
        memory_list = memories['results']
        memory_context = "\n".join([f"- {mem['memory']}" for mem in memory_list])
        return {"status": "success", "memories": memory_context}
    return {"status": "no_memories", "message": "No relevant memories found"}

def save_memory(content: str, user_id: str) -> dict:
    """Save important information to memory"""
    try:
        result = mem0.add([{"role": "user", "content": content}], user_id=user_id)
        return {"status": "success", "message": "Information saved to memory", "result": result}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save memory: {str(e)}"}

# Create agent with memory capabilities
personal_assistant = Agent(
    name="personal_assistant",
    model="gemini-2.0-flash",
    instruction="""You are a helpful personal assistant with memory capabilities.
    Use the search_memory function to recall past conversations and user preferences.
    Use the save_memory function to store important information about the user.
    Always personalize your responses based on available memory.""",
    description="A personal assistant that remembers user preferences and past interactions",
    tools=[search_memory, save_memory]
)

async def chat_with_agent(user_input: str, user_id: str) -> str:
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="memory_assistant",
        user_id=user_id,
        session_id=f"session_{user_id}"
    )
    
    # The Runner handles the tool execution loop automatically
    runner = Runner(agent=personal_assistant, app_name="memory_assistant", session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=user_input)])
    events = runner.run(user_id=user_id, session_id=session.id, new_message=content)

    final_text = []

    for event in events:
        # Check if the event contains content and parts
        if event.content and event.content.parts:
            # 2. FIX: Iterate through all parts to find text, avoiding the "non-text parts" warning
            for part in event.content.parts:
                if part.text:
                    final_text.append(part.text)
                
                # If you want to see what the agent is doing behind the scenes:
                if part.function_call:
                    print(f"--- Agent calling tool: {part.function_call.name} ---")

        if event.is_final_response():
            # Return all collected text joined together
            return "\n".join(final_text) if final_text else "No text response generated."

    return "No response generated"

# Example usage
if __name__ == "__main__":
    # response = asyncio.run(chat_with_agent(
    #     "I love Italian food and I'm planning a trip to Rome next month",
    #     user_id="alice"
    # ))
    # print("-" * 30)
    # print(f"FINAL RESPONSE:\n{response}")

    response = asyncio.run(chat_with_agent(
        "Do you know my travel plan and favorite food",
        user_id="alice"
    ))
    print("-" * 30)
    print(f"FINAL RESPONSE:\n{response}")