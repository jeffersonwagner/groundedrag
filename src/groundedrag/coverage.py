"""The documentary coverage map: the gate's single source of truth.

A coverage map is a plain ``topic -> [document ids]`` mapping. It is meant
to be small enough to be hand-edited by a domain expert who is not a
programmer — see docs/architecture.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml


class CoverageError(ValueError):
    """Raised when a coverage map file is malformed."""


class CoverageMap:
    """Loads and queries a topic -> documents coverage map."""

    def __init__(self, mapping: dict[str, list[str]] | None = None) -> None:
        self._mapping = mapping or {}

    def has_coverage(self, topic: str) -> bool:
        """Return True if at least one document is mapped to ``topic``."""
        return bool(self._mapping.get(topic))

    def documents_for(self, topic: str) -> list[str]:
        """Return the document ids mapped to ``topic``, if any."""
        return list(self._mapping.get(topic, []))

    def topics(self) -> list[str]:
        """Return every topic with at least one document mapped to it."""
        return [topic for topic, documents in self._mapping.items() if documents]

    def add(self, topic: str, document_ids: list[str]) -> None:
        """Map ``document_ids`` to ``topic``, in place, without duplicates."""
        existing = self._mapping.setdefault(topic, [])
        for document_id in document_ids:
            if document_id not in existing:
                existing.append(document_id)

    def to_dict(self) -> dict[str, list[str]]:
        """Return a plain copy of the underlying mapping."""
        return {topic: list(documents) for topic, documents in self._mapping.items()}

    def save(self, path: str | Path) -> None:
        """Write this coverage map to ``path`` as YAML.

        This rewrites the whole file — comments and key order in a
        hand-edited file are not preserved. Fine for the CLI's own writes;
        keep hand-curated coverage maps under version control so a rewrite
        is always a reviewable diff.
        """
        Path(path).write_text(
            yaml.safe_dump(self.to_dict(), sort_keys=True), encoding="utf-8"
        )

    @classmethod
    def from_file(cls, path: str | Path) -> CoverageMap:
        """Load a coverage map from a YAML or JSON file.

        The file must contain a mapping of ``topic -> [document ids]``.
        Malformed content raises :class:`CoverageError` rather than failing
        silently or half-loading — a broken coverage map must never be
        mistaken for an empty (and therefore fully-refusing) one.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise CoverageError(f"Coverage map file not found: {file_path}")

        raw = file_path.read_text(encoding="utf-8")
        try:
            if file_path.suffix.lower() == ".json":
                data = json.loads(raw)
            else:
                data = yaml.safe_load(raw)
        except (json.JSONDecodeError, yaml.YAMLError) as exc:
            raise CoverageError(f"Could not parse coverage map {file_path}: {exc}") from exc

        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise CoverageError(
                f"Coverage map {file_path} must be a mapping of topic -> [documents], "
                f"got {type(data).__name__}"
            )

        mapping: dict[str, list[str]] = {}
        for topic, documents in data.items():
            if not isinstance(topic, str):
                raise CoverageError(f"Coverage map {file_path}: topic keys must be strings")
            if documents is None:
                mapping[topic] = []
                continue
            if not isinstance(documents, list) or not all(isinstance(d, str) for d in documents):
                raise CoverageError(
                    f"Coverage map {file_path}: topic '{topic}' must map to a list of "
                    "document id strings"
                )
            mapping[topic] = documents

        return cls(mapping)
