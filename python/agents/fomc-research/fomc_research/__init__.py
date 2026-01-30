"""Initialization functions for FOMC Research Agent."""

import logging
import os

loglevel = os.getenv("GOOGLE_GENAI_FOMC_AGENT_LOG_LEVEL", "INFO")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {loglevel}")
logger = logging.getLogger(__package__)
logger.setLevel(numeric_level)

GOOGLE_MODEL_NAME = os.getenv("GOOGLE_GENAI_GOOGLE_MODEL_NAME")
if not GOOGLE_MODEL_NAME:
    GOOGLE_MODEL_NAME = "gemini-2.5-flash"

# GOOGLE_MODEL_NAME needs to be defined before this import
from . import agent  # pylint: disable=wrong-import-position
