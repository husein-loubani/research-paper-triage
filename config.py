"""Shared configuration for the research-triage pipeline.

Defined in ONE place so the Searcher and Summarizer agents can never drift
onto different Gemini models. Import these values everywhere instead of
retyping them, which is what avoids a "model not found" surprise on first run.
"""

# Current Flash model on the Gemini API (AI Studio).
# Both agents use this exact string.
MODEL = "gemini-2.5-flash"

# How many candidate papers the Searcher may pull in a single run.
# The security guard uses this to size the confirmation prompt.
MAX_RESULTS = 25

# How many briefs the Summarizer writes from the ranked candidates.
TOP_N = 5
