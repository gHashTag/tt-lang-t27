"""GF16 codec: bit-precise encode/decode mirroring t27 FORMAT_REGISTRY.md.

GF16 layout (sign-magnitude, single-stage normalised):
    [ S(1) | E(6) | M(9) ]   bits 15..0
    bias = 31
    value = (-1)^S * 2^(E - 31) * (1 + M / 2^9)   for normals
"""

from __future__ import annotations

import hashlib
import math
import struct

ANCHOR_TEXT = "phi^2 + 1/phi^2 = 3"


def anchor_hash() -> str:
    """SHA-256 of the canonical anchor identity string (ASCII)."""
    return hashlib.sha256(ANCHOR_TEXT.encode("ascii")).hexdigest()


def gf16_encode(value: float) -> int:
    """Encode a Python float into a GF16 bit pattern (16-bit int)."""
    if math.isnan(value):
        return 0x7FFF
    if value == 0.0:
        sign = 1 if math.copysign(1.0, value) < 0 else 0
        return sign << 15
    sign = 1 if value < 0 else 0
    a = abs(value)
    if math.isinf(a):
        return (sign << 15) | (0x3F << 9)
    exp_unbiased = math.floor(math.log2(a))
    mant_frac = a / (2.0 ** exp_unbiased) - 1.0
    E = exp_unbiased + 31
    if E <= 0:
        scaled = a / (2.0 ** -30)
        M = int(round(scaled * (1 << 9)))
        if M >= (1 << 9):
            E, M = 1, 0
        return (sign << 15) | (M & 0x1FF)
    if E >= 63:
        return (sign << 15) | (0x3F << 9)
    M = int(round(mant_frac * (1 << 9)))
    if M >= (1 << 9):
        M = 0
        E += 1
        if E >= 63:
            return (sign << 15) | (0x3F << 9)
    return (sign << 15) | ((E & 0x3F) << 9) | (M & 0x1FF)


def gf16_decode(bits: int) -> float:
    """Decode a GF16 bit pattern back to a Python float."""
    bits &= 0xFFFF
    sign = (bits >> 15) & 0x1
    E = (bits >> 9) & 0x3F
    M = bits & 0x1FF
    sgn = -1.0 if sign else 1.0
    if E == 0:
        if M == 0:
            return sgn * 0.0
        return sgn * (2.0 ** -30) * (M / (1 << 9))
    if E == 63:
        if M == 0:
            return sgn * math.inf
        return math.nan
    return sgn * (2.0 ** (E - 31)) * (1.0 + M / (1 << 9))


def f64_hex(value: float) -> str:
    if math.isnan(value):
        return "NaN"
    packed = struct.pack(">d", value)
    return "0x" + packed.hex().upper()
