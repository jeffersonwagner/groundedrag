# groundedrag

**A hard gate that stops your RAG from answering without evidence.**

[Leia em português](README.pt-BR.md)

> Status: early development (Phase 3 — packaging). Not yet published on PyPI —
> see [`docs/RELEASING.md`](docs/RELEASING.md) for what's left.

[Docs site](https://jeffersonwagner.github.io/groundedrag/) ·
[Benchmark](docs/benchmark.md) ·
[Changelog](CHANGELOG.md)

## The problem

Most RAG (retrieval-augmented generation) pipelines always call the LLM, even
when retrieval finds nothing relevant. The model fills the gap with invented
information — confidently. In domains where a wrong answer has a real cost
(compliance, internal support, technical documentation, safety procedures),
that is not a UX bug, it is a liability.

## What groundedrag does

`groundedrag` is a small, opinionated Python library that adds two things on top
of whatever retrieval stack you already have:

1. **Documentary gate.** Before the LLM is ever called, `groundedrag` checks
   whether there is real coverage for the topic of the question, using an
   auditable `topic → documents` map that a non-engineer can read and edit.
   No coverage → the LLM is never called, and the caller gets an explicit
   "not documented, here's what to add" response instead of a guess.
2. **Verified citations.** Every factual claim the LLM makes must cite
   `[n]`. A verifier runs **after** generation and checks that every citation
   points to a chunk that was actually retrieved, flagging or stripping any
   claim that isn't traceable. A prompt asking the model to cite its sources
   is an instruction, not a guarantee — the verification in code is what
   makes it one.

`groundedrag` does not replace your retrieval stack, your vector database, or
your LLM provider. It sits in front of the LLM call and after the generation
step, as a thin, provider-agnostic layer.

## Why not just use LangChain / LlamaIndex / Guardrails AI?

Those are large, general-purpose frameworks. `groundedrag` is deliberately
narrow: it does two things — the gate and the citation check — and is meant
to drop into a stack you already have, including one built on LangChain or
LlamaIndex, without asking you to adopt a whole new framework.

## Status

**Phase 3 (packaging) in progress.** The library, CLI, docs site, and
release automation are all in place; the one thing left is the two
one-time manual steps on PyPI's and GitHub's side described in
[`docs/RELEASING.md`](docs/RELEASING.md) and below — until then, install
from source (`pip install -e .` or `uv sync`), not from PyPI. See
[`docs/architecture.md`](docs/architecture.md) for the full design and
[`docs/adr/`](docs/adr) for the reasoning behind each decision.

### Try it in two minutes — no API key needed

```bash
uv sync --extra dev --extra chroma
uv run python examples/helpdesk_bot/demo.py
```

This shows groundedrag's two core guarantees with sample documents bundled
in the repo: a documented question retrieves real chunks, and an
undocumented one is refused *before* any LLM would be called. See
[`examples/`](examples) for both runnable examples.

### CLI

```bash
groundedrag init my-project && cd my-project
# put a few .txt/.md/.pdf files in documents/, then:
groundedrag ingest documents --topic hr-policy
groundedrag ask "how many remote days are allowed?" --topic hr-policy
```

By default `ingest`/`ask` use the dependency-free `HashingEmbedder` (no API
key, but lower retrieval quality — see `docs/adr/0003`) and a local Chroma
store persisted under `.groundedrag/chroma`. Pass `--embedder openai` (with
`OPENAI_API_KEY` set) for real retrieval quality, and `--provider
anthropic|openai|ollama` to pick the LLM that generates the final answer.

### As a library

```python
from groundedrag.coverage import CoverageMap
from groundedrag.gate import DocumentGate
from groundedrag.retriever import GatedRetriever
from groundedrag.guardrails import build_answer
from groundedrag.prompting import build_prompt
from groundedrag.stores.memory import InMemoryStore
from groundedrag.embeddings.openai import OpenAIEmbedder
from groundedrag.providers.anthropic import AnthropicProvider

gate = DocumentGate(CoverageMap.from_file("coverage.yaml"))
retriever = GatedRetriever(gate, InMemoryStore(), OpenAIEmbedder())

question = "when do I get paid?"
decision, chunks = retriever.retrieve("payroll", question)
if not decision.allowed:
    print(decision.missing_documents_hint)
else:
    raw_answer = AnthropicProvider().generate(build_prompt(question, chunks))
    answer = build_answer(raw_answer, [c.id for c in chunks])
```

### Benchmark

```bash
uv run python scripts/benchmark.py
```

On out-of-scope questions (no matching documentation), a pipeline with no
gate answers 100% of the time — it has no way to know it shouldn't.
`groundedrag` refuses 100% of the time, and `tests/test_benchmark.py` holds
that number as a regression check, not just a demo. See
[`docs/benchmark.md`](docs/benchmark.md) for methodology and
[ADR-0005](docs/adr/0005-hallucination-benchmark-methodology.md) for why
it's scoped this way.

## Project layout

```
src/groundedrag/
├── gate.py            # decides: call the LLM, or refuse with a reason
├── coverage.py         # topic → documents map, auditable (YAML/JSON)
├── retriever.py        # retrieval + gate integration
├── guardrails.py        # citation extraction and verification
├── prompting.py          # builds the citation-required LLM prompt
├── chunking.py           # pure-Python, whitespace-safe text chunking
├── ingestion.py          # walks a directory into (Document, Chunk) pairs
├── factories.py          # name -> instance wiring for the CLI's flags
├── schemas.py          # Pydantic contracts
├── cli.py               # groundedrag init / ingest / ask / doctor
├── providers/           # LLM providers: anthropic, openai, ollama
├── stores/              # vector stores: chroma, pgvector, memory
├── embeddings/           # embedding backends, incl. the zero-setup HashingEmbedder
├── loaders/              # document loaders (PDF, OCR fallback, text)
└── api/                  # optional thin FastAPI wrapper
```

Elsewhere in the repo: `examples/` (the two runnable demos),
`scripts/benchmark.py` (the hallucination-rate benchmark), `docs/` (the
mkdocs site source — architecture, ADRs, benchmark methodology,
quickstart), and `CHANGELOG.md`.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Skips sentence-transformers on purpose — it pulls in a multi-GB PyTorch
# download. Add --extra sentence-transformers if you need that backend.
uv sync --extra dev --extra anthropic --extra openai --extra ollama --extra chroma --extra pdf
uv run pytest
uv run ruff check .
uv run mypy src/groundedrag
```

To build the docs site locally: `uv sync --extra docs && uv run mkdocs serve`.

## License

[Apache 2.0](LICENSE).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).
