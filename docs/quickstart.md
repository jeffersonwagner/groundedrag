# Quickstart

## See it work — no API key

```bash
uv sync --extra dev --extra chroma
uv run python examples/helpdesk_bot/demo.py
```

This runs entirely offline (the dependency-free `HashingEmbedder`, no
network calls) and shows the two guarantees that matter most: a documented
question retrieves real chunks, and an undocumented one is refused before
any LLM would be called. See
[`examples/compliance_qa`](https://github.com/jeffersonwagner/groundedrag/tree/main/examples/compliance_qa)
for a second, compliance-flavored example.

## CLI

```bash
groundedrag init my-project && cd my-project
# put a few .txt/.md/.pdf files in documents/
groundedrag ingest documents --topic hr-policy
groundedrag ask "how many remote days are allowed?" --topic hr-policy
```

`ask` on an undocumented topic prints the refusal reason and exits
non-zero instead of guessing — try `--topic something-you-never-ingested`
to see it. Defaults use `HashingEmbedder` (see
[`docs/adr/0003`](adr/0003-hashing-embedder-for-zero-setup-demos.md)) and a
local Chroma store; pass `--embedder openai` (with `OPENAI_API_KEY` set)
for real retrieval quality, and `--provider anthropic|openai|ollama` to
pick the LLM.

## As a library

See the [README](https://github.com/jeffersonwagner/groundedrag#as-a-library)
for the minimal `DocumentGate` + `GatedRetriever` + `build_answer` wiring,
or read [Architecture](architecture.md) for how the pieces fit together
and [the ADRs](adr/0001-domain-agnostic-core.md) for why they're built
this way.
