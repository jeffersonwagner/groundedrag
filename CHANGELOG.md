# Changelog

All notable changes to this project are documented in this file. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-28

First tagged release: the core library, CLI, and packaging are usable
end to end.

### Changed

- Renamed the project from `rag-gate` to `groundedrag`: PyPI rejected the
  original name as too similar to an existing, thematically adjacent
  package (`raggate`, a CI evaluation gate for RAG systems). See
  [ADR-0007](docs/adr/0007-renamed-to-groundedrag.md).

### Added

- `DocumentGate` + `CoverageMap`: a hard, auditable gate that refuses to
  let a question reach the LLM without documented coverage.
- `GatedRetriever`: wires an `Embedder` and a `VectorStore` behind the
  gate — a refused topic never touches the vector index.
- `guardrails.build_answer()`: post-generation citation extraction and
  verification.
- Reference implementations: `InMemoryStore` and `ChromaStore` (vectors),
  `OpenAIEmbedder` and `SentenceTransformersEmbedder` (embeddings),
  `AnthropicProvider`, `OpenAIProvider`, and `OllamaProvider` (generation),
  plus text and PDF (with automatic OCR fallback) loaders.
- `HashingEmbedder`: a dependency-free, deterministic embedder so the CLI
  and examples work with no API key, GPU, or network access.
- CLI: `groundedrag init|ingest|ask|doctor`.
- Two runnable examples (`examples/helpdesk_bot`, `examples/compliance_qa`).
- A hallucination-rate benchmark (`scripts/benchmark.py`) measuring the
  answer-rate gap on out-of-scope questions, with docs in
  [`docs/benchmark.md`](docs/benchmark.md).
- Documentation site (mkdocs) and this changelog.
- `stores/pgvector.py` and `stores/qdrant.py` ship as typed stubs — not
  implemented yet, contributions welcome (see `CONTRIBUTING.md`).
