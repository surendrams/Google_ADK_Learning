from __future__ import annotations

import os
from dotenv import load_dotenv, find_dotenv
import json
import sqlite3
import asyncio
from typing import Any, Dict, List

import requests

from google.adk.agents import LlmAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ================
# 1) External API Tool
# ================


class WeatherApiTool(BaseTool):
    """
    Example tool that calls a public HTTP API.
    Uses the free "wttr.in" endpoint for demonstration.
    """

    def __init__(self) -> None:
        super().__init__(
            name="weather_api_tool",
            description=(
                "Get current weather information for any city. "
                "Use this tool when the user asks about weather conditions, temperature, or forecasts. "
                "Required parameter: city (string) - the name of the city to get weather for."
            ),
        )

    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: ToolContext,
    ) -> Dict[str, Any]:
        city = args.get("city")
        if not city:
            return {"error": "Missing required parameter: 'city'"}

        url = f"https://wttr.in/{city}?format=j1"

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            return {"error": f"HTTP error: {e}"}

        try:
            data = resp.json()
        except Exception as e:
            return {"error": f"Failed to parse JSON: {e}"}

        current = data.get("current_condition", [{}])[0]
        temp_c = current.get("temp_C")
        desc = current.get("weatherDesc", [{}])[0].get("value")

        return {
            "city": city,
            "temperature_c": temp_c,
            "description": desc,
            "raw": data,
        }


# ================
# 2) File Read/Write Tool
# ================


class FileStoreTool(BaseTool):
    """
    Tool that can read/write simple text files in a sandboxed 'data' directory.
    """

    BASE_DIR = "data"

    def __init__(self) -> None:
        super().__init__(
            name="file_store_tool",
            description=(
                "Read from or write to text files in the local data directory. "
                "Use this tool when the user wants to create, save, read, or manage files. "
                "Parameters: operation ('read' or 'write'), filename (string), content (string, required for write operations)."
            ),
        )
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def _path(self, filename: str) -> str:
        safe_name = filename.replace("..", "_")
        return os.path.join(self.BASE_DIR, safe_name)

    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: ToolContext,
    ) -> Dict[str, Any]:
        operation = args.get("operation")
        filename = args.get("filename")

        if not operation or not filename:
            return {"error": "Required: 'operation' and 'filename'"}

        path = self._path(filename)

        if operation == "write":
            content = args.get("content")
            if content is None:
                return {"error": "For 'write', 'content' is required."}
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {
                    "status": "ok",
                    "message": f"Wrote {len(content)} chars to {filename}.",
                }
            except Exception as e:
                return {"error": f"Write failed: {e}"}

        elif operation == "read":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"status": "ok", "filename": filename, "content": content}
            except FileNotFoundError:
                return {"error": f"File not found: {filename}"}
            except Exception as e:
                return {"error": f"Read failed: {e}"}

        else:
            return {"error": f"Unknown operation: {operation}"}


# ================
# 3) Database Tool (SQLite)
# ================


class SqliteTool(BaseTool):
    """
    Very simple SQLite tool. Supports:
      - init_db: creates a demo table 'notes'
      - add_note: inserts a note
      - list_notes: returns all notes
    """

    DB_PATH = "demo.db"

    def __init__(self) -> None:
        super().__init__(
            name="sqlite_tool",
            description=(
                "Interact with a SQLite database for storing and retrieving notes. "
                "Use this tool when the user wants to work with a database, store data, or manage notes. "
                "Operations: 'init_db' (create database), 'add_note' (add a note), 'list_notes' (show all notes). "
                "Parameters: operation (string), content (string, required for add_note)."
            ),
        )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.DB_PATH)

    def _init_db(self) -> str:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()
        return "Database initialized."

    def _add_note(self, content: str) -> str:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            conn.commit()
            note_id = cur.lastrowid
        finally:
            conn.close()
        return f"Inserted note with id={note_id}"

    def _list_notes(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, content FROM notes ORDER BY id ASC")
            rows = cur.fetchall()
        finally:
            conn.close()
        return [{"id": r[0], "content": r[1]} for r in rows]

    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: ToolContext,
    ) -> Dict[str, Any]:
        op = args.get("operation")
        if not op:
            return {"error": "Missing 'operation'."}

        if op == "init_db":
            msg = self._init_db()
            return {"status": "ok", "message": msg}

        if op == "add_note":
            content = args.get("content")
            if not content:
                return {"error": "Missing 'content' for add_note."}
            msg = self._add_note(content)
            return {"status": "ok", "message": msg}

        if op == "list_notes":
            notes = self._list_notes()
            return {"status": "ok", "notes": notes}

        return {"error": f"Unknown operation: {op}"}


