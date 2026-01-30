import logging
import os

import vertexai
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from vertexai.preview.vision_models import ImageGenerationModel

from .utils.utils import load_prompt_from_file

# Set logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configuration constants
GOOGLE_MODEL_NAME = "gemini-2.5-flash"
DESCRIPTION = (
    "Agent responsible for creating storyboards based on a screenplay and story"
)

# Initialize VertexAI and image generation model
IMAGEN_GOOGLE_MODEL_NAME = "imagen-4.0-ultra-generate-001"

logger.debug(f"ProjectID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
logger.debug(f"Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)
generation_model = ImageGenerationModel.from_pretrained(IMAGEN_GOOGLE_MODEL_NAME)


# Storyboard generate tool
def storyboard_generate(
    prompt: str, scene_number: int, tool_context: ToolContext
) -> list[str]:
    """
    Generate storyboard image representing the passed prompt.

    Args:
        prompt (str): A text prompt describing the storyboard image that should be generated and returned by the tool.
        scene_number (int): Scene number
        tool_context (): ToolContext needed by the tool

    Returns:
        str: Link to the image stored in GCS bucket.
    """
    try:
        # Get session_id for the GCS_PATH
        session_id = tool_context._invocation_context.session.id
        bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
        GCS_PATH = f"gs://{bucket_name}/{session_id}"
        AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"

        # Actual image generation
        logger.info(f"Generating image for scene {scene_number} with prompt: {prompt}")
        response = generation_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            output_gcs_uri=f"{GCS_PATH}/scene_{scene_number}",
            aspect_ratio="1:1",
            negative_prompt="",
            person_generation="allow_adult",
            safety_filter_level="block_few",
            add_watermark=True,
        )

        if response.images:
            logger.info(
                f"Generated {len(response.images)} image(s) for prompt: {prompt}"
            )
            return [
                image._gcs_uri.replace("gs://", AUTHORIZED_URI)
                for image in response.images
            ]
        else:
            logger.info(f"Generated no (0) images for prompt: {prompt}")
            return []  # Return an empty list if no images
    except Exception as e:
        logger.error(f"Error generating an image for {prompt}: {e}")
        return []


# --- Storyboard Agent ---
storyboard_agent = None
try:
    storyboard_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=GOOGLE_MODEL_NAME,
        name="storyboard_agent",
        description=(DESCRIPTION),
        instruction=load_prompt_from_file("storyboard_agent.txt"),
        output_key="storyboard",
        tools=[storyboard_generate],
    )
    logger.info(f"✅ Agent '{storyboard_agent.name}' created using model '{GOOGLE_MODEL_NAME}'.")
except Exception as e:
    logger.error(
        f"❌ Could not create Storyboard agent. Check API Key ({GOOGLE_MODEL_NAME}). Error: {e}"
    )
