"""MXFP4 conformance runner: bit-precise check of mxfp4 codec against vector pack.

Each vector carries:
    - input_f32  (list of 32 floats)
    - expected_scale_byte  (int, E8M0)
    - expected_nibbles     (list of 32 ints, 0..15)
    - expected_bytes_hex   (hex string of 1 + 16 packed bytes)
    - roundtrip_max_abs_error (diagnostic, not used in pass/fail)

Pass criterion: re-encode produces byte-identical scale + nibble pattern.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .mxfp4 import encode_block, pack_block_to_bytes


@dataclass(frozen=True)
class MxfpConformanceReport:
    total: int
    passed: int
    failed: int
    failures: list[dict]

    @property
    def ok(self) -> bool:
        return self.failed == 0

    def verdict_line(self, sha: str = "-") -> str:
        return (
            f"OK mxfp4_conform={'true' if self.ok else 'false'} "
            f"reasons={self.failed} sha256={sha}"
        )


def check_mxfp4_vectors(vectors: list[dict]) -> MxfpConformanceReport:
    failures: list[dict] = []
    passed = 0
    for v in vectors:
        inp = [float(x) for x in v["input_f32"]]
        got = encode_block(inp)
        exp_scale = v["expected_scale_byte"]
        exp_nibbles = tuple(v["expected_nibbles"])
        if got.scale_byte != exp_scale:
            failures.append({
                "name": v["name"],
                "issue": "scale_byte_mismatch",
                "expected": exp_scale,
                "got": got.scale_byte,
            })
            continue
        if got.elements != exp_nibbles:
            diffs = [(i, e, g) for i, (e, g) in enumerate(zip(exp_nibbles, got.elements)) if e != g]
            failures.append({
                "name": v["name"],
                "issue": "nibble_mismatch",
                "first_diffs": diffs[:5],
            })
            continue
        # Re-pack to bytes and compare hex
        bytes_got = pack_block_to_bytes(got).hex()
        if bytes_got != v["expected_bytes_hex"]:
            failures.append({
                "name": v["name"],
                "issue": "bytes_mismatch",
                "expected": v["expected_bytes_hex"],
                "got": bytes_got,
            })
            continue
        passed += 1
    return MxfpConformanceReport(
        total=len(vectors),
        passed=passed,
        failed=len(failures),
        failures=failures,
    )


def load_mxfp4_pack(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    if data.get("schema") != "t27-conformance/v0.1":
        raise ValueError(f"schema mismatch: {data.get('schema')!r}")
    if data.get("format") != "MXFP4":
        raise ValueError(f"expected format MXFP4, got {data.get('format')!r}")
    return data
