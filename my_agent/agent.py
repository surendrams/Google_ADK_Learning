import os
from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from typing import Dict, Any, ClassVar, Type
from pydantic import BaseModel, Field
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext # Needed for the signature

from google.adk.models.lite_llm import LiteLlm

load_dotenv(find_dotenv())

# https://docs.litellm.ai/docs/providers/openrouter
model = LiteLlm(
    model="openrouter/mistralai/devstral-2512:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

class BillContent(BaseModel):
    line_item: str = Field(
        description="The line item from the bill. Should be concise and descriptive."
    )
    amount: int = Field(
        description="The amount against the line item. Should be well-formatted upto decimals."
    )


# ----------------------
# 1. FUNCTION TOOL
# ----------------------

# NOTE: No special imports needed other than the standard ones

def calculate_tip(bill_amount: float, tip_percentage: float = 0.15) -> dict:
    """
    Calculates the tip amount and the total bill.

    Args:
        bill_amount (float): The initial cost of the bill.
        tip_percentage (float): The percentage to calculate the tip (e.g., 0.15 for 15%). 
                                Defaults to 0.15.

    Returns:
        dict: A dictionary containing 'tip_amount' and 'total_bill'.
    """
    tip = bill_amount * tip_percentage
    total = bill_amount + tip
    
    return {
        "tip_amount": round(tip, 2),
        "total_bill": round(total, 2)
    }

# Agent Registration: Pass the function directly
# tools=[calculate_tip]

# ----------------------
# 2A. DEFINE INPUT SCHEMA
# ----------------------
class GreetingInput(BaseModel):
    """The input schema for the GreetingTool."""
    # Field description is used by the LLM
    name: str = Field(..., description="The name of the person to greet.")
    language: str = Field("English", description="The language to use for the greeting.")

# ----------------------
# 2B. BASE TOOL CLASS
# ----------------------
class SimpleGreetingTool(BaseTool):
    """
    A BaseTool example that generates a greeting message.
    """
    
    # ⬅️ CRITICAL for 1.19.0: Declare the input schema class variable
    input_schema: ClassVar[Type[BaseModel]] = GreetingInput
    
    # CRITICAL for 1.19.0: Explicitly satisfy the BaseTool constructor
    def __init__(self):
        super().__init__(
            name="simple_greeting_tool", 
            description="Generates a customized greeting in a specified language."
        )

    async def run_async(
        self,
        *,
        args: GreetingInput, # Args are typed as the Pydantic model
        tool_context: ToolContext,
    ) -> Dict[str, Any]:
        """Tool execution logic."""
        
        greetings = {
            "English": f"Hello, {args.name}!",
            "Spanish": f"¡Hola, {args.name}!",
            "French": f"Bonjour, {args.name}!",
        }
        
        # Returns the result the LLM will see
        return {"greeting_message": greetings.get(args.language, greetings["English"])}

# Agent Registration: Pass the tool instance
# tools=[SimpleGreetingTool()]

# Agent setup
root_agent = LlmAgent(
    model=model,
    name="two_tool_agent",
    instruction="You are an assistant. Use the 'calculate_tip' tool for math and the 'simple_greeting_tool' for greetings.",
    tools=[
        # Function Tool: Pass the function itself
        calculate_tip, 
        # Base Tool: Pass an instance of the class
        SimpleGreetingTool() 
    ], 
)
