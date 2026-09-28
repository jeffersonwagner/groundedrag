# groundedrag

**A hard gate that stops your RAG from answering without evidence.**

Most RAG pipelines always call the LLM, even when retrieval finds nothing
relevant — the model fills the gap with invented information,
confidently. `groundedrag` is a small, opinionated Python library that adds
two things on top of whatever retrieval stack you already have:

1. **Documentary gate** — before the LLM is ever called, checks whether
   there's real coverage for the question's topic, using an auditable
   `topic → documents` map a non-engineer can read and edit. No coverage
   means the LLM is never called.
2. **Verified citations** — every factual claim must cite `[n]`; a
   verifier runs after generation and checks each citation against what
   was actually retrieved.

See the [GitHub repository](https://github.com/jeffersonwagner/groundedrag)
for the full pitch, installation, and source. This site holds the deeper
technical documentation:

- **[Quickstart](quickstart.md)** — try it in two minutes, no API key.
- **[Architecture](architecture.md)** — how the pieces fit together and
  the project's roadmap.
- **[Benchmark](benchmark.md)** — the hallucination-rate benchmark and
  what it does (and doesn't) measure.
- **[Decision records](adr/0001-domain-agnostic-core.md)** — every
  non-obvious design decision, its rejected alternatives, and what would
  invalidate it.
- **[Releasing](RELEASING.md)** — how versions get published to PyPI.
