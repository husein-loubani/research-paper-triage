"""arXiv search tool -- the live external data source.

Wraps the `arxiv` PyPI package in a plain Python function. ADK exposes this
function to the Searcher agent as a callable tool (a FunctionTool), so results
come from arXiv at runtime rather than from hardcoded data. This satisfies the
course's "external tool" concept. An MCP server would also work; see the README.

The function is written so it can be run and tested on its own, with no agent
and no Gemini key involved.
"""

from __future__ import annotations

import time

import arxiv

# Hard cap so the tool can never fetch more than this many papers, even if the
# model asks for more. A second, independent guard on top of the security check.
_HARD_CAP = 50

# One shared client. Small pages + built-in retries keep us polite to arXiv and
# resilient to the occasional HTTP 429 / 503 from their public API.
_client = arxiv.Client(page_size=25, delay_seconds=3.0, num_retries=5)

# Outer backoff (seconds) if the whole request is being rate-limited.
_BACKOFF = (5, 12, 25)


def arxiv_search(query: str, max_results: int = 25) -> dict:
    """Search arXiv for recent papers matching a query.

    Args:
        query: The research topic or search phrase.
        max_results: How many papers to return. Capped at 50.

    Returns:
        A dict with two keys:
          - "count": number of papers found.
          - "papers": a list of papers, each a dict with "title", "authors"
            (comma-separated names), "abstract", and "link" (the arXiv page URL).
        On failure it returns count 0, an empty list, and an "error" string, so
        the caller degrades gracefully instead of crashing.
    """
    query = (query or "").strip()
    if not query:
        return {"count": 0, "papers": [], "error": "empty query"}

    n = max(1, min(int(max_results), _HARD_CAP))
    search = arxiv.Search(
        query=query,
        max_results=n,
        sort_by=arxiv.SortCriterion.SubmittedDate,  # most recent first
    )

    last_err = None
    for attempt, wait in enumerate((0, *_BACKOFF)):
        if wait:
            time.sleep(wait)
        try:
            papers = [
                {
                    "title": r.title.strip(),
                    "authors": ", ".join(a.name for a in r.authors),
                    "abstract": r.summary.strip().replace("\n", " "),
                    "link": r.entry_id,
                }
                for r in _client.results(search)
            ]
            return {"count": len(papers), "papers": papers}
        except Exception as e:  # arxiv.HTTPError, network hiccups, etc.
            last_err = e

    return {
        "count": 0,
        "papers": [],
        "error": f"arxiv request failed after retries: {last_err}",
    }


if __name__ == "__main__":
    # Standalone smoke test: prove the tool pulls live results from arXiv.
    import json

    out = arxiv_search("retrieval augmented generation", max_results=3)
    print(f"count = {out['count']}")
    for i, p in enumerate(out["papers"], 1):
        print(f"\n[{i}] {p['title']}")
        print(f"    authors: {p['authors'][:80]}")
        print(f"    link:    {p['link']}")
        print(f"    abstract: {p['abstract'][:120]}...")
    print("\nraw dict shape:", json.dumps({k: (v if k == 'count' else '...') for k, v in out.items()}))
