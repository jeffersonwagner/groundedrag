# ADR-0001 — Keep the core domain-agnostic

## Context

The two ideas behind `groundedrag` — a hard documentary gate before calling the
LLM, and citation verification after generation — are easy to build in a way
that quietly couples them to one vertical: the coverage map keyed by a
domain-specific taxonomy, chunk metadata shaped around one kind of document,
prompt templates that assume a particular question format. That coupling is
tempting because it is faster to ship a first working version, but it turns
the project into a template for one use case rather than a reusable library.

## Decision

`gate.py` and `guardrails.py` operate only on three generic types —
`Document`, `Chunk`, and `Answer` — and the coverage map is a plain
`topic → [documents]` mapping with no assumptions about what a "topic" is.
Everything domain-specific (what counts as a topic, how documents are
chunked, what the LLM prompt looks like) lives outside the core, in
provider/store implementations or in the caller's own configuration.

## Alternatives considered

**Ship a vertical-specific starter template** (e.g., a pre-built internal
IT-helpdesk bot) instead of a general library. Rejected: a template gets
copied and forked per use case, which means every bug fix and every
improvement to the gate or the citation verifier has to be re-applied by
hand across every fork. A library with a stable core interface fixes bugs
once for everyone who depends on it.

**Bake a default taxonomy into the coverage map** (e.g., ship with a
predefined set of topic categories) to make onboarding faster. Rejected: any
default taxonomy is wrong for most domains, and "wrong but built-in" is
worse than "absent and obviously the caller's job," because a wrong default
fails silently — a topic that doesn't fit the built-in categories would
either be forced into the wrong bucket or silently fall through the gate.

## Consequences

- Onboarding a new domain means writing a coverage map and, if needed, a
  loader for that domain's document format — there is no default to fall
  back on. This is a deliberate cost: it keeps the gate's behavior
  predictable rather than "mostly right."
- The reference implementations (Chroma + sentence-transformers + Ollama/
  Anthropic) exist to prove the interfaces work end-to-end, not to be the
  only supported path — any `VectorStore`, `Embedder`, or `LLMProvider` that
  satisfies the `Protocol` works.

## What would invalidate this

If, after a few real integrations, every single caller ends up writing
near-identical coverage maps or loaders, that repetition is a signal to
extract a second, optional layer of domain presets **on top of** the
generic core — without removing the domain-agnostic core itself.
