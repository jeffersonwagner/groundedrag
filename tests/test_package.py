"""Phase 0 sanity checks: the package imports and its skeleton holds together."""

import re
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from groundedrag import __version__
from groundedrag.cli import app

runner = CliRunner()


def test_version_is_set():
    # Not pinned to a literal so bumping the release version doesn't
    # require touching this test — just that it looks like a version.
    assert re.match(r"^\d+\.\d+\.\d+", __version__)


def test_version_matches_pyproject():
    # docs/RELEASING.md asks a release to bump both by hand — this catches
    # the two drifting apart rather than only finding out at publish time.
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    assert data["project"]["version"] == __version__


def test_cli_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
