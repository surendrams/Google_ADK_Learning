"""Performs quality assurance checks on generated media using a generative model."""

import logging
from typing import Literal, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

from content_gen_agent.utils.evaluation_prompts import get_image_evaluation_prompt

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
EVALUATION_GOOGLE_MODEL_NAME = "gemini-2.5-flash"


class EvalResult(BaseModel):
    """Represents the structured result of a media evaluation."""

    decision: Literal["Pass", "Fail"]
    reason: str
    subject_adherence: Literal["Pass", "Fail"]
    attribute_matching: Literal["Pass", "Fail"]
    spatial_accuracy: Literal["Pass", "Fail"]
    style_fidelity: Literal["Pass", "Fail"]
    quality_and_coherence: Literal["Pass", "Fail"]
    no_storyboard: Literal["Pass", "Fail"]


def _get_internal_prompt(mime_type: str, evaluation_criteria: str) -> str:
    """Constructs the internal prompt for the evaluation model.

    Args:
        mime_type: The MIME type of the media being evaluated.
        evaluation_criteria: The specific criteria for evaluation.

    Returns:
        The formatted prompt string.
    """
    if mime_type == "image/png":
        return get_image_evaluation_prompt(evaluation_criteria)
    return f"""
    You are a strict Quality Assurance specialist.
    Evaluate the following media based on this single criterion: '{evaluation_criteria}'.

    Your response must be in JSON.
    - If the media passes, respond with: {{"decision": "Pass"}}
    - If it fails, respond with: {{"decision": "Fail", "reason": "A concise explanation."}}
    """


async def evaluate_media(
    media_bytes: bytes, mime_type: str, evaluation_criteria: str
) -> Optional[EvalResult]:
    """Performs a quality assurance check on media bytes.

    Args:
        media_bytes: The media content as bytes.
        mime_type: The MIME type of the media.
        evaluation_criteria: The rule or question to evaluate the media against.

    Returns:
        An instance of EvalResult, or None on failure.
    """
    try:
        client = genai.Client()
        internal_prompt = _get_internal_prompt(mime_type, evaluation_criteria)

        response = await client.aio.models.generate_content(
            model=EVALUATION_GOOGLE_MODEL_NAME,
            contents=[
                internal_prompt,
                types.Part.from_bytes(data=media_bytes, mime_type=mime_type),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EvalResult,
            ),
        )

        result = response.parsed
        logging.info(f"Overall Evaluation Decision: {result.decision}")
        if result.decision == "Fail":
            logging.warning(f"Evaluation failed reason: {result.reason}")
        return result
    except Exception as e:
        logging.error(f"Media evaluation failed: {e}", exc_info=True)
        return None


def calculate_evaluation_score(
    evaluation_result: Optional[EvalResult],
) -> int:
    """Calculates a score based on the evaluation result.

    Args:
        evaluation_result: The result of the media evaluation.

    Returns:
        An integer score from 0 to 22.
    """
    if not evaluation_result:
        return 0

    score = 0
    score_mapping = {
        "decision": 10,
        "subject_adherence": 2,
        "attribute_matching": 2,
        "spatial_accuracy": 2,
        "style_fidelity": 2,
        "quality_and_coherence": 2,
        "no_storyboard": 2,
    }

    for field, value in score_mapping.items():
        if getattr(evaluation_result, field) == "Pass":
            score += value

    return score
