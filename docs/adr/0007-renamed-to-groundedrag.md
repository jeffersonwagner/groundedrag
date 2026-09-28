# ADR-0007 — Renamed from `rag-gate` to `groundedrag`

## Context

While registering a PyPI trusted publisher for `rag-gate` (see
`docs/RELEASING.md`), PyPI's project-name-similarity check rejected it:
"O nome do projeto é muito semelhante a um projeto existente." An exact
lookup for `rag-gate` had already returned 404 (confirmed before Phase 0),
so the collision wasn't the literal name — it was `raggate` (no
separator), an existing, unrelated-but-thematically-adjacent package:
a CI-gated evaluation harness for RAG systems using a golden set and an
LLM-judge or heuristic scorer. Different approach (offline evaluation
scoring vs. a runtime refusal gate), same problem space, close enough in
name that PyPI's typosquat-prevention heuristic — and, more importantly,
a human skimming search results — would reasonably confuse the two.

## Decision

Rename the whole project to `groundedrag`: the GitHub repository, the
Python import package (`src/groundedrag/`), the CLI command, the PyPI
distribution name, and every doc, ADR, and example referencing the old
name. `groundedrag` was checked the same way (`https://pypi.org/pypi/
<name>/json` returns 404 for the exact name and every separator variant:
`groundedrag`, `grounded-rag`, `grounded_rag`) and reads naturally against
this project's own vocabulary — the README and architecture docs already
describe the pattern as "grounded RAG" / "ancorado em evidência."

## Alternatives considered

**Keep `rag-gate` everywhere, publish to PyPI under a different
distribution name** (e.g. `rag-gate-guardian`), since the PyPI
distribution name doesn't have to match the import package name. Rejected:
it would leave the project's own brand — repo name, CLI command, the name
people would actually call it — nearly identical to an existing, adjacent
competitor. The confusion PyPI's check exists to prevent doesn't go away
just because the PyPI listing itself has a different name; a brand
collision this close is worth fixing at the source, not routing around on
one platform.

## Consequences

- Every internal reference (`rag_gate` the import name, `rag-gate` the
  repo/CLI/PyPI name) was mechanically replaced with `groundedrag` before
  any tagged release or PyPI publish had happened — there was no external
  install path relying on the old name to preserve compatibility for.
- The GitHub repository itself still needs a manual rename (`Settings →
  General → Repository name`) — nothing in this session's tooling can do
  that on the user's behalf. GitHub redirects the old URL automatically
  once renamed.
- Verified under Python 3.11, 3.12, and 3.13 (ruff, mypy, the full test
  suite, the CLI, both examples, the benchmark, and a strict `mkdocs
  build`) after the rename, not just a single local run — see ADR-0006 for
  why a single-version check isn't enough to trust here.

## What would invalidate this

None expected before a first PyPI release — this is exactly the point in
a project's life where a rename is cheapest. Renaming again after a real
release would need a proper deprecation path (a final release of the old
name pointing to the new one), which this ADR does not need to plan for.
