"""Conformance vector runner: bit-precise check of GF16 codec against vector pack."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .gf16 import gf16_decode, gf16_encode


@dataclass(frozen=True)
class ConformanceReport:
    total: int
    passed: int
    failed: int
    failures: list[dict]

    @property
    def ok(self) -> bool:
        return self.failed == 0

    def verdict_line(self, sha: str = "-") -> str:
        return (
            f"OK conform={'true' if self.ok else 'false'} "
            f"reasons={self.failed} sha256={sha}"
        )


def check_vectors(vectors: list[dict]) -> ConformanceReport:
    """Re-encode each vector's input_f64, compare against expected gf16_bits_int."""
    failures: list[dict] = []
    passed = 0
    for v in vectors:
        inp = v["input_f64"]
        if isinstance(inp, str) and inp == "NaN":
            inp_f = math.nan
        else:
            inp_f = float(inp)
        expected_bits = v["gf16_bits_int"]
        got_bits = gf16_encode(inp_f)
        if got_bits != expected_bits:
            failures.append(
                {
                    "name": v["name"],
                    "input": inp,
                    "expected_bits": expected_bits,
                    "got_bits": got_bits,
                }
            )
            continue
        # Round-trip check
        rt = gf16_decode(got_bits)
        if math.isnan(inp_f):
            if not math.isnan(rt):
                failures.append({"name": v["name"], "issue": "expected NaN", "got": rt})
                continue
        elif math.isinf(inp_f):
            if rt != inp_f:
                failures.append({"name": v["name"], "issue": "inf sign drift", "got": rt})
                continue
        passed += 1
    return ConformanceReport(
        total=len(vectors),
        passed=passed,
        failed=len(failures),
        failures=failures,
    )
