"""Entry point. Runs the whole thing from the command line.

Flow:
  1. load .env  (reads GEMINI_API_KEY)
  2. read the research topic (from argv or a prompt)
  3. security guard: validate_topic  ->  ensure key  ->  confirm_search
  4. run the SequentialAgent pipeline (Searcher -> Summarizer)
  5. print the briefs

Usage:
    python main.py "large language model agents"
    python main.py            # will prompt for the topic
    python main.py -y "..."   # skip the confirmation prompt
"""

import warnings

# Keep the demo output clean: hide library deprecation and experimental notices.
warnings.filterwarnings("ignore")

import argparse
import asyncio
import os
import sys
import time

from dotenv import load_dotenv

from config import MAX_RESULTS
from security.guard import validate_topic, confirm_search, TopicRejected


def _ensure_api_key() -> bool:
    """Confirm a usable Gemini key is present and expose it the way ADK expects."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key or key.strip() in ("", "your-gemini-api-key-here"):
        print("\nERROR: no Gemini API key found.")
        print("Copy .env.example to .env and set GEMINI_API_KEY, then retry.")
        return False
    # google-genai (used by ADK) reads GOOGLE_API_KEY. Set only that one and drop
    # GEMINI_API_KEY from the environment, so the SDK doesn't announce that both
    # are set on every model call.
    os.environ["GOOGLE_API_KEY"] = key
    os.environ.pop("GEMINI_API_KEY", None)
    return True


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Research paper triage: search arXiv, rank, and brief the top papers."
    )
    parser.add_argument("topic", nargs="*", help="Your research topic in plain English.")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt.")
    args = parser.parse_args()

    raw_topic = " ".join(args.topic).strip() or input("Research topic: ").strip()

    # 1) security: validate the input string
    try:
        topic = validate_topic(raw_topic)
    except TopicRejected as e:
        print(f"Rejected: {e}")
        return 2

    # 2) make sure we can actually run before asking to confirm
    if not _ensure_api_key():
        return 3

    # 3) security: confirm before a large live search
    if not args.yes and not confirm_search(topic, MAX_RESULTS):
        print("Cancelled.")
        return 1

    # 4) run the pipeline (imported here so a bad topic / missing key exits fast
    #    without spinning up ADK)
    from pipeline import run_triage
    from google.genai.errors import APIError

    print("\nRunning Searcher -> Summarizer ...\n")

    # Gemini sometimes returns a transient 503 (model busy) or 429 (rate limit).
    # Retry a few times with backoff so a temporary spike does not kill the run,
    # and if it still fails, print one clean line instead of a long traceback.
    retryable = {429, 500, 502, 503, 504}
    max_attempts = 4
    for attempt in range(1, max_attempts + 1):
        try:
            briefs = asyncio.run(run_triage(topic))
            print(briefs or "(no output produced)")
            return 0
        except KeyboardInterrupt:
            print("\nInterrupted.")
            return 130
        except APIError as e:
            code = getattr(e, "code", None)
            if code in retryable and attempt < max_attempts:
                wait = attempt * 4
                print(
                    f"Gemini is busy (HTTP {code}). Retrying in {wait}s ... "
                    f"[attempt {attempt} of {max_attempts}]"
                )
                time.sleep(wait)
                continue
            print(f"\nGemini request failed (HTTP {code}). Please try again in a minute.")
            return 4


if __name__ == "__main__":
    sys.exit(main())
