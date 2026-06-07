"""CLI: tt-lang-t27-conform.

Reads a registry + vector pack, runs the bit-precise codec check,
emits a single verdict line.  Exit 0 if conform, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from .conformance import check_vectors
from .registry import load_registry, load_vectors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tt-lang-t27-conform",
        description="Run t27 conformance vectors against the GF16 codec.",
    )
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--vectors", required=True, type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    registry = load_registry(args.registry)
    vectors = load_vectors(args.vectors)
    report = check_vectors(vectors)

    sha = hashlib.sha256(args.vectors.read_bytes()).hexdigest()

    if not args.quiet:
        print(report.verdict_line(sha=sha))
        if not report.ok:
            for f in report.failures[:10]:
                print(f"  fail: {f}", file=sys.stderr)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
