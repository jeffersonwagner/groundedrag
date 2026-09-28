# Releasing

Publishing to PyPI is automated (`.github/workflows/release.yml`, triggered
by pushing a `v*` tag), using PyPI's **trusted publishing** (OIDC) — no API
token is stored in this repository. That automation needs two one-time,
manual steps on PyPI's side before the first release; nothing else here can
do them on your behalf.

## One-time setup (before the first release)

1. Log in at [pypi.org](https://pypi.org) and go to
   **Your projects → Publishing** (or, if the `groundedrag` project doesn't
   exist yet, use PyPI's
   [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
   flow, which lets you register a trusted publisher for a project name
   before it has a first release).
2. Add a trusted publisher with:
   - **PyPI project name:** `groundedrag`
   - **Owner:** `jeffersonwagner`
   - **Repository name:** `groundedrag`
   - **Workflow filename:** `release.yml`
   - **Environment name:** `pypi`

That environment name must match the `environment: name: pypi` in
`release.yml` exactly, or PyPI will reject the publish with an OIDC error.

## Cutting a release

1. Update `version` in `pyproject.toml` and `__version__` in
   `src/groundedrag/__init__.py` (keep them in sync — nothing currently
   enforces that automatically).
2. Move the `[Unreleased]` section of `CHANGELOG.md` under a new
   `## [X.Y.Z] - YYYY-MM-DD` heading.
3. Commit, then tag and push:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. The `Release` workflow builds the sdist/wheel and publishes to PyPI.
   Watch it in the Actions tab — a failure here almost always means the
   trusted publisher configuration doesn't match (wrong environment name,
   wrong workflow filename) rather than a problem with the build itself.

## Versioning

[Semantic versioning](https://semver.org/). Anything before `1.0.0` may
still change its public API between minor versions — the project has been
at `0.x` through Phases 0-3 for exactly that reason.
