import asyncio
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from dotenv import load_dotenv, find_dotenv

class CapCategory(str, Enum):
    MID = "Mid"
    LARGE = "Large"
    MEGA = "Mega"

class StockAnalysis(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol (e.g., NVDA)")
    name: str = Field(..., description="Full company name")
    high: float = Field(..., description="Today's high price in USD")
    low: float = Field(..., description="Today's low price in USD")
    gain_pct: Optional[float] = Field(None, description="Percentage gain (e.g., 16.36)")
    cap: CapCategory = Field(..., description="Market capitalization category")
    buyout_trap: bool = Field(..., description="Whether the price jump is due to an acquisition")
    rsi_14d: int = Field(..., description="14-day Relative Strength Index (0-100)", ge=0, le=100)
    strategy: str = Field(..., description="Investment strategy (e.g., Growth, Value, Rebound)")
    worth_investing: str = Field(..., description="Qualitative verdict (e.g., Yes, No, Risky)")
    recommendation: str = Field(..., description="Specific action (e.g., Strong Buy, Avoid)")
    analyst_insights_strategy: str = Field(..., description="Analyst Insight information (e.g., 'overbought','need to wait for correction')")

    # Validator to clean '$', '%', and '*' from incoming strings
    @field_validator('high', 'low', 'gain_pct', 'analyst_insights_strategy', mode='before')
    @classmethod
    def clean_financial_strings(cls, v):
        if isinstance(v, str):
            # Remove characters that prevent float conversion
            clean_v = v.replace('$', '').replace('%', '').replace('+', '').replace('*', '').strip()
            if clean_v.upper() == "N/A":
                return None
            return float(clean_v)
        return v

class DailyMarketReport(BaseModel):
    analysis_date: str
    top_gainers: List[StockAnalysis]

load_dotenv(find_dotenv())

model_name = os.getenv('GOOGLE_MODEL_NAME', 'gemini-3-flash')
current_date = datetime.now().strftime("%B %d, %Y %H:%M:%S")

# --- STEP 1: Define the Researcher Agent ---
# Its sole job is to fetch raw data and store it in 'market_raw_data'.
researcher = LlmAgent(
    name="Researcher",
    model=model_name,
    instruction=f"""
    You are a Live Market Data Specialist. Today is {current_date}.
    Your ONLY job is to find REAL-TIME market data for the top US stock gainers today, {current_date}. 
    Focus on Mid-cap, Large-cap and Mega-cap stocks.

    Find: Symbol, Company Name, High, Low, and Gain.
    Also, search for any news regarding 'buyouts' or 'mergers' or 'market movers' for these specific tickers.

    SEARCH RULES:
    - Always include the specific date '{current_date}' in your search queries.
    - Prioritize sources like 'Morningstar Movers', 'Investing.com Live', or 'Nasdaq Real-time'.
    - If you cannot find data for today, state 'Data not yet available for {current_date}' instead of giving old data.
    """,
    tools=[google_search],
    output_key="market_raw_data"  # Data is saved here in the session state
)

# --- STEP 2: Define the Analyst Agent ---
# It doesn't use tools; it only processes the data from the previous step.
analyst = LlmAgent(
    name="Analyst",
    model=model_name,
    instruction=f"""
    Analyze the stock data found in '{{{{market_raw_data}}}}'.
    
    CRITERIA:
    1. Filter: Ensure only Mid to Large-cap stocks.
    2. Buyout Trap: Flag as 'Yes' if news indicates an active acquisition.
    3. Technicals: Estimate the 14-day RSI.
    4. Try to get a maximum of 10 stocks.
    
    OUTPUT FORMAT:
    Produce a CSV format table: Symbol, Name, High, Low, Gain, Cap, Buyout Trap?, RSI, Strategy, Worth Investing, Recommendation
    """,
    output_key="market_analyzed_data"
)

# --- STEP 3: Define the StructuredOutput Agent ---
# It doesn't use tools; it only processes the data from the previous step.
structured_output = LlmAgent(
    name="StructuredOutput",
    model=model_name,
    instruction=f"""
    You are an data analyst uses the available data from '{{{{market_analyzed_data}}}} and formats the data to store in database for further processing'.
    
    Carefully review the given information, you may need to combine the text and other information for converting into the output schema.
    """,
    output_schema=DailyMarketReport
)


#stocks > $2B market cap are included.

# --- STEP 3: Create the Sequential Pipeline ---
# This acts as the "Manager" running the agents in a fixed order.
pipeline_agent = SequentialAgent(
    name="Market_Analysis_Pipeline",
    sub_agents=[researcher, analyst, structured_output],
    description="A sequential pipeline to research and analyze daily stock gainers."
)

APP_NAME = "stock_pipeline_app"
USER_ID = "surendra"
SESSION_ID = f"session_{datetime.now().strftime('%Y%m%d')}"

async def setup_runner(agent: SequentialAgent):
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
    runner = await setup_runner(pipeline_agent)
    print(f"Starting Sequential Pipeline for {current_date}...")
    
    user_query = f"Run the high-quality REAL TIME stock gainer analysis as of {current_date}."
    new_message = types.Content(role="user", parts=[types.Part(text=user_query)])
    
    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message
        ):
            # In a pipeline, we watch for the final response from the last agent (Analyst)
            if event.is_final_response():
                print("\n" + "="*40)
                print("PIPELINE ANALYSIS COMPLETE", event.author)
                print("="*40 + "\n")
                print(event.content.parts[0].text)
    except Exception as e:
        print(f"Pipeline Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
