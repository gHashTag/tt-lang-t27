"""tt-lang-t27-catalog -- CLI for the 84-format SSOT catalog.

v0.3.1 ergonomic refactor: subcommand-style CLI.

New (preferred) form:

    tt-lang-t27-catalog count
    tt-lang-t27-catalog list
    tt-lang-t27-catalog clusters
    tt-lang-t27-catalog statuses
    tt-lang-t27-catalog cluster GoldenFloat
    tt-lang-t27-catalog status Verified
    tt-lang-t27-catalog show bfloat16
    tt-lang-t27-catalog dump
    tt-lang-t27-catalog anchor

Old (deprecated, still works) form:

    tt-lang-t27-catalog --count
    tt-lang-t27-catalog --list
    tt-lang-t27-catalog --cluster GoldenFloat
    tt-lang-t27-catalog --status Verified
    tt-lang-t27-catalog --show bfloat16
    tt-lang-t27-catalog --clusters
    tt-lang-t27-catalog --statuses
    tt-lang-t27-catalog --json
    tt-lang-t27-catalog --anchor

Both forms accept ``--json`` as a flag to emit machine-readable JSON.
The default invocation (no args) prints a summary header.
"""

from __future__ import annotations

import argparse
import json as _json
import sys
from typing import List, Optional

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


# ---- formatting helpers ----------------------------------------------------


def _fmt_row(f: Format) -> str:
    pd = f.phi_distance if f.phi_distance_defined else "  N/A"
    return (
        f"  {f.id:24s}  {f.cluster:18s}  bits={f.bits:>4s}  "
        f"s={f.s:>1s}  e={f.e:>3s}  m={f.m:>4s}  "
        f"phi={pd:>6s}  status={f.status}"
    )


