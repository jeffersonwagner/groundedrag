# Architecture

## 1. Scope

`groundedrag` adds two things to a RAG pipeline: a **documentary gate** that
decides whether the LLM should be called at all, and a **citation
verifier** that checks the LLM's answer after the fact. It does not
implement retrieval, chunking, or an LLM itself — those are provided by
whatever stack the caller already has, through small pluggable interfaces.

## 2. Decision flow

```
User question
      │
      ▼
Retrieval over indexed documents (top-k chunks)
      │
      ▼
GATE: is there documentary coverage for this question's topic?
   (topic → documents map, an auditable, hand-editable config)
      │
 ┌────┴────┐
 NO         YES
 │           │
 ▼           ▼
Refuse      Call the LLM with the retrieved chunks as context
+ explain   (prompt requires a [n] citation per claim)
what's           │
missing          ▼
           GUARDRAIL: extract the citations from the answer and check
           that each one points to a chunk that was actually retrieved
                 │
                 ▼
           Final answer, with verified, cited sources
```

## 3. Components

| Layer | Module | Responsibility | Status |
|---|---|---|---|
| Gate | `gate.py` | decide: call the LLM or refuse, based on coverage | done |
| Coverage | `coverage.py` | topic → documents map (YAML/JSON), the gate's source of truth | done |
| Retrieval | `retriever.py` | wraps an `Embedder` + `VectorStore`, applies the gate first | done |
| Reliability | `guardrails.py` | citation extraction + post-generation verification (`build_answer`) | done |
| Generation | `providers/*` | one `LLMProvider` per backend | Anthropic, OpenAI, Ollama implemented |
| Storage | `stores/*` | one `VectorStore` per backend | `InMemoryStore`, `ChromaStore` implemented; pgvector/Qdrant are stubs |
| Embeddings | `embeddings/*` | one embedding backend | OpenAI, sentence-transformers implemented |
| Ingestion | `loaders/*` | text extraction, with automatic OCR fallback for scanned PDFs | done (text, PDF+OCR) |
| Chunking | `chunking.py` | splits text into overlapping, whitespace-safe chunks | done |

`LLMProvider`, `VectorStore`, and `Embedder` are `Protocol`-based (see
`docs/adr/0002`): `groundedrag`'s core never imports a specific vendor SDK
directly — every provider/store/embedder implementation imports its SDK
lazily and raises a clear `ImportError` naming the extra to install when
it's missing, so swapping Chroma for pgvector or Ollama for Anthropic never
touches `gate.py`, `retriever.py`, or `guardrails.py`.

## 4. Design principles

- **The gate is a hard stop, not a soft hint.** If coverage is missing, the
  LLM is never called — there is no context for it to hallucinate against.
- **Citation is verified in code, not just requested in the prompt.** A
  prompt asking the model to cite `[n]` is an instruction the model can
  ignore or fake; the verifier checks it after the fact.
- **The coverage map is auditable by a non-engineer.** It is a plain
  YAML/JSON file — `topic → [documents]` — that a domain expert can read
  and correct without touching code.
- **Document tagging is conservative by default.** As of Phase 1, the
  coverage map is a hand-written `topic → [documents]` file — there is no
  automatic inference yet. A planned Phase 2+ addition is an *optional*
  cascade (explicit manifest entry → filename/folder → keyword match in
  text) to help populate the map, always erring toward leaving a topic
  undocumented over guessing wrong.
- **Nothing about the core is domain-specific.** `gate.py` and
  `guardrails.py` operate on generic `Document`, `Chunk`, and `Answer`
  types — the same core works for HR policies, technical manuals, or API
  documentation.

## 5. Roadmap

See the repository's [issues](https://github.com/jeffersonwagner/groundedrag/issues)
and [the ADRs](adr/0001-domain-agnostic-core.md) for in-progress design
decisions. At a high level:

| Phase | Deliverables | Status |
|---|---|---|
| 0 — Setup | repository, license, CI, project skeleton, first ADR | done |
| 1 — Core | gate, coverage map, guardrails, pluggable interfaces, reference implementations (in-memory + Chroma stores, OpenAI + sentence-transformers embeddings, Anthropic/OpenAI/Ollama providers, text/PDF+OCR loaders) | done |
| 2 — DX & examples | CLI (`init`/`ingest`/`ask`/`doctor`), a zero-setup `HashingEmbedder` default, two runnable examples, quickstart docs | done |
| 3 — Packaging | PyPI release, docs site, hallucination-rate benchmark | next |
| 4 — Launch | public announcement | planned |
| 5 — Post-launch | issue triage, community-requested integrations | planned |
