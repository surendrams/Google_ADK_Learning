import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search, AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

model_name = os.getenv('GOOGLE_MODEL_NAME','gemini-3-flash-preview')

# 1. FIX: Added specific temporal instructions to the specialist
# This ensures it appends the current date to every search query.
current_date = datetime.now().strftime("%B %d, %Y")

search_agent = LlmAgent(
    name="search_specialist",
    model=model_name,
    instruction=f"""
    You are a Live Market Data Specialist. Today is {current_date}.
    Your ONLY job is to find REAL-TIME market data.
    
    SEARCH RULES:
    - Always include the specific date '{current_date}' in your search queries.
    - Prioritize sources like 'Morningstar Movers', 'Investing.com Live', or 'Nasdaq Real-time'.
    - If you cannot find data for today, state 'Data not yet available for {current_date}' instead of giving old data.
    """,
    tools=[google_search]
)

# 2. FIX: Added 'Verbatim' constraint to the main agent
market_agent = LlmAgent(
    name="market_agent",
    model=model_name,
    instruction=f"""
    You are a professional U.S. Stock Market Analyst. Today's date is {current_date}.
    
    TASK:
    - Request the TOP GAINERS for {current_date} from the 'search_specialist'.
    - DO NOT use your internal knowledge for stock prices; only use the search results.
    - Filter for 'Quality' stocks (Mid/Large-Cap > $2B).
    
    OUTPUT:
    Provide a Markdown table: Symbol, Name, High, Low, Gain, Cap, Buyout Trap?, RSI, Strategy.
    """,
    tools=[AgentTool(agent=search_agent)]
)

APP_NAME = "stock_market_agent"
USER_ID = "surendra"
SESSION_ID = "daily_market_session"

async def setup_runner(agent: LlmAgent):
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    return Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

async def run_analysis():
    runner = await setup_runner(market_agent)

    print(f"Agent is analyzing market data for {datetime.now()}...")
    
    user_query = f"Provide the Top 10 High-Quality U.S. Stock Gainers report as of {datetime.now()}."
    new_message = types.Content(role="user", parts=[types.Part(text=user_query)])
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message
        ):
            if event.is_final_response():
                print("\n--- DAILY MARKET INTELLIGENCE REPORT ---")
                print(event.content.parts[0].text)
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_analysis())