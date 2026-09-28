"""groundedrag command-line interface.

Defaults favor a zero-setup first run: the ``hashing`` embedder and the
``chroma`` store (persisted under ``.groundedrag/chroma`` by default) need no
API key, no GPU, and no external service. Pass ``--embedder openai`` or
``--embedder sentence-transformers`` once you care about real retrieval
quality — see docs/quickstart.md.
"""

from __future__ import annotations

from pathlib import Path

import typer

from groundedrag import __version__
from groundedrag.coverage import CoverageError, CoverageMap
from groundedrag.factories import (
    EMBEDDER_CHOICES,
    PROVIDER_CHOICES,
    STORE_CHOICES,
    build_embedder,
    build_provider,
    build_store,
)
from groundedrag.gate import DocumentGate
from groundedrag.guardrails import build_answer
from groundedrag.ingestion import load_directory
from groundedrag.prompting import build_prompt
from groundedrag.retriever import GatedRetriever

app = typer.Typer(help="A hard documentary gate and citation verifier for RAG pipelines.")

DEFAULT_COVERAGE = "coverage.yaml"
DEFAULT_PERSIST_DIR = ".groundedrag/chroma"


@app.command()
def version() -> None:
    """Print the installed groundedrag version."""
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check that groundedrag is installed correctly."""
    typer.echo(f"groundedrag {__version__} — core package importable.")


@app.command()
def init(directory: str = typer.Argument(".", help="Where to scaffold the project.")) -> None:
    """Scaffold a new groundedrag project: an empty coverage map and a
    documents folder to ingest from."""
    root = Path(directory)
    documents_dir = root / "documents"
    coverage_path = root / DEFAULT_COVERAGE

    documents_dir.mkdir(parents=True, exist_ok=True)
    if coverage_path.exists():
        typer.echo(f"{coverage_path} already exists, leaving it as is.")
    else:
        CoverageMap().save(coverage_path)
        typer.echo(f"Created {coverage_path}")
    typer.echo(f"Created {documents_dir}/ — put your .txt, .md, or .pdf files here.")
    typer.echo(
        "\nNext: groundedrag ingest documents --topic <topic-name>\n"
        "Then: groundedrag ask \"your question\" --topic <topic-name>"
    )


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Directory of .txt/.md/.pdf files to ingest."),
    topic: str = typer.Option(
        ..., "--topic", help="Topic to map every ingested document to in the coverage map."
    ),
    coverage: str = typer.Option(DEFAULT_COVERAGE, "--coverage", help="Coverage map file."),
    store: str = typer.Option(
        "chroma", "--store", help=f"Vector store: {', '.join(STORE_CHOICES)}."
    ),
    persist_dir: str = typer.Option(
        DEFAULT_PERSIST_DIR, "--persist-dir", help="Where the chroma store persists to disk."
    ),
    embedder: str = typer.Option(
        "hashing", "--embedder", help=f"Embedding backend: {', '.join(EMBEDDER_CHOICES)}."
    ),
) -> None:
    """Ingest documents from PATH, index them, and map them to TOPIC in
    the coverage map."""
    documents, chunks = load_directory(path)
    if not documents:
        typer.echo(f"No .txt, .md, or .pdf files found directly under {path}.")
        raise typer.Exit(code=1)
    if not chunks:
        typer.echo("Documents were found but produced no text chunks — nothing to index.")
        raise typer.Exit(code=1)

    embedder_instance = build_embedder(embedder)
    vectors = embedder_instance.embed([chunk.text for chunk in chunks])

    store_instance = build_store(store, persist_dir if store == "chroma" else None)
    store_instance.add(chunks, vectors)

    coverage_path = Path(coverage)
    coverage_map = (
        CoverageMap.from_file(coverage_path) if coverage_path.exists() else CoverageMap()
    )
    coverage_map.add(topic, [document.id for document in documents])
    coverage_map.save(coverage_path)

    typer.echo(
        f"Indexed {len(chunks)} chunks from {len(documents)} document(s) "
        f"under topic '{topic}'."
    )


@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to ask."),
    topic: str = typer.Option(..., "--topic", help="Topic the question belongs to."),
    coverage: str = typer.Option(DEFAULT_COVERAGE, "--coverage", help="Coverage map file."),
    store: str = typer.Option(
        "chroma", "--store", help=f"Vector store: {', '.join(STORE_CHOICES)}."
    ),
    persist_dir: str = typer.Option(
        DEFAULT_PERSIST_DIR, "--persist-dir", help="Where the chroma store persists to disk."
    ),
    embedder: str = typer.Option(
        "hashing", "--embedder", help=f"Embedding backend: {', '.join(EMBEDDER_CHOICES)}."
    ),
    provider: str = typer.Option(
        "anthropic", "--provider", help=f"LLM provider: {', '.join(PROVIDER_CHOICES)}."
    ),
    model: str = typer.Option(None, "--model", help="Override the provider's default model."),
    top_k: int = typer.Option(5, "--top-k", help="How many chunks to retrieve."),
) -> None:
    """Ask a question through the gated pipeline: refuse if undocumented,
    otherwise generate a cited answer and verify every citation."""
    try:
        coverage_map = CoverageMap.from_file(coverage)
    except CoverageError as exc:
        typer.echo(f"Coverage map error: {exc}")
        raise typer.Exit(code=1) from exc

    gate = DocumentGate(coverage_map)
    store_instance = build_store(store, persist_dir if store == "chroma" else None)
    embedder_instance = build_embedder(embedder)
    retriever = GatedRetriever(gate, store_instance, embedder_instance)

    decision, chunks = retriever.retrieve(topic, question, top_k=top_k)
    if not decision.allowed:
        typer.echo(f"Refused: {decision.missing_documents_hint}")
        raise typer.Exit(code=1)
    if not chunks:
        typer.echo(f"'{topic}' is documented, but nothing indexed matched this question yet.")
        raise typer.Exit(code=1)

    try:
        provider_instance = build_provider(provider, model)
        prompt = build_prompt(question, chunks)
        raw_answer = provider_instance.generate(prompt)
    except ImportError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # the vendor SDK's own errors vary by provider
        typer.echo(f"'{provider}' provider failed: {exc}")
        raise typer.Exit(code=1) from exc
    answer = build_answer(raw_answer, [chunk.id for chunk in chunks])

    typer.echo(answer.text)
    typer.echo("")
    typer.echo(
        "✓ Fully cited" if answer.fully_cited else "⚠ Not fully cited — verify before trusting"
    )
    for citation in answer.citations:
        if citation.valid:
            source_chunk = next(c for c in chunks if c.id == citation.chunk_id)
            typer.echo(f"  [{citation.index}] {source_chunk.document_id}")


if __name__ == "__main__":
    app()
