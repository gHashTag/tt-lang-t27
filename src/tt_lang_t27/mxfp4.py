"""MXFP4 codec: bit-precise OCP S1E2M1 microscaling (block_size=32).

Layout matches tenstorrent/tt-metal kMxFp4Params exactly:
    block_size = 32
    scale_bias = 0x7F (E8M0 shared scale, bias 127)
    element = S(1) | E(2) | M(1)  packed 2-per-byte, no padding
    elem_exp_bias = 1
    elem_exp_max_unbiased = 2, min_unbiased = 0
    elem_exp_subnorm_encoding = 0  (E=0 -> subnormal)
    elem_man_max = 0x1
    sat_supported = true (sat_pos = 0x7, sat_neg = 0xF)
    inf / nan: NotRepresentable

Reference: OCP Microscaling Formats (MX) Specification v1.0,
mirrored in tt-metal `tt_metal/impl/data_format/mxfp4.cpp` (kMxFp4Params).

This is a pure-Python reference codec for conformance testing, not a
performance kernel.  Bit patterns match tt-metal's pack/unpack output
for the supported value subset.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass


BLOCK_SIZE = 32
SCALE_BIAS = 0x7F  # E8M0 bias
ELEM_EXP_BITS = 2
ELEM_MAN_BITS = 1
ELEM_EXP_BIAS = 1
ELEM_WIDTH_BITS = 4
ELEM_SAT_POS = 0x7   # +6.0  (sign=0, E=3, M=1)  -- max representable * 2^scale
ELEM_SAT_NEG = 0xF   # -6.0  (sign=1, E=3, M=1)


# All 16 4-bit codes -> decoded element value (before block-scale).
# S(1) | E(2) | M(1), bias=1.  E=0 subnormal (no implicit 1), E>=1 normal.
# E=0,M=0 -> +-0;  E=0,M=1 -> +-0.5;  E=1..3 normal: +-(1+M/2)*2^(E-1)
ELEM_DECODE = {}
for code in range(16):
    s = (code >> 3) & 0x1
    e = (code >> 1) & 0x3
    m = code & 0x1
    sgn = -1.0 if s else 1.0
    if e == 0:
        val = sgn * (m / 2.0)            # 0 or +-0.5
    else:
        val = sgn * (1.0 + m / 2.0) * (2.0 ** (e - ELEM_EXP_BIAS))
    ELEM_DECODE[code] = val
# Sanity: positive set = {0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0}
# Note: 0x7 = sign=0, E=3, M=1 -> (1+0.5)*4 = 6.0 (= sat_pos_bits=0x7 per kMxFp4Params)


# Reverse map for encode: positive magnitudes -> (E, M) code without sign.
_POSITIVE_VALUES = sorted({ELEM_DECODE[c] for c in range(16) if ELEM_DECODE[c] >= 0.0})
# = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]


@dataclass(frozen=True)
class MxBlock:
    """One MXFP4 block: 32 4-bit elements + 1-byte E8M0 shared scale."""
    scale_byte: int            # 0..255 (E8M0; biased by 0x7F)
    elements: tuple[int, ...]  # length 32, each 0..15

    def __post_init__(self) -> None:
        if not (0 <= self.scale_byte <= 255):
            raise ValueError(f"scale_byte out of range: {self.scale_byte}")
        if len(self.elements) != BLOCK_SIZE:
            raise ValueError(f"block must have {BLOCK_SIZE} elements")
        for e in self.elements:
            if not (0 <= e <= 15):
                raise ValueError(f"element nibble out of range: {e}")


def _nearest_elem_code(positive_normalized: float) -> int:
    """Round-to-nearest-even to closest representable positive elem code (sign=0)."""
    # Clamp to saturation
    if positive_normalized >= 6.0:
        return ELEM_SAT_POS & 0x7    # 0x7 = sign-clear sat_pos
    if positive_normalized <= 0.0:
        return 0x0
    # Find closest in _POSITIVE_VALUES
    best_code = 0
    best_dist = float("inf")
    for code in range(8):  # sign=0 nibbles only
        v = ELEM_DECODE[code]
        d = abs(v - positive_normalized)
        if d < best_dist or (d == best_dist and (code & 1) == 0):
            best_dist = d
            best_code = code
    return best_code


def encode_block(values: list[float]) -> MxBlock:
    """Encode 32 floats into one MXFP4 block (E8M0 shared scale + 32 nibbles).

    Scale chosen so that max(|values|) <= 6.0 * 2^(scale - 127).
    """
    if len(values) != BLOCK_SIZE:
        raise ValueError(f"block must have {BLOCK_SIZE} values, got {len(values)}")
    abs_max = max((abs(v) for v in values), default=0.0)
    if abs_max == 0.0 or not math.isfinite(abs_max):
        # All zeros (or non-finite): pick scale=0 (i.e. 2^-127), all nibbles 0.
        return MxBlock(scale_byte=0, elements=tuple([0] * BLOCK_SIZE))
    # Element max representable is 6.0; pick scale_e so that abs_max / 2^(scale_e - bias) ~ 6
    # i.e. scale_e = bias + ceil(log2(abs_max / 6.0))
    needed = math.log2(abs_max / 6.0)
    scale_e = SCALE_BIAS + math.ceil(needed)
    scale_e = max(0, min(255, scale_e))
    scale_factor = 2.0 ** (scale_e - SCALE_BIAS)
    elems: list[int] = []
    for v in values:
        if v == 0.0:
            elems.append(0x8 if math.copysign(1.0, v) < 0 else 0x0)
            continue
        sign = 1 if v < 0 else 0
        normalized = abs(v) / scale_factor
        code_no_sign = _nearest_elem_code(normalized) & 0x7
        elems.append((sign << 3) | code_no_sign)
    return MxBlock(scale_byte=scale_e, elements=tuple(elems))


def decode_block(block: MxBlock) -> list[float]:
    """Decode one MXFP4 block back to 32 floats."""
    scale_factor = 2.0 ** (block.scale_byte - SCALE_BIAS)
    return [ELEM_DECODE[code] * scale_factor for code in block.elements]


def pack_block_to_bytes(block: MxBlock) -> bytes:
    """Pack one block: 1 scale byte + 16 element bytes (2 nibbles/byte, lo first).

    Matches tt-metal/mx_tile_pack layout convention: element[2*i] in low nibble.
    """
    out = bytearray()
    out.append(block.scale_byte & 0xFF)
    for i in range(0, BLOCK_SIZE, 2):
        lo = block.elements[i] & 0xF
        hi = block.elements[i + 1] & 0xF
        out.append((hi << 4) | lo)
    return bytes(out)


def unpack_bytes_to_block(payload: bytes) -> MxBlock:
    """Inverse of pack_block_to_bytes."""
    if len(payload) != 1 + BLOCK_SIZE // 2:
        raise ValueError(f"expected {1 + BLOCK_SIZE // 2} bytes, got {len(payload)}")
    scale_byte = payload[0]
    elements: list[int] = []
    for i in range(1, len(payload)):
        b = payload[i]
        elements.append(b & 0xF)
        elements.append((b >> 4) & 0xF)
    return MxBlock(scale_byte=scale_byte, elements=tuple(elements))


def encode_tensor(values: list[float]) -> list[MxBlock]:
    """Encode an arbitrary-length flat tensor into a list of MXFP4 blocks.

    Pads the last block with zeros if not a multiple of 32.
    """
    blocks: list[MxBlock] = []
    n = len(values)
    for start in range(0, n, BLOCK_SIZE):
        chunk = list(values[start : start + BLOCK_SIZE])
        if len(chunk) < BLOCK_SIZE:
            chunk += [0.0] * (BLOCK_SIZE - len(chunk))
        blocks.append(encode_block(chunk))
    return blocks


def decode_tensor(blocks: list[MxBlock], n_elements: int) -> list[float]:
    """Inverse of encode_tensor, trimming to original length."""
    out: list[float] = []
    for b in blocks:
        out.extend(decode_block(b))
    return out[:n_elements]


def block_max_abs_error(values: list[float]) -> float:
    """Round-trip max(|v - decode(encode(v))|) over one 32-block.  Diagnostic."""
    enc = encode_block(values)
    dec = decode_block(enc)
    return max(abs(a - b) for a, b in zip(values, dec))
