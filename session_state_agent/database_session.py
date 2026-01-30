import uuid
import os
from dotenv import load_dotenv, find_dotenv
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


async def main():
    load_dotenv(find_dotenv())

    model = LiteLlm(
    model="openrouter/mistralai/devstral-2512:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),)

    database_state_agent = Agent(
        name="database_state_agent",
        model=model,
        description="Question answering agent",
        instruction="""
            You are a helpful assistant that answers questions about the user's preferences.

            Here is some information about the user:
            Name: 
            {user_name}
            Preferences: 
            {user_preferences} """,
    )

    # Create a new Session service to store state.
    database_service = DatabaseSessionService("sqlite+aiosqlite:///./adk_advanced_tools/demo.db")

    initial_state = {
        "user_name": "Surendra",
        "user_preferences": """I like to play Pickleball, Disc Golf, and Tennis.
            My favorite food is Mexican.
            My favorite TV show is Game of Thrones.
            Loves it when people like and subscribe to his YouTube channel.""",
    }

    # Create new Session
    APP_NAME = "Meera"
    USER_ID = "Surendra"
    SESSION_ID = str(uuid.uuid4())

    stateful_session = await database_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, state=initial_state, session_id=SESSION_ID
    )

    print("CREATED NEW SESSION:")
    print(f"\nSession ID: {SESSION_ID}")

    runner = Runner(
        app_name=APP_NAME,
        agent=database_state_agent,
        session_service=database_service,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Surendra's favorite food?")]
    )

    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response: {event.content.parts[0].text}")

    print("==== Session Event Exploration ====")
    session = await database_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # Log final Session state
    print("=== Final Session State ===")
    assert session is not None, "Failed to retrieve the session we just created."
    for key, value in session.state.items():
        print(f"{key}: {value}")


# Start the asynchronous event loop
if __name__ == "__main__":
    asyncio.run(main())
