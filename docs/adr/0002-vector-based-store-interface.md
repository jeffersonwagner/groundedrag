# ADR-0002 — VectorStore deals in vectors, not raw text

## Context

The first draft of `VectorStore.query()` took a raw query string and a
`topic`, implying the store itself would embed text and know about topics.
That conflates three concerns that need to vary independently: which
embedding model is used, which vector backend stores the result, and how
"coverage" is defined for a given caller's domain.

## Decision

`VectorStore` only ever sees vectors (`add(chunks, vectors)`,
`query(vector, document_ids=...)`). Embedding is the `Embedder`'s job, and
`GatedRetriever` is the only component that talks to both: it asks the
`DocumentGate` for the topic's allowed `document_ids`, embeds the query
with the `Embedder`, and only then queries the `VectorStore`, passing
`document_ids` through as a metadata filter.

This also means the coverage map's topic vocabulary never leaks into the
storage layer: a `VectorStore` implementation filters by `document_id`,
a concept every backend already has, not by `topic`, a concept only the
gate understands.

## Consequences

- Swapping the embedding backend (e.g. sentence-transformers → OpenAI)
  never touches a `VectorStore` implementation, and swapping the vector
  backend never touches an `Embedder` implementation — each Phase 1
  reference implementation (`InMemoryStore`, `ChromaStore`,
  `OpenAIEmbedder`, `SentenceTransformersEmbedder`) was written and tested
  independently of the others.
- Every provider and heavy-dependency backend (Anthropic, OpenAI, Ollama,
  Chroma, sentence-transformers) imports its vendor SDK lazily, inside the
  method that needs it, and raises a clear `ImportError` naming the extra
  to install rather than failing at package import time. This is what lets
  `import groundedrag` stay light regardless of which extras are installed.
- Default CI installs `anthropic`, `openai`, `ollama`, `chroma`, and `pdf`,
  but not `sentence-transformers`, `pgvector`, or `qdrant`: the first group
  is fast to install and is exercised by tests (mocked SDK clients for the
  providers and embedder, a real ephemeral collection for Chroma); the
  second group either pulls a multi-gigabyte PyTorch/CUDA download
  (sentence-transformers) or has no backend available in CI at all
  (pgvector needs a live Postgres, qdrant a live Qdrant instance). Those
  three remain typed, importable stubs/adapters, exercised by hand or by a
  future opt-in integration workflow rather than every push.

## What would invalidate this

If a vector backend needs to embed internally to use its own model (e.g. a
managed service that only accepts raw text), that backend's adapter can
still embed internally and ignore the `Embedder` — the `Protocol` doesn't
forbid it, it just isn't required by `GatedRetriever`'s default wiring.
