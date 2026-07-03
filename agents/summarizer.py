"""Summarizer agent, step 2 of the pipeline.

Reads the `candidates` list from session state, ranks the papers by relevance
to the topic, and writes a brief for the top ones. The output format is locked
by skills/SKILL.md, whose contents are injected into this agent's instruction
so every paper comes out with the same structure:

    title, authors, one-line relevance note, three-sentence summary.

`{topic}` and `{candidates}` are filled from session state at run time.
`candidates` is set by the Searcher's output_key before this agent runs.
"""

import os

from google.adk.agents import LlmAgent

from config import MODEL, TOP_N

# Load the skill file next to the project root, regardless of the working dir.
_SKILL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "skills", "SKILL.md"
)
with open(_SKILL_PATH, encoding="utf-8") as _f:
    _SKILL = _f.read()

_INSTRUCTION = (
    "You rank and brief research papers for a specific topic.\n"
    "The user's research topic is:\n{topic}\n\n"
    "Here are the candidate papers found by the search step:\n{candidates}\n\n"
    "Rank the candidates by how relevant each is to the topic. Then write a "
    "brief for the top " + str(TOP_N) + " papers only (fewer if there are not "
    "that many). Apply the output-format skill below EXACTLY to every paper, "
    "and number the papers 1..N in ranked order.\n\n"
    "SKILL (paper brief output format):\n" + _SKILL
)

summarizer_agent = LlmAgent(
    name="summarizer",
    model=MODEL,
    description="Ranks candidate papers and writes a formatted brief for the top ones.",
    instruction=_INSTRUCTION,
    output_key="briefs",
)
