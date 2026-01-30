import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv, find_dotenv
from .prompts import return_instructions_root

load_dotenv(find_dotenv())

# Build tools list conditionally based on RAG_CORPUS availability
tools = []
rag_corpus = os.environ.get("RAG_CORPUS")

if rag_corpus:
    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description=(
            "Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,"
        ),
        rag_resources=[
            rag.RagResource(
                # please fill in your own rag corpus
                # here is a sample rag corpus for testing purpose
                # e.g. projects/123/locations/us-central1/ragCorpora/456
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
    tools.append(ask_vertex_retrieval)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="ask_rag_agent",
    instruction=return_instructions_root(),
    tools=tools,
)
