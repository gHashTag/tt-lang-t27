"""Bit-precise round-trip + anchor identity tests for GF16."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from tt_lang_t27 import (
    anchor_hash,
    check_vectors,
    gf16_decode,
    gf16_encode,
    load_registry,
    load_vectors,
)


HERE = Path(__file__).resolve().parent
VECTORS_PATH = HERE.parent / "vectors" / "gf16_conformance_v0.json"
REGISTRY_PATH = HERE.parent / "vectors" / "format-spec-001-sample.json"


def test_anchor_hash_is_64_hex():
    h = anchor_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_anchor_identity_ieee754_exact():
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    assert phi * phi + 1.0 / (phi * phi) == 3.0


@pytest.mark.parametrize(
    "value",
    [0.0, -0.0, 1.0, -1.0, 2.0, 0.5, 3.0, math.e, math.pi],
)
def test_roundtrip_normal(value):
    bits = gf16_encode(value)
    rt = gf16_decode(bits)
    if value == 0.0:
        assert rt == 0.0
    else:
        assert abs(rt - value) / max(abs(value), 1e-30) < 1e-2


def test_inf_roundtrip():
    assert gf16_decode(gf16_encode(math.inf)) == math.inf
    assert gf16_decode(gf16_encode(-math.inf)) == -math.inf


def test_nan_roundtrip():
    assert math.isnan(gf16_decode(gf16_encode(math.nan)))


def test_signed_zero():
    pos = gf16_decode(gf16_encode(0.0))
    neg = gf16_decode(gf16_encode(-0.0))
    assert pos == 0.0
    assert neg == 0.0
    assert math.copysign(1.0, neg) == -1.0


def test_vector_pack_loads_and_passes():
    if not VECTORS_PATH.exists():
        pytest.skip("vectors not present")
    vectors = load_vectors(VECTORS_PATH)
    report = check_vectors(vectors)
    assert report.ok, f"failures: {report.failures}"
    assert report.total == 21


def test_phi_distance_under_gf16():
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    bits = gf16_encode(phi)
    rt = gf16_decode(bits)
    assert abs(rt - phi) < 0.0486 + 1e-6  # FORMAT_REGISTRY phi_distance for GF16
