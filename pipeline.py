"""Pipeline -- wires the two agents into one orchestrated flow, and runs it.

A SequentialAgent runs the Searcher first and the Summarizer second, passing
candidates through shared session state. This is the course's "multi-agent
system" concept: two separate agents in one orchestrated flow.

`root_agent` is also what ADK's CLI (`adk run` / `adk web`) would pick up.
"""

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.searcher import searcher_agent
from agents.summarizer import summarizer_agent

APP_NAME = "research_triage"

root_agent = SequentialAgent(
    name="research_triage",
    description="Searches arXiv, then ranks and briefs the most relevant papers.",
    sub_agents=[searcher_agent, summarizer_agent],
)


async def run_triage(
    topic: str,
    user_id: str = "local_user",
    session_id: str = "session_1",
) -> str:
    """Run Searcher -> Summarizer for a topic and return the final briefs text.

    The topic is seeded into session state so both agents can read `{topic}`.
    The Searcher writes `candidates` to state; the Summarizer reads it and
    produces the briefs, which are the pipeline's final response.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state={"topic": topic},
    )

    message = types.Content(role="user", parts=[types.Part(text=topic)])

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        # Both sub-agents emit a final response; the Summarizer runs last, so
        # the last non-empty final response is the ranked briefs.
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                final_text = text

    return final_text
