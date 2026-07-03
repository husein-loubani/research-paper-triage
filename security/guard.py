"""Security guard. Runs BEFORE any live search.

Two checks keep the run controlled, which is the course's "guardrails" concept:

  1. validate_topic(topic): rejects empty, over-long, non-printable, or
     obvious prompt-injection input before it reaches the model or arXiv.
  2. confirm_search(topic, max_results): shows exactly what is about to run
     and asks for a y/n confirmation, so a large live search never runs blind.
"""

from config import MAX_RESULTS

MAX_TOPIC_LEN = 200
MIN_TOPIC_LEN = 3

# Cheap tripwires for prompt injection or abuse. Not exhaustive, a sane gate,
# not a full firewall.
_SUSPICIOUS = (
    "ignore previous",
    "ignore all previous",
    "disregard previous",
    "system prompt",
    "you are now",
    "reveal your",
    "api key",
    "os.system",
    "<script",
)


class TopicRejected(ValueError):
    """Raised when a topic fails validation."""


def validate_topic(topic: str) -> str:
    """Return a cleaned topic, or raise TopicRejected explaining why not."""
    if not topic or not topic.strip():
        raise TopicRejected("Topic is empty.")

    cleaned = " ".join(topic.split())  # collapse newlines / runs of whitespace

    if len(cleaned) < MIN_TOPIC_LEN:
        raise TopicRejected(f"Topic is too short (min {MIN_TOPIC_LEN} characters).")
    if len(cleaned) > MAX_TOPIC_LEN:
        raise TopicRejected(f"Topic is too long (max {MAX_TOPIC_LEN} characters).")
    if not cleaned.isprintable():
        raise TopicRejected("Topic contains non-printable characters.")

    low = cleaned.lower()
    for marker in _SUSPICIOUS:
        if marker in low:
            raise TopicRejected(
                f"Topic looks like a prompt-injection attempt (matched {marker!r})."
            )

    return cleaned


def confirm_search(topic: str, max_results: int = MAX_RESULTS) -> bool:
    """Show what is about to run and ask for confirmation. Returns True to go."""
    print("\nAbout to run a live search:")
    print(f"  topic      : {topic}")
    print(f"  max papers : up to {max_results} from arXiv")
    print("  will call  : arXiv API + Gemini API (uses your quota)")
    answer = input("Proceed? [y/N]: ").strip().lower()
    return answer in ("y", "yes")
