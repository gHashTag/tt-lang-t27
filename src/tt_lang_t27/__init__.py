"""tt-lang-t27: open numeric-format SSOT bridge for tt-lang kernels.

Apache-2.0.  ASCII only.  No upstream tt-lang dependency.
"""

from .registry import Registry, FormatSpec, load_registry, load_vectors
from .decorator import t27_kernel
from .conformance import check_vectors, ConformanceReport
from .conformance_mxfp4 import (
    check_mxfp4_vectors,
    load_mxfp4_pack,
    MxfpConformanceReport,
)
from .gf16 import gf16_encode, gf16_decode, anchor_hash
from .mxfp4 import (
    encode_block,
    decode_block,
    pack_block_to_bytes,
    unpack_bytes_to_block,
    encode_tensor,
    decode_tensor,
    MxBlock,
    BLOCK_SIZE,
    SCALE_BIAS,
)
from .catalog import (
    ANCHOR,
    ARXIV,
    SSOT_URL,
    CATALOG,
    Format,
    by_id,
    find,
    by_cluster,
    by_status,
    clusters,
    statuses,
    count as catalog_count,
    as_dict as catalog_as_dict,
    ssot_source,
)

__version__ = "0.3.1"

__all__ = [
    "Registry",
    "FormatSpec",
    "load_registry",
    "load_vectors",
    "t27_kernel",
    "check_vectors",
    "ConformanceReport",
    "check_mxfp4_vectors",
    "load_mxfp4_pack",
    "MxfpConformanceReport",
    "gf16_encode",
    "gf16_decode",
    "anchor_hash",
    "encode_block",
    "decode_block",
    "pack_block_to_bytes",
    "unpack_bytes_to_block",
    "encode_tensor",
    "decode_tensor",
    "MxBlock",
    "BLOCK_SIZE",
    "SCALE_BIAS",
    "ANCHOR",
    "ARXIV",
    "SSOT_URL",
    "CATALOG",
    "Format",
    "by_id",
    "find",
    "by_cluster",
    "by_status",
    "clusters",
    "statuses",
    "catalog_count",
    "catalog_as_dict",
    "ssot_source",
]