# ================
# 4) Streaming Output Tool
# ================


class StreamingCounterTool(BaseTool):
    """
    Example tool that "streams" progress updates logically.
    In this simple demo we just return all updates at the end.
    """

    def __init__(self) -> None:
        super().__init__(
            name="streaming_counter_tool",
            description=(
                "Count from 1 to a specified number and show progress updates. "
                "Use this tool when the user wants a counting demonstration or streaming progress example. "
                "Parameter: n (integer) - the number to count up to (default: 5)."
            ),
        )

    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: ToolContext,
    ) -> Dict[str, Any]:
        import asyncio as _asyncio

        n = int(args.get("n", 5))
        updates: List[str] = []

        for i in range(1, n + 1):
            msg = f"Count: {i}/{n}"
            updates.append(msg)
            # In a real app you might use ToolContext + events
            # to stream these updates back incrementally.
            await _asyncio.sleep(0.3)

        return {
            "final": f"Finished counting to {n}.",
            "updates": updates,
        }



def file_storage(operation: str, filename: str, content: str = None) -> Dict[str, Any]:
    """
    Read from or write to text files in the local data directory.

    Args:
        operation: Either 'read' or 'write'
        filename: Name of the file to read or write
        content: Content to write (required for write operations)

    Returns:
        Result of the file operation.
    """
    import os

    BASE_DIR = "data"
    os.makedirs(BASE_DIR, exist_ok=True)

    # Simple path sanitization
    safe_name = filename.replace("..", "_")
    path = os.path.join(BASE_DIR, safe_name)

    if operation == "write":
        if content is None:
            return {"error": "For 'write', 'content' is required."}
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "status": "ok",
                "message": f"Wrote {len(content)} chars to {filename}.",
            }
        except Exception as e:
            return {"error": f"Write failed: {e}"}

    elif operation == "read":
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "ok", "filename": filename, "content": content}
        except FileNotFoundError:
            return {"error": f"File not found: {filename}"}
        except Exception as e:
            return {"error": f"Read failed: {e}"}
    else:
        return {"error": f"Unknown operation: {operation}"}


def sqlite_database(operation: str, content: str = None) -> Dict[str, Any]:
    """
    Interact with a SQLite database for storing and retrieving notes.

    Args:
        operation: 'init_db' (create database), 'add_note' (add a note), or 'list_notes' (show all notes)
        content: Content for the note (required for add_note operation)

    Returns:
        Result of the database operation.
    """
    import sqlite3

    DB_PATH = "demo.db"

    def _connect():
        return sqlite3.connect(DB_PATH)

    if operation == "init_db":
        conn = _connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()
        return {"status": "ok", "message": "Database initialized."}

    elif operation == "add_note":
        if not content:
            return {"error": "Missing 'content' for add_note."}
        conn = _connect()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            conn.commit()
            note_id = cur.lastrowid
        finally:
            conn.close()
        return {"status": "ok", "message": f"Inserted note with id={note_id}"}

    elif operation == "list_notes":
        conn = _connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, content FROM notes ORDER BY id ASC")
            rows = cur.fetchall()
        finally:
            conn.close()
        notes = [{"id": r[0], "content": r[1]} for r in rows]
        return {"status": "ok", "notes": notes}

    else:
        return {"error": f"Unknown operation: {operation}"}


