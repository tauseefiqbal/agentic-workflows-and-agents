"""
Multi-agent workflow using Google ADK.

Pipeline (SequentialAgent): Researcher -> TechnicalWriter
- Researcher uses a stub `search_tool` to gather facts.
- TechnicalWriter uses `formatting_tool` to produce the final report.

Run:
    python agent.py "Explain the benefits of solid-state batteries."
"""

import asyncio
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

load_dotenv()

APP_NAME = "research_writer_swarm"
USER_ID = "local-user"
RESEARCHER_MODEL = "gemini-2.5-flash"
WRITER_MODEL = "gemini-2.5-flash"


def search_tool(query: str) -> str:
    """Find technical details about a topic."""
    return (
        f"Technical details about {query}: solid-state batteries use solid "
        "electrolytes, can improve safety, may increase energy density, and "
        "may support faster charging."
    )


def formatting_tool(text: str) -> str:
    """Format text as a professional report."""
    return f"Professional Report:\n\n{text}"


researcher = LlmAgent(
    name="Researcher",
    model=RESEARCHER_MODEL,
    description="Finds technical details about the user's query.",
    instruction=(
        "You are a research specialist. Call the `search_tool` with the "
        "user's query, then return concise bullet points of the key facts."
    ),
    tools=[search_tool],
    output_key="research_data",
)

writer = LlmAgent(
    name="TechnicalWriter",
    model=WRITER_MODEL,
    description="Synthesizes research into a professional report.",
    instruction=(
        "You are a technical writer. The prior research is available in "
        "session state under key 'research_data'. Pass a polished synthesis "
        "of it to the `formatting_tool`, then return the formatted result. "
        "Keep it under 300 words."
    ),
    tools=[formatting_tool],
    output_key="final_report",
)

# Sequential pipeline: Researcher first, then Writer.
root_agent = SequentialAgent(
    name="ResearchWriterPipeline",
    sub_agents=[researcher, writer],
    description="Runs research then writes a synthesized report.",
)


async def main(query: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    content = types.Content(role="user", parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            text = "".join(p.text or "" for p in event.content.parts)
            if text.strip():
                print(f"\n--- {event.author} ---\n{text}")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Explain the benefits of solid-state batteries."
    asyncio.run(main(query))