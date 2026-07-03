"""Searcher agent, step 1 of the pipeline.

Takes the user's research topic, calls the live arXiv tool, and returns a list
of candidate papers (title, authors, abstract, link). Its text output is saved
to shared session state under output_key="candidates" so the Summarizer can
read it in step 2.

The `{topic}` placeholder is filled from session state at run time (main.py
seeds it). MAX_RESULTS is substituted here in Python, not from state.
"""

from google.adk.agents import LlmAgent

from config import MODEL, MAX_RESULTS
from tools.arxiv_tool import arxiv_search

_INSTRUCTION = (
    "You are a research paper search assistant.\n"
    "The user's research topic is:\n{topic}\n\n"
    "Do exactly this:\n"
    "1. Call the `arxiv_search` tool once. Set `query` to the research topic "
    "and `max_results` to " + str(MAX_RESULTS) + ".\n"
    "2. Return every paper the tool returns, as a numbered list. For each "
    "paper put Title, Authors, Link, and the full Abstract on their own lines.\n\n"
    "Do not rank, filter, or summarize the papers. That is the next agent's "
    "job. Return them faithfully. If the tool returns an 'error' field, report "
    "that error plainly instead of inventing papers."
)

searcher_agent = LlmAgent(
    name="searcher",
    model=MODEL,
    description="Searches arXiv for papers matching the user's topic.",
    instruction=_INSTRUCTION,
    tools=[arxiv_search],
    output_key="candidates",
)
