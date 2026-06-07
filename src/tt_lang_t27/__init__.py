"""tt-lang-t27: open numeric-format SSOT bridge for tt-lang kernels.

Apache-2.0.  ASCII only.  No upstream tt-lang dependency.
"""

from .registry import Registry, FormatSpec, load_registry, load_vectors
from .decorator import t27_kernel
from .conformance import check_vectors, ConformanceReport
from .gf16 import gf16_encode, gf16_decode, anchor_hash

__version__ = "0.1.0"

__all__ = [
    "Registry",
    "FormatSpec",
    "load_registry",
    "load_vectors",
    "t27_kernel",
    "check_vectors",
    "ConformanceReport",
    "gf16_encode",
    "gf16_decode",
    "anchor_hash",
]
