"""Bit-precise tests for MXFP4 codec (parity with tt-metal kMxFp4Params)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from tt_lang_t27 import (
    BLOCK_SIZE,
    SCALE_BIAS,
    MxBlock,
    check_mxfp4_vectors,
    decode_block,
    decode_tensor,
    encode_block,
    encode_tensor,
    load_mxfp4_pack,
    pack_block_to_bytes,
    unpack_bytes_to_block,
)


HERE = Path(__file__).resolve().parent
VECTORS_PATH = HERE.parent / "vectors" / "mxfp4_conformance_v0.json"


def test_block_size_constants():
    assert BLOCK_SIZE == 32
    assert SCALE_BIAS == 0x7F


def test_representable_grid_exact():
    """Positive grid {0, 0.5, 1, 1.5, 2, 3, 4, 6} must round-trip exactly when block-scale lands."""
    grid = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
    # repeat to fill a 32-block
    values = (grid * 4)
    assert len(values) == 32
    block = encode_block(values)
    decoded = decode_block(block)
    for v, d in zip(values, decoded):
        assert v == d, f"grid value {v} did not round-trip exactly (got {d})"


def test_negative_grid_exact():
    grid = [-6.0, -4.0, -3.0, -2.0, -1.5, -1.0, -0.5, 0.0]
    values = grid * 4
    block = encode_block(values)
    decoded = decode_block(block)
    for v, d in zip(values, decoded):
        assert v == d


def test_pack_unpack_bytes_roundtrip():
    """Packed bytes must round-trip through unpack to the same MxBlock."""
    values = [(i % 7) - 3 for i in range(32)]
    block = encode_block([float(v) for v in values])
    payload = pack_block_to_bytes(block)
    assert len(payload) == 1 + BLOCK_SIZE // 2  # 17 bytes
    recovered = unpack_bytes_to_block(payload)
    assert recovered.scale_byte == block.scale_byte
    assert recovered.elements == block.elements


def test_tensor_encode_decode_length():
    values = [float(i) * 0.5 for i in range(100)]
    blocks = encode_tensor(values)
    assert len(blocks) == math.ceil(100 / 32)
    decoded = decode_tensor(blocks, n_elements=100)
    assert len(decoded) == 100


def test_saturation_clamps_to_six():
    """Per-element nibble must always be in the representable grid {0, +-0.5, ..., +-6}."""
    values = [1e9] * 32
    block = encode_block(values)
    decoded = decode_block(block)
    scale_factor = 2.0 ** (block.scale_byte - SCALE_BIAS)
    for d in decoded:
        elem = d / scale_factor
        assert elem in {0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0,
                        -0.5, -1.0, -1.5, -2.0, -3.0, -4.0, -6.0}
        assert abs(elem) <= 6.0  # never exceeds positive saturation bound


def test_zero_block_scale_is_zero():
    values = [0.0] * 32
    block = encode_block(values)
    assert block.scale_byte == 0
    assert all(e == 0 for e in block.elements)


def test_signed_zero_handling():
    """All-zero (incl. neg zero) input must produce all-zero block: scale=0, nibbles all 0.

    Note: tt-metal kMxFp4Params does not require preserving -0 sign at the nibble level
    when the block is uniform zero (scale_byte=0 dominates).  This test pins our chosen
    behaviour: uniform-zero block -> canonical all-zero output.
    """
    values = [-0.0] + [0.0] * 31
    block = encode_block(values)
    # Uniform-zero block: scale=0, all nibbles 0
    assert block.scale_byte == 0
    assert all(e == 0 for e in block.elements)


def test_vector_pack_loads_and_passes():
    if not VECTORS_PATH.exists():
        pytest.skip("mxfp4 vectors not present")
    pack = load_mxfp4_pack(VECTORS_PATH)
    report = check_mxfp4_vectors(pack["vectors"])
    assert report.ok, f"failures: {report.failures}"
    assert report.total == 12


def test_vector_pack_metadata():
    if not VECTORS_PATH.exists():
        pytest.skip("mxfp4 vectors not present")
    pack = load_mxfp4_pack(VECTORS_PATH)
    assert pack["format"] == "MXFP4"
    assert pack["block_size"] == 32
    assert pack["scale_bias"] == 0x7F
    assert pack["element_layout"] == "S1E2M1"
    assert pack["saturation"] is True
    ref = pack.get("reference_impl") or pack.get("reference_implementation", "")
    assert "tt-metal" in ref


def test_anchor_in_pack():
    if not VECTORS_PATH.exists():
        pytest.skip("mxfp4 vectors not present")
    pack = load_mxfp4_pack(VECTORS_PATH)
    assert pack["anchor_identity"] == "phi^2 + 1/phi^2 = 3"
    assert "2606.05017" in pack["anchor_url"]
