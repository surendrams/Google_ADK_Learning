import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    def __init__(self):
        # Google Cloud Configuration
        self.project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv(
            "GCP_PROJECT_ID"
        )
        self.location: Optional[str] = os.getenv(
            "GOOGLE_CLOUD_LOCATION", "us-central1"
        ).lower()
        self.use_vertex_ai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1"

        # Model Configuration
        self.root_agent_model: str = os.getenv("ROOT_AGENT_GOOGLE_MODEL_NAME", "gemini-2.5-pro")

        # Dataform Configuration
        self.repository_name: str = os.getenv(
            "DATAFORM_REPOSITORY_NAME", "default-repository"
        )
        self.workspace_name: str = os.getenv(
            "DATAFORM_WORKSPACE_NAME", "default-workspace"
        )

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        return True

    @property
    def project_location(self) -> str:
        """Get the project location in the format required by BigQuery and Dataform."""
        return f"{self.project_id}.{self.location}"

    @property
    def vertex_project_location(self) -> str:
        """Get the project location in the format required by Vertex AI."""
        return f"{self.project_id}.{self.location}"


# Create a global config instance
config = Config()
