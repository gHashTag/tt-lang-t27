"""Registry loader for t27 FORMAT-SPEC-001 SSOT and conformance vector packs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


REGISTRY_SCHEMA = "t27-format-spec/v0.1"
VECTORS_SCHEMA = "t27-conformance/v0.1"


@dataclass(frozen=True)
class FormatSpec:
    name: str
    kind: str
    bits: int
    sign_bits: int
    exponent_bits: int
    mantissa_bits: int
    bias: int
    encoding: str
    decoded_value_formula: str
    status: str
    conformance_vectors_path: str | None = None
    proof_path: str | None = None
    proof_sha256: str | None = None


@dataclass(frozen=True)
class Registry:
    ssot_commit: str
    anchor_identity: str
    anchor_hash_sha256: str
    formats: dict[str, FormatSpec] = field(default_factory=dict)


def load_registry(path: str | Path) -> Registry:
    data = json.loads(Path(path).read_text())
    if data.get("schema") != REGISTRY_SCHEMA:
        raise ValueError(f"registry schema mismatch: {data.get('schema')!r}")
    formats: dict[str, FormatSpec] = {}
    for name, f in data["formats"].items():
        formats[name] = FormatSpec(
            name=name,
            kind=f["kind"],
            bits=f["bits"],
            sign_bits=f["sign_bits"],
            exponent_bits=f["exponent_bits"],
            mantissa_bits=f["mantissa_bits"],
            bias=f["bias"],
            encoding=f["encoding"],
            decoded_value_formula=f["decoded_value_formula"],
            status=f["status"],
            conformance_vectors_path=f.get("conformance_vectors"),
            proof_path=f.get("proof_path"),
            proof_sha256=f.get("proof_sha256"),
        )
    return Registry(
        ssot_commit=data["ssot_commit"],
        anchor_identity=data["anchor_identity"],
        anchor_hash_sha256=data["anchor_hash_sha256"],
        formats=formats,
    )


def load_vectors(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text())
    if data.get("schema") != VECTORS_SCHEMA:
        raise ValueError(f"vectors schema mismatch: {data.get('schema')!r}")
    return data["vectors"]
