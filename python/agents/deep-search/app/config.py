import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file in the app directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Authentication Configuration:
# By default, uses AI Studio with GOOGLE_API_KEY from .env file.
# To use Vertex AI instead, set GOOGLE_GENAI_USE_VERTEXAI=TRUE in your .env
# and ensure you have Google Cloud credentials configured.

if os.getenv("GOOGLE_API_KEY"):
    # AI Studio mode (default): Use API key authentication
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    # Vertex AI mode: Fall back to Google Cloud credentials
    import google.auth

    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
    """

    critic_model: str = "gemini-3-pro-preview"
    worker_model: str = "gemini-3-pro-preview"
    max_search_iterations: int = 5


config = ResearchConfiguration()
