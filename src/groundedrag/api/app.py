"""Optional thin FastAPI wrapper around the core pipeline.

Not required to use groundedrag as a library — this is a convenience for
callers who want an HTTP endpoint. Requires the ``api`` extra. Lands in
Phase 2.
"""

from __future__ import annotations


def create_app():
    raise NotImplementedError("Phase 2")
