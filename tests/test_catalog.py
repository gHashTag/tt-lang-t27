"""Tests for the 83-format SSOT catalog."""

from __future__ import annotations

import pytest

from tt_lang_t27 import catalog
from tt_lang_t27.catalog import (
    ANCHOR,
    ARXIV,
    SSOT_URL,
    CATALOG,
    Format,
    by_cluster,
    by_id,
    by_status,
    clusters,
    count,
    find,
    statuses,
)


def test_catalog_loads_83_formats():
    assert count() == 83
    assert len(CATALOG) == 83
    assert isinstance(CATALOG[0], Format)


def test_catalog_anchor_and_arxiv():
    assert ANCHOR == "phi^2 + 1/phi^2 = 3 = L_2"
    assert ARXIV == "arXiv:2606.05017"
    assert SSOT_URL.startswith("https://github.com/gHashTag/t27/")
    assert "formats_catalog.t27" in SSOT_URL


def test_thirteen_clusters_with_expected_counts():
    # The upstream catalog has 13 clusters, summing to 83 with
    # cluster counts CI-enforced upstream.
    expected = {
        "Ieee754Binary": 5,
        "Ieee754Decimal": 3,
        "ExtendedFloat": 3,
        "MlLowPrecision": 7,
        "Microscaling": 3,
        "QuantTuned": 2,
        "PositUnumIII": 8,
        "Lns": 4,
        "GoldenFloat": 22,
        "IntegerFixed": 8,
        "HistoricalVendor": 10,
        "Theoretical": 4,
        "CompressionTrick": 4,
    }
    assert sum(expected.values()) == 83
    cl = clusters()
    assert len(cl) == 13
    assert set(cl) == set(expected)
    for name, n in expected.items():
        assert len(by_cluster(name)) == n, name


def test_lookup_by_id_known_anchors():
    bf = by_id("bfloat16")
    assert bf.bits_int == 16
    assert bf.e_int == 8
    assert bf.m_int == 7
    assert bf.bias_int == 127
    assert bf.cluster == "MlLowPrecision"

    gf = by_id("gf16")
    assert gf.bits_int == 16
    assert gf.cluster == "GoldenFloat"

    mx = by_id("mxfp4")
    assert mx.cluster == "Microscaling"


def test_find_returns_none_for_missing():
    assert find("does_not_exist") is None


def test_by_id_raises_for_missing():
    with pytest.raises(KeyError):
        by_id("does_not_exist")


def test_status_labels_are_canonical():
    # Status labels must be drawn from the canonical set per the catalog
    # header.  We do not assert every label is present; we assert no
    # extras.
    canonical = {
        "Verified",
        "EmpiricalFit",
        "Open",
        "Risk",
        "Retracted",
        "Experimental",
        "Historical",
    }
    seen = set(statuses())
    assert seen.issubset(canonical), seen - canonical


def test_at_least_some_verified_formats():
    verified = by_status("Verified")
    # IEEE 754 binary family + GF16 etc must be Verified
    ids = {f.id for f in verified}
    assert "binary32" in ids
    assert "binary64" in ids
    assert "bfloat16" in ids
    assert "gf16" in ids


def test_phi_distance_sentinel_handled():
    # Decimal formats use the -1.0 sentinel for "undefined"
    d = by_id("decimal32")
    assert d.phi_distance_float == -1.0
    assert d.phi_distance_defined is False
    # Radix-2 formats have a defined phi_distance
    bf = by_id("bfloat16")
    assert bf.phi_distance_defined is True
    assert 0.0 <= bf.phi_distance_float <= 1.0


def test_dataclass_is_frozen():
    f = CATALOG[0]
    with pytest.raises(Exception):
        f.id = "mutated"


def test_as_dict_returns_complete_record():
    f = by_id("bfloat16")
    d = f.as_dict()
    required = {
        "id", "name", "bits", "s", "e", "m", "bias",
        "phi_distance", "storage", "cluster", "status",
        "standard", "use_case", "gf_relation", "source",
    }
    assert required.issubset(set(d.keys()))


def test_goldenfloat_ladder_has_all_rungs():
    # GF cluster should include the canonical ladder + extras
    gf = {f.id for f in by_cluster("GoldenFloat")}
    canonical_ladder = {
        "gfternary", "gf4", "gf8", "gf16", "gf32", "gf64",
        "gf128", "gf256", "gf512", "gf1024",
    }
    assert canonical_ladder.issubset(gf), canonical_ladder - gf


def test_module_namespace_exposes_catalog():
    # Public re-exports from tt_lang_t27 top-level
    import tt_lang_t27 as m
    assert m.catalog_count() == 83
    assert m.ANCHOR == ANCHOR
    assert isinstance(m.CATALOG, tuple)
    assert m.by_id("bfloat16").e_int == 8
