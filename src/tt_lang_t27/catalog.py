"""tt_lang_t27.catalog -- access to the full 83-format SSOT catalog.

The catalog is loaded from ``vectors/all_formats_v0.json``, shipped inside
the wheel.  Its upstream source of truth is

    https://github.com/gHashTag/t27/blob/master/specs/numeric/formats_catalog.t27

(13 clusters; bootstrap grammar parsed by ``tools/gen_formats_catalog.py``).

This module exposes:

- ``Format``       -- a frozen dataclass for one record.
- ``CATALOG``      -- list of all 83 ``Format`` objects, in catalog order.
- ``ANCHOR``       -- the canonical anchor ``phi^2 + 1/phi^2 = 3 = L_2``.
- ``by_id(id)``    -- look up a format by its id (e.g. ``"bfloat16"``).
- ``by_cluster(c)``-- list all formats in a cluster (e.g. ``"GoldenFloat"``).
- ``by_status(s)`` -- list all formats with a status label.
- ``clusters()``   -- list of all 13 cluster names, in canonical order.
- ``statuses()``   -- list of all status labels used.
- ``as_dict()``    -- the raw JSON payload (read-only-by-convention).

Status labels are the ones the upstream catalog enforces, taken verbatim
from ``goldenfloat-ladder`` + ``igla-phi-architecture`` skills:

  Verified, EmpiricalFit, Open, Risk, Retracted, Experimental, Historical

Anchor identity ``phi^2 + 1/phi^2 = 3`` is exact in IEEE-754 double
arithmetic and is the canonical numerical sameness-check for any decoder.
Reference: arXiv:2606.05017 (GoldenFloat preprint).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from importlib.resources import files
from typing import Any, Dict, List, Optional, Tuple


ANCHOR: str = "phi^2 + 1/phi^2 = 3 = L_2"
ARXIV: str = "arXiv:2606.05017"
SSOT_URL: str = (
    "https://github.com/gHashTag/t27/blob/master/specs/numeric/"
    "formats_catalog.t27"
)


@dataclass(frozen=True)
class Format:
    """One numeric-format record from the SSOT catalog.

    All fields are strings as parsed from the catalog's ``CATALOG:`` lines;
    integer-valued fields (``bits``, ``s``, ``e``, ``m``, ``bias``) are
    exposed verbatim, with convenience properties ``bits_int``, ``s_int``,
    ``e_int``, ``m_int``, ``bias_int``, ``phi_distance_float`` for typed
    access.  ``phi_distance`` of ``-1.0`` is the catalog's sentinel for
    "undefined" (used for decimal / non radix-2 formats).
    """

    id: str
    name: str
    bits: str
    s: str
    e: str
    m: str
    bias: str
    phi_distance: str
    storage: str
    cluster: str
    status: str
    standard: str
    use_case: str
    gf_relation: str
    source: str

    # ---- typed convenience accessors -----------------------------------

    @property
    def bits_int(self) -> int:
        return int(self.bits)

    @property
    def s_int(self) -> int:
        return int(self.s)

    @property
    def e_int(self) -> int:
        return int(self.e)

    @property
    def m_int(self) -> int:
        return int(self.m)

    @property
    def bias_int(self) -> int:
        return int(self.bias)

    @property
    def phi_distance_float(self) -> float:
        return float(self.phi_distance)

    @property
    def phi_distance_defined(self) -> bool:
        return self.phi_distance_float >= 0.0

    def as_dict(self) -> Dict[str, str]:
        return asdict(self)


# ---- loader ------------------------------------------------------------


def _load_payload() -> Dict[str, Any]:
    """Load the shipped ``all_formats_v0.json`` resource."""
    pkg_root = files("tt_lang_t27").joinpath("..").joinpath("..")  # not used
    # Use the canonical path: vectors/all_formats_v0.json sits at the repo
    # root, but inside the wheel it is shipped under the data dir referenced
    # by importlib.resources via the package itself.  We embed by loading
    # alongside the package and falling back to the source-tree location.
    try:
        data = (
            files("tt_lang_t27")
            .joinpath("data")
            .joinpath("all_formats_v0.json")
            .read_text(encoding="utf-8")
        )
        return json.loads(data)
    except (FileNotFoundError, ModuleNotFoundError):
        # source-tree fallback for editable installs / tests
        import pathlib
        here = pathlib.Path(__file__).resolve().parent
        for candidate in [
            here / "data" / "all_formats_v0.json",
            here.parent.parent / "vectors" / "all_formats_v0.json",
        ]:
            if candidate.is_file():
                return json.loads(candidate.read_text(encoding="utf-8"))
        raise FileNotFoundError(
            "all_formats_v0.json not found in package data or source tree"
        )


_PAYLOAD: Dict[str, Any] = _load_payload()


def _build_catalog() -> List[Format]:
    out: List[Format] = []
    for r in _PAYLOAD["formats"]:
        # Defensive: ensure every required field exists with empty default
        record = {
            "id": r.get("id", ""),
            "name": r.get("name", ""),
            "bits": r.get("bits", "0"),
            "s": r.get("s", "0"),
            "e": r.get("e", "0"),
            "m": r.get("m", "0"),
            "bias": r.get("bias", "0"),
            "phi_distance": r.get("phi_distance", "-1.0"),
            "storage": r.get("storage", ""),
            "cluster": r.get("cluster", ""),
            "status": r.get("status", ""),
            "standard": r.get("standard", ""),
            "use_case": r.get("use_case", ""),
            "gf_relation": r.get("gf_relation", ""),
            "source": r.get("source", ""),
        }
        out.append(Format(**record))
    return out


CATALOG: Tuple[Format, ...] = tuple(_build_catalog())
_BY_ID: Dict[str, Format] = {f.id: f for f in CATALOG}


# ---- public lookups ----------------------------------------------------


def by_id(format_id: str) -> Format:
    """Return the Format with this id, or raise KeyError."""
    return _BY_ID[format_id]


def find(format_id: str) -> Optional[Format]:
    """Return the Format with this id, or None if not present."""
    return _BY_ID.get(format_id)


def by_cluster(cluster: str) -> List[Format]:
    """Return all formats in a cluster, in catalog order."""
    return [f for f in CATALOG if f.cluster == cluster]


def by_status(status: str) -> List[Format]:
    """Return all formats with this status label, in catalog order."""
    return [f for f in CATALOG if f.status == status]


def clusters() -> List[str]:
    """Return the 13 distinct cluster names in catalog order."""
    seen: List[str] = []
    for f in CATALOG:
        if f.cluster not in seen:
            seen.append(f.cluster)
    return seen


def statuses() -> List[str]:
    """Return distinct status labels in catalog order."""
    seen: List[str] = []
    for f in CATALOG:
        if f.status not in seen:
            seen.append(f.status)
    return seen


def count() -> int:
    """Return the total number of formats in the catalog."""
    return len(CATALOG)


def as_dict() -> Dict[str, Any]:
    """Return the raw JSON payload."""
    return dict(_PAYLOAD)


def ssot_source() -> str:
    """Return the upstream SSOT URL."""
    return SSOT_URL


__all__ = [
    "ANCHOR",
    "ARXIV",
    "SSOT_URL",
    "Format",
    "CATALOG",
    "by_id",
    "find",
    "by_cluster",
    "by_status",
    "clusters",
    "statuses",
    "count",
    "as_dict",
    "ssot_source",
]
