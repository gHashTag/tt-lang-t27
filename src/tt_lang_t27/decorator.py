"""@t27_kernel decorator: pins a tt-lang kernel function to a t27 numeric format."""

from __future__ import annotations

import functools
import hashlib
from pathlib import Path
from typing import Callable

from .conformance import check_vectors
from .registry import Registry, load_registry, load_vectors


def _provenance_tag(fn_name: str, registry: Registry, fmt: str) -> str:
    h = hashlib.sha256()
    h.update(fn_name.encode("ascii"))
    h.update(registry.ssot_commit.encode("ascii"))
    h.update(fmt.encode("ascii"))
    h.update(registry.anchor_hash_sha256.encode("ascii"))
    return h.hexdigest()


def t27_kernel(
    fmt: str = "GF16",
    registry_path: str | Path = "format-spec-001.json",
    vectors_path: str | Path | None = None,
    verbose: bool = True,
):
    """Decorator wiring kernel function to t27 numeric SSOT.

    Loads the registry once at decoration time (not on each call).
    Optionally runs conformance vector check at decoration time
    if `vectors_path` is provided.
    """
    registry = load_registry(registry_path)
    if fmt not in registry.formats:
        raise KeyError(f"format {fmt!r} not in registry")
    spec = registry.formats[fmt]

    vector_report = None
    if vectors_path is not None:
        vectors = load_vectors(vectors_path)
        vector_report = check_vectors(vectors)

    def decorator(fn: Callable) -> Callable:
        tag = _provenance_tag(fn.__name__, registry, fmt)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if verbose:
                print(
                    f"[t27] kernel={fn.__name__} fmt={fmt} "
                    f"ssot={registry.ssot_commit} tag={tag[:12]}"
                )
                if vector_report is not None:
                    print(
                        f"[t27]   vector-check n={vector_report.total} "
                        f"passed={vector_report.passed} "
                        f"failed={vector_report.failed}"
                    )
            return fn(*args, **kwargs)

        wrapper.t27_meta = {
            "fmt": fmt,
            "ssot_commit": registry.ssot_commit,
            "tag": tag,
            "spec": spec,
            "vector_report": vector_report,
        }
        return wrapper

    return decorator
