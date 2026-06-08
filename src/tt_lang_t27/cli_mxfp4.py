"""CLI: tt-lang-t27-mxfp4-conform.

Reads an MXFP4 vector pack, re-encodes each block, compares bit-exact
against expected scale + nibbles + packed bytes.  Emits a single verdict
line.  Exit 0 if conform, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from .conformance_mxfp4 import check_mxfp4_vectors, load_mxfp4_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tt-lang-t27-mxfp4-conform",
        description="Run MXFP4 conformance vectors against the t27 codec "
                    "(parity check vs tt-metal kMxFp4Params).",
    )
    parser.add_argument("--vectors", required=True, type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    pack = load_mxfp4_pack(args.vectors)
    report = check_mxfp4_vectors(pack["vectors"])
    sha = hashlib.sha256(args.vectors.read_bytes()).hexdigest()

    if not args.quiet:
        print(report.verdict_line(sha=sha))
        if not report.ok:
            for f in report.failures[:10]:
                print(f"  fail: {f}", file=sys.stderr)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
