from __future__ import annotations
import os
import sys
import warnings
import uvicorn
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Suppress experimental warnings from Google ADK
warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*")

# Add the current directory to the path to import agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import root_agent

# --- Configuration ---
# This directory contains the agent.py file
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# For the web dashboard, point to the parent directory that contains this package
AGENTS_PARENT_DIR = os.path.dirname(AGENT_DIR)

# Create in-memory session service (no database required)
session_service = InMemorySessionService()

# 1. Create the FastAPI App using the ADK Helper
# get_fast_api_app automatically adds routes like /run, /run_sse, /config, etc.
# web=True looks for agent packages in subdirectories of agents_dir
# Using session_service_uri=None to use in-memory sessions (avoids greenlet dependency)
app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_PARENT_DIR,  # Points to parent dir containing fastapi_adk_agent/
    session_service_uri=None,  # Use in-memory sessions (no database/greenlet needed)
    web=True,  # Enables the built-in Dev Dashboard UI
)


# --- Pydantic Models for Request/Response ---
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    user_id: str = "default_user"


class QuestionResponse(BaseModel):
    answer: str
    session_id: str


# 2. Add a Custom Endpoint (Optional but Recommended)
@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


# 3. Add Custom Question Endpoint
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Post a question to the agent and get a response.

    Args:
        request: QuestionRequest containing the question and optional session_id

    Returns:
        QuestionResponse with the agent's answer
    """
    try:
        # Generate session_id if not provided
        import uuid

        session_id = request.session_id or str(uuid.uuid4())

        # Create or get session
        try:
            await session_service.create_session(
                app_name="learner_assistant",
                user_id=request.user_id,
                session_id=session_id,
            )
        except Exception:
            # Session might already exist, that's okay
            pass

        # Create runner
        runner = Runner(
            app_name="learner_assistant",
            agent=root_agent,
            session_service=session_service,
        )

        # Create message
        new_message = genai_types.Content(
            role="user", parts=[genai_types.Part(text=request.question)]
        )

        # Run agent asynchronously and collect response
        full_response = ""
        async for event in runner.run_async(
            user_id=request.user_id, session_id=session_id, new_message=new_message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            full_response += part.text

        return QuestionResponse(
            answer=full_response if full_response else "No response from agent",
            session_id=session_id,
        )
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        return QuestionResponse(
            answer=f"Error: {str(e)}\n\nDetails:\n{error_details}",
            session_id=request.session_id or "error",
        )


# 3. Run the Server
if __name__ == "__main__":
    # Ensure uvicorn is installed (pip install uvicorn)
    uvicorn.run(app, host="0.0.0.0", port=8000)
