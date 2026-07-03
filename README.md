# Research Paper Triage — Kaggle 5-Day AI Agents Capstone

Give it a research topic in plain English. It searches recent arXiv papers,
ranks them by relevance to your topic, and writes a short brief for the top
five. Built with the Google Agent Development Kit (ADK) and the Gemini API.

## How it maps to the course concepts
One line per concept — reuse this as the Kaggle writeup rationale.

| Concept | Where it lives |
|---|---|
| Multi-agent system | `pipeline.py` — a `SequentialAgent` runs Searcher → Summarizer, passing candidates through shared session state |
| External tool | `tools/arxiv_tool.py` — a live arXiv search the Searcher calls at runtime (an ADK FunctionTool) |
| Agent skill | `skills/SKILL.md` — injected into the Summarizer so every paper has the same four-part format |
| Security guard | `security/guard.py` — input validation + a confirmation step before any large live search |

## Project layout
```
config.py            MODEL / MAX_RESULTS / TOP_N, defined once so agents can't drift
agents/searcher.py   Searcher agent (calls the arXiv tool, writes "candidates" to state)
agents/summarizer.py Summarizer agent (ranks, briefs the top five, format from SKILL.md)
tools/arxiv_tool.py  live arXiv search, with retry/backoff and a graceful error path
security/guard.py    validate_topic() + confirm_search()
skills/SKILL.md      the locked output format
pipeline.py          SequentialAgent + async run_triage()
main.py              CLI entry point
```

## Setup
Uses Python 3.13 (google-adk supports 3.9–3.13). A virtualenv is already at `.venv`.

```bash
source .venv/bin/activate            # on macOS/Linux
pip install -r requirements.txt      # already installed if you followed along
cp .env.example .env                 # then edit .env and paste your key
```

Get a free Gemini API key at https://aistudio.google.com/apikey and put it in
`.env`:

```
GEMINI_API_KEY=your-real-key-here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

`.env` is gitignored, so the key never gets committed.

## Run
```bash
python main.py "large language model agents"
```

What happens:
1. `validate_topic` checks the string (length, printable, no obvious injection).
2. A key check confirms your Gemini key is set.
3. `confirm_search` shows what will run and waits for `y`. Add `-y` to skip it.
4. The Searcher queries arXiv live, the Summarizer ranks and briefs the top five.

Other forms:
```bash
python main.py                 # prompts you for the topic
python main.py -y "diffusion models for protein design"
```

## Output format (per paper)
Locked by `skills/SKILL.md`:
1. **Title**
2. **Authors**
3. **Relevance** — one line on why it matters to your topic
4. **Summary** — exactly three sentences

## Notes
- Model is set once in `config.py` (`gemini-2.5-flash`) and shared by both
  agents, so a "model not found" mismatch can't happen.
- The arXiv search is an ADK **FunctionTool**. An MCP server is an alternative
  way to expose the same capability; this project uses a FunctionTool for
  simplicity, which still satisfies the "external tool" concept.
- The arXiv public API rate-limits aggressively (HTTP 429). The tool retries
  with backoff and, if it still fails, returns an error the agent reports
  instead of crashing.
- You can also explore the pipeline with ADK's built-in UI: `adk web` picks up
  `root_agent` from `pipeline.py`.
```
