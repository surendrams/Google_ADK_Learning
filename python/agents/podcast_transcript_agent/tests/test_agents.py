import pytest
from google.adk.runners import InMemoryRunner
from podcast_transcript_agent.agent import podcast_transcript_agent
from pathlib import Path
from google.genai import types
import dotenv
import json


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv(find_dotenv())


@pytest.mark.asyncio
async def test_run_with_txt():
    """Tests that the agent can generate a transcript from a text file."""
    runner = InMemoryRunner(agent=podcast_transcript_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    file_path = Path("./tests/test_artifacts/test_pyramid.txt")
    file_content = file_path.read_bytes()

    content = types.Content(
        parts=[
            types.Part(
                text=(
                    "Generate podcast from this document. Podcast host name is"
                    " Charlotte, expert's name is Dr Joe Sponge"
                )
            ),
            types.Part(
                inline_data=types.Blob(mime_type="text/plain", data=file_content)
            ),
        ]
    )

    found_valid_transcript = False

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if (
            event.is_final_response()
            and event.author == "podcast_transcript_writer_agent"
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        data = json.loads(part.text)
                        if (
                            "metadata" in data
                            and "duration_seconds" in data["metadata"]
                        ):
                            if data["metadata"]["duration_seconds"] > 0:
                                found_valid_transcript = True

    assert found_valid_transcript, "No final event found with valid transcript metadata"
