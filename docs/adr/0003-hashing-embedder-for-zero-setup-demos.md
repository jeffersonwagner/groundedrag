# ADR-0003 — A dependency-free embedder for the CLI's and examples' defaults

## Context

Both real embedding backends (Phase 1) have a real cost: `OpenAIEmbedder`
needs an API key and a network call per chunk; `SentenceTransformersEmbedder`
needs a multi-gigabyte PyTorch download the first time it runs. Either one
as the CLI's or the examples' *default* means the first thing a new user
does — `groundedrag init && groundedrag ingest && groundedrag ask`, or running an
example script — requires a signup or a long wait before they see anything
work.

## Decision

Add `HashingEmbedder` (`embeddings/hashing.py`): a deterministic, pure-
Python hashed bag-of-words vectorizer (the standard "hashing trick," the
same idea behind scikit-learn's `HashingVectorizer`) with zero
dependencies beyond the standard library. It is the CLI's default
`--embedder` and what both example scripts use.

Its docstring and the CLI help text both say plainly that it is for demos
and tests, not production retrieval quality — `--embedder openai` or
`--embedder sentence-transformers` is one flag away once real usage
starts.

## Consequences

- `groundedrag init && groundedrag ingest documents --topic x && groundedrag ask
  "..." --topic x` and both example scripts (`examples/*/demo.py`) run to
  completion with no API key, no GPU, and no network access — the two
  guarantees that matter most for a first impression (the gate refusing an
  undocumented topic, and citation verification) are visible immediately.
- Retrieval quality from `HashingEmbedder` is meaningfully worse than a
  real embedding model — it captures shared vocabulary, not semantics.
  This is an acceptable, disclosed trade-off for a *default*, not for the
  library's recommended production configuration.
- The examples still show the real LLM-generation-and-citation-verification
  path when `ANTHROPIC_API_KEY` is set, so nothing about the citation
  guardrail itself is demonstrated with a shortcut — only the vector
  embedding step is.

## What would invalidate this

If `HashingEmbedder`'s retrieval quality is confusing enough that people
mistake it for a real bug when they use the CLI's defaults on their own
documents, the fix is a louder runtime warning on first use, not removing
the zero-setup path — the value of "it works instantly" outweighs the cost
of a documented quality caveat.
