import logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.models.llm_request import LlmRequest


def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    last = (llm_request.contents or [])[-1] if llm_request.contents else None
    if not last or last.role != "user":
        return

    for part in getattr(last, "parts", None) or []:
        if getattr(part, "text", None):
            logging.info("[query to %s]: %s", callback_context.agent_name, part.text)


def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(
                    "[response from %s]: %s", callback_context.agent_name, part.text
                )
            elif part.function_call:
                logging.info(
                    "[function call from %s]: %s",
                    callback_context.agent_name,
                    part.function_call.name,
                )
