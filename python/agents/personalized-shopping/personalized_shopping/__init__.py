import os

import google.auth

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

import torch

# Workaround to Resolve the PyTorch-Streamlit Incompatibility Issue
torch.classes.__path__ = []

# Initialize webshop environment (requires Java)
# If Java is not available (e.g., in CI), set webshop_env to None
try:
    from .shared_libraries.init_env import init_env, webshop_env
except Exception:
    webshop_env = None
    init_env = None

from . import agent
