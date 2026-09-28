"""End-to-end CLI tests.

`ingest` and `ask` use the real `hashing` embedder and a real (temp-dir)
Chroma store — no API key needed for retrieval. Only the LLM provider is
mocked, via `factories.build_provider`, so these tests never hit a real
API.
"""

from typer.testing import CliRunner

from groundedrag import cli
from groundedrag.cli import app

runner = CliRunner()


class FakeProvider:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str, *, temperature: float = 0.1) -> str:
        self.prompts.append(prompt)
        return self.response


def test_init_scaffolds_project(tmp_path):
    project_dir = tmp_path / "myproject"

    result = runner.invoke(app, ["init", str(project_dir)])

    assert result.exit_code == 0
    assert (project_dir / "coverage.yaml").exists()
    assert (project_dir / "documents").is_dir()


def test_init_does_not_overwrite_existing_coverage_map(tmp_path):
    project_dir = tmp_path / "myproject"
    project_dir.mkdir()
    coverage_path = project_dir / "coverage.yaml"
    coverage_path.write_text("billing: [doc-1]\n")

    result = runner.invoke(app, ["init", str(project_dir)])

    assert result.exit_code == 0
    assert coverage_path.read_text() == "billing: [doc-1]\n"


def test_ingest_indexes_documents_and_updates_coverage(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()
    (documents_dir / "remote-work.md").write_text(
        "Employees may work remotely up to three days a week."
    )
    coverage_path = tmp_path / "coverage.yaml"
    persist_dir = tmp_path / "chroma"

    result = runner.invoke(
        app,
        [
            "ingest",
            str(documents_dir),
            "--topic",
            "hr-policy",
            "--coverage",
            str(coverage_path),
            "--persist-dir",
            str(persist_dir),
            "--embedder",
            "hashing",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Indexed 1 chunks from 1 document" in result.output
    assert "remote-work" in coverage_path.read_text()


def test_ask_refuses_undocumented_topic(tmp_path):
    coverage_path = tmp_path / "coverage.yaml"
    coverage_path.write_text("hr-policy: [remote-work]\n")

    result = runner.invoke(
        app,
        [
            "ask",
            "when do I get paid?",
            "--topic",
            "payroll",
            "--coverage",
            str(coverage_path),
            "--persist-dir",
            str(tmp_path / "chroma"),
        ],
    )

    assert result.exit_code == 1
    assert "Refused" in result.output


def test_ask_end_to_end_with_mocked_provider(tmp_path, monkeypatch):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()
    (documents_dir / "remote-work.md").write_text(
        "Employees may work remotely up to three days a week."
    )
    coverage_path = tmp_path / "coverage.yaml"
    persist_dir = tmp_path / "chroma"

    ingest_result = runner.invoke(
        app,
        [
            "ingest",
            str(documents_dir),
            "--topic",
            "hr-policy",
            "--coverage",
            str(coverage_path),
            "--persist-dir",
            str(persist_dir),
        ],
    )
    assert ingest_result.exit_code == 0, ingest_result.output

    fake_provider = FakeProvider("You may work remotely up to three days a week [1].")
    monkeypatch.setattr(cli, "build_provider", lambda name, model: fake_provider)

    ask_result = runner.invoke(
        app,
        [
            "ask",
            "how many remote days are allowed?",
            "--topic",
            "hr-policy",
            "--coverage",
            str(coverage_path),
            "--persist-dir",
            str(persist_dir),
        ],
    )

    assert ask_result.exit_code == 0, ask_result.output
    assert "three days a week [1]" in ask_result.output
    assert "Fully cited" in ask_result.output
    assert "remote-work" in ask_result.output
    assert "[1]" in fake_provider.prompts[0]  # the prompt included numbered context
