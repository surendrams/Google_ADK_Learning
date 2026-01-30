import asyncio
import os
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ValidationInfo

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# --- CONFIGURATION ---
APP_NAME = "stock_pipeline_app"
USER_ID = "surendra"
SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d')}"
MODEL_NAME = os.getenv('GOOGLE_MODEL_NAME', 'gemini-3-flash')
CURRENT_DATE = datetime.now().strftime("%B %d, %Y")

# --- 1. PYDANTIC MODELS WITH VALIDATION ---
class CapCategory(str, Enum):
    MID = "Mid"
    LARGE = "Large"
    MEGA = "Mega"

class StockAnalysis(BaseModel):
    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Company name")
    day_high: float = Field(..., description="Intraday High price")
    day_low: float = Field(..., description="Intraday Low price")
    day_open: float = Field(..., description="Day Open price")
    day_close: float = Field(..., description="Day Close price")
    gain_pct: Optional[float] = Field(None, description="Percentage gain")
    cap: CapCategory = Field(..., description="Cap category")
    buyout_trap: bool = Field(..., description="Is jump due to acquisition?")
    rsi_14d: int = Field(..., description="RSI (0-100)", ge=0, le=100)
    strategy: str = Field(..., description="Investment strategy")
    worth_investing: str = Field(..., description="Verdict (Yes/No/Risky)")
    recommendation: str = Field(..., description="Specific action")
    analyst_insights_strategy: str = Field(..., description="Brief insight/warning")

    @field_validator('day_high')
    @classmethod
    def validate_range(cls, v: float, info: ValidationInfo) -> float:
        """Generic validator to stop halluncinated prices."""
        if 'day_low' in info.data and v < info.data['day_low']:
            # This triggers if the LLM tries to give a High lower than the Low
            raise ValueError(f"Logic Error: High ({v}) cannot be lower than Low ({info.data['day_low']})")
        return v

class DailyMarketReport(BaseModel):
    analysis_date: str
    top_gainers: List[StockAnalysis]

# --- 2. AGENT DEFINITIONS ---

# RESEARCHER: This agent has the tools and the mission to find RAW accuracy.
list_finder = LlmAgent(
    name="list_finder",
    model=MODEL_NAME,
    instruction=f"""
    Today is {CURRENT_DATE}. 
    1. Search for Top 10 US stock gainers (> $2B cap) for today.
    2. For each ticker, perform a targeted search for: '[Ticker] intraday price range {CURRENT_DATE}'.
    3. You MUST extract the specific 'Day High', 'Day Low', 'Day Open' and 'Day Close'. 
    4. If you find data for a previous date, mark it 'N/A'. DO NOT guess.
    """,
    tools=[google_search],
    output_key="raw_ticker_list"
)

news_researcher = LlmAgent(
    name="news_researcher",
    model=MODEL_NAME,
    instruction=f"Find buyout/merger/acquisition news for today's ({CURRENT_DATE}) market movers.",
    tools=[google_search],
    output_key="raw_news_data"
)

# PARALLEL: Executes research simultaneously
parallel_research = ParallelAgent(
    name="parallel_research",
    sub_agents=[list_finder, news_researcher]
)

# ANALYST: This agent organizes data into the Final Pydantic Schema.
# Note: It does NOT have tools; its job is pure reasoning on the research data.
market_analyst = LlmAgent(
    name="market_analyst",
    model=MODEL_NAME,
    instruction=f"""
    Process '{{{{raw_ticker_list}}}}' and '{{{{raw_news_data}}}}'.
    
    1. Map the Day High/Low and Gain from the research. 
    2. If a value is missing, use 0.0. 
    3. Determine if any stock is a 'Buyout Trap' based on the news data.
    4. Estimate the 14-day RSI.
    
    Produce a valid DailyMarketReport JSON for {CURRENT_DATE}.
    """,
    output_schema=DailyMarketReport,
    output_key="final_report"
)

# --- 3. PIPELINE ORCHESTRATION ---
pipeline_agent = SequentialAgent(
    name="stock_analysis_pipeline",
    sub_agents=[parallel_research, market_analyst]
)

# --- 4. EXECUTION LOGIC ---
async def setup_runner(agent):
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    return Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

async def run_analysis():
    runner = await setup_runner(pipeline_agent)
    
    print(f"--- Launching Market Pipeline for {CURRENT_DATE} ---")
    print("Step 1: Deep Research (Searching High/Low/News)...")
    
    user_query = f"Provide the structured daily market report for {CURRENT_DATE}."
    new_message = types.Content(role="user", parts=[types.Part(text=user_query)])
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message
        ):
            if event.is_final_response():
                print("\n--- FINAL STRUCTURED REPORT ---")
                print(event.content.parts[0].text)
    except Exception as e:
        print(f"\nPipeline Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
