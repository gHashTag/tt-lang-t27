"""tt-lang-t27-catalog -- CLI for the 83-format SSOT catalog.

Examples:

    tt-lang-t27-catalog --count
    tt-lang-t27-catalog --list
    tt-lang-t27-catalog --cluster GoldenFloat
    tt-lang-t27-catalog --status Verified
    tt-lang-t27-catalog --show bfloat16
    tt-lang-t27-catalog --json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .catalog import (
    ANCHOR,
    ARXIV,
    SSOT_URL,
    CATALOG,
    Format,
    by_cluster,
    by_status,
    clusters,
    count,
    find,
    statuses,
    as_dict,
)


def _fmt_row(f: Format) -> str:
    pd = f.phi_distance if f.phi_distance_defined else "  N/A"
    return (
        f"  {f.id:24s}  {f.cluster:18s}  bits={f.bits:>4s}  "
        f"s={f.s:>1s}  e={f.e:>3s}  m={f.m:>4s}  "
        f"phi={pd:>6s}  status={f.status}"
    )


def _print_list(rows: List[Format]) -> None:
    print(f"# {len(rows)} formats")
    for r in rows:
        print(_fmt_row(r))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="tt-lang-t27-catalog",
        description=(
            "Inspect the 83-format SSOT numeric catalog "
            "(t27 specs/numeric/formats_catalog.t27). "
            "Anchor: phi^2 + 1/phi^2 = 3 = L_2 (arXiv:2606.05017)."
        ),
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--count",
        action="store_true",
        help="print the total number of formats and exit.",
    )
    g.add_argument(
        "--list",
        action="store_true",
        help="print every format in catalog order.",
    )
    g.add_argument(
        "--cluster",
        metavar="NAME",
        help=(
            "print every format in the given cluster "
            "(e.g. GoldenFloat, Ieee754Binary, Microscaling)."
        ),
    )
    g.add_argument(
        "--status",
        metavar="LABEL",
        help=(
            "print every format with this status label "
            "(Verified, EmpiricalFit, Open, Risk, Retracted, "
            "Experimental, Historical)."
        ),
    )
    g.add_argument(
        "--show",
        metavar="ID",
        help="print the full record for one format by id.",
    )
    g.add_argument(
        "--clusters",
        action="store_true",
        help="list distinct cluster names (in catalog order).",
    )
    g.add_argument(
        "--statuses",
        action="store_true",
        help="list distinct status labels (in catalog order).",
    )
    g.add_argument(
        "--json",
        action="store_true",
        help="dump the full catalog as JSON to stdout.",
    )
    p.add_argument(
        "--anchor",
        action="store_true",
        help="also print the anchor identity, arXiv ref, and SSOT URL.",
    )
    args = p.parse_args(argv)

    if args.anchor:
        print(f"# anchor: {ANCHOR}")
        print(f"# arxiv : {ARXIV}")
        print(f"# ssot  : {SSOT_URL}")
        print()

    if args.count:
        print(count())
        return 0

    if args.list:
        _print_list(list(CATALOG))
        return 0

    if args.cluster:
        rows = by_cluster(args.cluster)
        if not rows:
            print(
                f"error: no formats in cluster {args.cluster!r}",
                file=sys.stderr,
            )
            print(f"known clusters: {clusters()}", file=sys.stderr)
            return 2
        _print_list(rows)
        return 0

    if args.status:
        rows = by_status(args.status)
        if not rows:
            print(
                f"error: no formats with status {args.status!r}",
                file=sys.stderr,
            )
            print(f"known statuses: {statuses()}", file=sys.stderr)
            return 2
        _print_list(rows)
        return 0

    if args.show:
        f = find(args.show)
        if f is None:
            print(f"error: no format with id {args.show!r}", file=sys.stderr)
            return 2
        for k, v in f.as_dict().items():
            print(f"  {k:14s}: {v}")
        return 0

    if args.clusters:
        for c in clusters():
            print(c)
        return 0

    if args.statuses:
        for s in statuses():
            print(s)
        return 0

    if args.json:
        json.dump(as_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    # default: summary
    print(f"# tt_lang_t27 catalog -- {count()} formats")
    print(f"# anchor: {ANCHOR}")
    print(f"# arxiv : {ARXIV}")
    print(f"# ssot  : {SSOT_URL}")
    print()
    print(f"# clusters ({len(clusters())}):")
    for c in clusters():
        n = len(by_cluster(c))
        print(f"  {c:22s}  {n:>3d} formats")
    print()
    print("use --list, --cluster NAME, --status LABEL, --show ID, --json.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
