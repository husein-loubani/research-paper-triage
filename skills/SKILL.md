# Skill: paper-brief-format

## Purpose
Guarantees the Summarizer agent writes every paper the same way, so a whole
run is scannable and consistent. This is the project's "agent skill" artifact.

## When this applies
Whenever the Summarizer produces a brief for a candidate paper.

## Required output format (per paper)
For each of the top papers, output exactly these four parts, in this order:

1. **Title** — the paper's title.
2. **Authors** — comma-separated author names.
3. **Relevance** — ONE line on why this paper matters to the given topic.
4. **Summary** — exactly THREE sentences describing the paper's contribution.

## Rules
- Keep the four parts in the same order for every paper.
- The relevance note is a single line, not a paragraph.
- The summary is three sentences: no more, no less.
- Do not invent details that are not supported by the abstract.