def _print_list(rows: List[Format], emit_json: bool) -> None:
    if emit_json:
        _json.dump([r.as_dict() for r in rows], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    print(f"# {len(rows)} formats")
    for r in rows:
        print(_fmt_row(r))


def _print_anchor() -> None:
    print(f"# anchor: {ANCHOR}")
    print(f"# arxiv : {ARXIV}")
    print(f"# ssot  : {SSOT_URL}")


# ---- per-subcommand handlers ----------------------------------------------


def _cmd_count(args) -> int:
    if args.json:
        _json.dump({"count": count()}, sys.stdout)
        sys.stdout.write("\n")
    else:
        print(count())
    return 0


def _cmd_list(args) -> int:
    _print_list(list(CATALOG), args.json)
    return 0


def _cmd_clusters(args) -> int:
    if args.json:
        out = {c: len(by_cluster(c)) for c in clusters()}
        _json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    for c in clusters():
        print(f"{c:22s}  {len(by_cluster(c)):>3d} formats")
    return 0


def _cmd_statuses(args) -> int:
    if args.json:
        out = {s: len(by_status(s)) for s in statuses()}
        _json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    for s in statuses():
        print(f"{s:14s}  {len(by_status(s)):>3d} formats")
    return 0


def _cmd_cluster(args) -> int:
    rows = by_cluster(args.name)
    if not rows:
        print(
            f"error: no formats in cluster {args.name!r}",
            file=sys.stderr,
        )
        print(f"known clusters: {clusters()}", file=sys.stderr)
        return 2
    _print_list(rows, args.json)
    return 0


def _cmd_status(args) -> int:
    rows = by_status(args.label)
    if not rows:
        print(
            f"error: no formats with status {args.label!r}",
            file=sys.stderr,
        )
        print(f"known statuses: {statuses()}", file=sys.stderr)
        return 2
    _print_list(rows, args.json)
    return 0


def _cmd_show(args) -> int:
    f = find(args.id)
    if f is None:
        print(f"error: no format with id {args.id!r}", file=sys.stderr)
        return 2
    if args.json:
        _json.dump(f.as_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    for k, v in f.as_dict().items():
        print(f"  {k:14s}: {v}")
    return 0


def _cmd_dump(args) -> int:
    _json.dump(as_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _cmd_anchor(args) -> int:
    if args.json:
        _json.dump(
            {"anchor": ANCHOR, "arxiv": ARXIV, "ssot_url": SSOT_URL},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    _print_anchor()
    return 0


def _cmd_summary(args) -> int:
    if args.anchor:
        _print_anchor()
        print()
    print(f"# tt_lang_t27 catalog -- {count()} formats")
    _print_anchor()
    print()
    print(f"# clusters ({len(clusters())}):")
    for c in clusters():
        n = len(by_cluster(c))
        print(f"  {c:22s}  {n:>3d} formats")
    print()
    print("use: count | list | clusters | statuses | "
          "cluster NAME | status LABEL | show ID | dump | anchor")
    return 0


# ---- argparse wiring -------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tt-lang-t27-catalog",
        description=(
            "Inspect the 84-format SSOT numeric catalog "
            "(t27 specs/numeric/formats_catalog.t27). "
            "Anchor: phi^2 + 1/phi^2 = 3 = L_2 (arXiv:2606.05017)."
        ),
    )
    # global flags (work with subcommands AND legacy form)
    p.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of text.",
    )
    p.add_argument(
        "--anchor",
        action="store_true",
        help="also print the anchor identity, arXiv ref, and SSOT URL.",
    )

    sub = p.add_subparsers(dest="cmd", metavar="COMMAND")

    sub.add_parser("count", help="print the total number of formats")
    sub.add_parser("list", help="print every format in catalog order")
    sub.add_parser("clusters", help="list cluster names with row counts")
    sub.add_parser("statuses", help="list status labels with row counts")
    sub.add_parser("dump", help="dump the full catalog as JSON")
    sub.add_parser("anchor", help="print anchor + arXiv + SSOT URL")

    s_cluster = sub.add_parser("cluster", help="print formats in a cluster")
    s_cluster.add_argument("name", help="cluster name (e.g. GoldenFloat)")

    s_status = sub.add_parser("status", help="print formats with a status")
    s_status.add_argument("label", help="status label (e.g. Verified)")

    s_show = sub.add_parser("show", help="print one format by id")
    s_show.add_argument("id", help="format id (e.g. bfloat16)")

    # legacy long-flag aliases (back-compat with v0.3.0)
    legacy = p.add_argument_group(
        "legacy flags (deprecated, kept for back-compat)"
    )
    legacy.add_argument("--count", dest="legacy_count", action="store_true")
    legacy.add_argument("--list", dest="legacy_list", action="store_true")
    legacy.add_argument("--clusters", dest="legacy_clusters",
                        action="store_true")
    legacy.add_argument("--statuses", dest="legacy_statuses",
                        action="store_true")
    legacy.add_argument("--cluster", dest="legacy_cluster", metavar="NAME")
    legacy.add_argument("--status", dest="legacy_status", metavar="LABEL")
    legacy.add_argument("--show", dest="legacy_show", metavar="ID")

    return p


_HANDLERS = {
    "count": _cmd_count,
    "list": _cmd_list,
    "clusters": _cmd_clusters,
    "statuses": _cmd_statuses,
    "cluster": _cmd_cluster,
    "status": _cmd_status,
    "show": _cmd_show,
    "dump": _cmd_dump,
    "anchor": _cmd_anchor,
}


def _resolve_legacy(args) -> Optional[str]:
    """If a legacy flag is set, return the subcommand it maps to and
    rewrite args in place.  Returns None if no legacy flag set."""
    if args.legacy_count:
        return "count"
    if args.legacy_list:
        return "list"
    if args.legacy_clusters:
        return "clusters"
    if args.legacy_statuses:
        return "statuses"
    if args.legacy_cluster:
        args.name = args.legacy_cluster
        return "cluster"
    if args.legacy_status:
        args.label = args.legacy_status
        return "status"
    if args.legacy_show:
        args.id = args.legacy_show
        return "show"
    return None


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # legacy --foo flags translate to the equivalent subcommand
    legacy_cmd = _resolve_legacy(args)
    cmd = args.cmd or legacy_cmd

    if cmd is None:
        return _cmd_summary(args)

    handler = _HANDLERS.get(cmd)
    if handler is None:  # pragma: no cover
        parser.error(f"unknown subcommand: {cmd}")
        return 2
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