def streaming_counter(n: int = 5) -> Dict[str, Any]:
    """
    Count from 1 to a specified number and show progress updates.

    Args:
        n: The number to count up to (default: 5)

    Returns:
        Counting results with progress updates.
    """
    import asyncio
    import time

    updates = []
    for i in range(1, n + 1):
        msg = f"Count: {i}/{n}"
        updates.append(msg)
        # Simulate some work
        time.sleep(0.1)

    return {
        "final": f"Finished counting to {n}.",
        "updates": updates,
    }


def summarize_json(data: dict) -> Dict[str, Any]:
    """
    Summarize a JSON object by listing its keys and serialized size.

    Args:
        data: A JSON-like dict to summarize.
    """
    keys = list(data.keys())
    size = len(json.dumps(data))
    summary = f"JSON with keys: {keys}, size={size} chars"
    return {"summary": summary}

def build_function_tool() -> FunctionTool:
    # You could also just pass `summarize_json` directly as a tool.
    # Here we wrap it explicitly to mirror your original structure.
    return FunctionTool(summarize_json)

# ================
# Build Agent
# ================


def build_agent() -> LlmAgent:
    tools = [
        WeatherApiTool(),
        FileStoreTool(),
        SqliteTool(),
        StreamingCounterTool(),
        build_function_tool(),
    ]

    agent = LlmAgent(
        name="advanced_tools_agent",
        model=os.getenv(key='GOOGLE_MODEL_NAME', default="gemini-2.5-flash-lite"),  # or your configured model name
        instruction=(
            "You are a helpful assistant with access to several specialized tools:\n"
            "1. WeatherApiTool - Get weather information for any city\n"
            "2. FileStoreTool - Read and write text files in a local data directory\n"
            "3. SqliteTool - Store and retrieve notes using a SQLite database\n"
            "4. StreamingCounterTool - Count numbers and show progress\n"
            "5. summarize_json - Summarize JSON objects\n\n"
            "Always use the appropriate tool when the user's request matches the tool's functionality. "
            "The tools are available and working properly."
        ),
        tools=tools,
    )
    return agent


# ================
# Runner helpers (ADK v1.19.0 pattern)
# ================


APP_NAME = "adk_advanced_tools"
USER_ID = "surendra"
SESSION_ID = "adk_advanced_tools_demo_session"


async def setup_runner(agent: LlmAgent) -> Runner:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return runner


async def run_once(runner: Runner, prompt: str) -> str:
    """Send a single text prompt and return the final model response text."""
    content = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text = "No final response from agent."
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(
                p.text for p in event.content.parts if p.text
            )
            break

    return final_text


# ================
# Demo main
# ================


async def async_main() -> None:

    load_dotenv(dotenv_path=find_dotenv())
    
    agent = build_agent()
    runner = await setup_runner(agent)

    print("=== Example 1: Ask for weather (external API tool) ===")
    resp_text = await run_once(
        runner,
        "What is the current weather in San Francisco? Use the weather tool.",
    )
    print(resp_text)

    print("\n=== Example 2: Write and read a file (file_store_tool) ===")
    resp_text = await run_once(
        runner,
        "Create a file named 'note.txt' with some text about our meeting, "
        "then read it back.",
    )
    print(resp_text)

    print("\n=== Example 3: Use SQLite tool ===")
    resp_text = await run_once(
        runner,
        "Initialize the database, add a note 'Buy milk', and then list all notes.",
    )
    print(resp_text)

    print("\n=== Example 4: Streaming counter ===")
    resp_text = await run_once(
        runner,
        "Use the streaming counter tool to count to 5.",
    )
    print(resp_text)

    print("\n=== Example 5: JSON summarizer FunctionTool ===")
    resp_text = await run_once(
        runner,
        "Here is some JSON: "
        "{'name': 'Alice', 'age': 30, 'hobbies': ['reading', 'hiking']}. "
        "Use the JSON summarizer tool on it.",
    )
    print(resp_text)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
