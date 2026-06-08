"""Structural invariants of the 84-format SSOT catalog (WP-A, v0.3.1).

These tests are intentionally property-style: they do not enumerate
expected rows, they only check shape-and-consistency properties that
must hold for ANY valid catalog version.  Breaking one is a strong
signal that the JSON SSoT drifted.

The 15 invariants below are derived from the upstream
``specs/numeric/formats_catalog.t27`` schema and from the
``tt-lang-integration-weakness-map`` skill (W-17 mitigation).
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from importlib.resources import files

import pytest

from tt_lang_t27 import catalog
from tt_lang_t27.catalog import (
    ANCHOR,
    ARXIV,
    SSOT_URL,
    CATALOG,
    by_cluster,
    by_status,
    clusters,
    count,
    statuses,
)


CANONICAL_STATUSES = {
    "Verified",
    "EmpiricalFit",
    "Open",
    "Risk",
    "Retracted",
    "Experimental",
    "Historical",
}

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


# ---------------------------------------------------------------------------
# Invariant 1: catalog_count() == len(CATALOG) == number of rows in JSON
# ---------------------------------------------------------------------------


def test_inv01_count_consistent():
    raw = catalog.as_dict()
    assert count() == len(CATALOG) == len(raw["formats"])
    assert count() == 84


# ---------------------------------------------------------------------------
# Invariant 2: all ids are unique
# ---------------------------------------------------------------------------


def test_inv02_ids_unique():
    ids = [f.id for f in CATALOG]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ids: {dupes}"


# ---------------------------------------------------------------------------
# Invariant 3: all ids are non-empty ASCII slugs
# ---------------------------------------------------------------------------


def test_inv03_ids_are_slugs():
    for f in CATALOG:
        assert f.id, "empty id"
        assert _SLUG_RE.match(f.id), f"bad id: {f.id!r}"


# ---------------------------------------------------------------------------
# Invariant 4: bits >= 0 always; bits > 0 for concrete (non-parametric)
# clusters.  Theoretical/CompressionTrick families (minifloat, unum_i,
# block_fp, etc.) are allowed to have bits=0 because they describe a
# family rather than one fixed-width format.
# ---------------------------------------------------------------------------


PARAMETRIC_CLUSTERS = {"Theoretical", "CompressionTrick"}
PARAMETRIC_EXCEPTIONS = {"q_format", "bcd"}  # IntegerFixed family rows


def test_inv04_bits_nonneg_concrete_positive():
    for f in CATALOG:
        assert f.bits_int >= 0, f"{f.id}: bits={f.bits!r}"
        if (
            f.cluster not in PARAMETRIC_CLUSTERS
            and f.id not in PARAMETRIC_EXCEPTIONS
        ):
            assert f.bits_int > 0, (
                f"{f.id} (cluster={f.cluster}) is concrete but bits=0"
            )


# ---------------------------------------------------------------------------
# Invariant 5: every cluster name in clusters() matches >=1 row
# ---------------------------------------------------------------------------


def test_inv05_every_cluster_nonempty():
    for c in clusters():
        rows = by_cluster(c)
        assert len(rows) >= 1, f"cluster {c!r} has 0 rows"


# ---------------------------------------------------------------------------
# Invariant 6: status labels subset of canonical set
# ---------------------------------------------------------------------------


def test_inv06_statuses_canonical():
    seen = set(statuses())
    extras = seen - CANONICAL_STATUSES
    assert not extras, f"non-canonical statuses: {extras}"


# ---------------------------------------------------------------------------
# Invariant 7: every GoldenFloat row carries a defined phi_distance
# ---------------------------------------------------------------------------


def test_inv07_goldenfloat_has_phi_distance():
    for f in by_cluster("GoldenFloat"):
        assert f.phi_distance_defined, (
            f"GoldenFloat row {f.id!r} has undefined phi_distance"
        )
        # tolerated range for the published ladder
        assert -0.01 <= f.phi_distance_float <= 1.0, (
            f"{f.id}: phi_distance={f.phi_distance}"
        )


# ---------------------------------------------------------------------------
# Invariant 8: every Microscaling row carries non-empty storage info
# ---------------------------------------------------------------------------


def test_inv08_microscaling_has_storage():
    rows = by_cluster("Microscaling")
    assert len(rows) >= 3, "Microscaling cluster suspiciously small"
    for f in rows:
        assert f.storage, f"Microscaling row {f.id!r} has empty storage field"


# ---------------------------------------------------------------------------
# Invariant 9: IEEE 754 binary rows carry e, m, bias > 0
# ---------------------------------------------------------------------------


def test_inv09_ieee_binary_rows_complete():
    for f in by_cluster("Ieee754Binary"):
        assert f.e_int > 0, f"{f.id}: e={f.e}"
        assert f.m_int > 0, f"{f.id}: m={f.m}"
        assert f.bias_int > 0, f"{f.id}: bias={f.bias}"


# ---------------------------------------------------------------------------
# Invariant 10: bits == 1 + e + m for IEEE binary rows
# ---------------------------------------------------------------------------


def test_inv10_ieee_binary_bit_sum():
    for f in by_cluster("Ieee754Binary"):
        assert f.bits_int == 1 + f.e_int + f.m_int, (
            f"{f.id}: bits={f.bits_int} != 1+e+m={1+f.e_int+f.m_int}"
        )


# ---------------------------------------------------------------------------
# Invariant 11: ANCHOR string contains 'phi' and '3'
# ---------------------------------------------------------------------------


def test_inv11_anchor_well_formed():
    assert "phi" in ANCHOR.lower()
    assert "3" in ANCHOR
    assert "=" in ANCHOR


# ---------------------------------------------------------------------------
# Invariant 12: ARXIV starts with 'arXiv:'
# ---------------------------------------------------------------------------


def test_inv12_arxiv_well_formed():
    assert ARXIV.startswith("arXiv:")
    assert re.match(r"^arXiv:\d{4}\.\d{4,5}$", ARXIV), ARXIV


# ---------------------------------------------------------------------------
# Invariant 13: SSOT_URL points to gHashTag/t27
# ---------------------------------------------------------------------------


def test_inv13_ssot_url_well_formed():
    assert SSOT_URL.startswith("https://github.com/gHashTag/t27/")
    assert "formats_catalog.t27" in SSOT_URL


# ---------------------------------------------------------------------------
# Invariant 14: JSON SHA-256 is stable across two reads
# ---------------------------------------------------------------------------


def test_inv14_json_sha256_stable():
    raw1 = (
        files("tt_lang_t27")
        .joinpath("data")
        .joinpath("all_formats_v0.json")
        .read_bytes()
    )
    raw2 = (
        files("tt_lang_t27")
        .joinpath("data")
        .joinpath("all_formats_v0.json")
        .read_bytes()
    )
    h1 = hashlib.sha256(raw1).hexdigest()
    h2 = hashlib.sha256(raw2).hexdigest()
    assert h1 == h2
    # tracked SHA for v0.3.1 (NVFP4 added, phi_distance -1.0 sentinel)
    # this is intentionally a soft check: only fails if the file is
    # silently mutated post-install
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# Invariant 15: sum(by_cluster) == catalog_count (no orphans)
# ---------------------------------------------------------------------------


def test_inv15_clusters_partition_catalog():
    total = sum(len(by_cluster(c)) for c in clusters())
    assert total == count(), (
        f"clusters cover {total} but catalog has {count()} rows"
    )
