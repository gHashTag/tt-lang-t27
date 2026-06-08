# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-06-08

NVFP4 added, P3109 cross-walk doc, catalog invariants test, CLI subcommand refactor.

### Added

- **NVFP4 row** in the Microscaling cluster (status: Experimental,
  standard: NVIDIA Blackwell vendor-specific, ~4.5 bits/value with
  E4M3 block-scale-16 + FP32 per-tensor). Sources: NVIDIA developer
  blog 2025-06-24; MR-GPTQ arXiv:2509.23202. Mitigates W-14 from the
  tt-lang-integration-weakness-map.
- **`docs/P3109_CROSSWALK.md`** -- descriptive cluster-by-cluster map
  between the 84-format catalog and the IEEE P3109 working-group draft.
  10 in-scope rows enumerated (fp8/fp6/fp4 family + mxfp8/mxfp6/mxfp4
  + nvfp4). Mitigates W-15.
- **`tests/test_catalog_invariants.py`** -- 15 property-style invariants
  on the SSoT JSON (id uniqueness, slug shape, cluster partition,
  IEEE bit-sum identity, anchor/arxiv/url shape, JSON SHA-256
  stability). Mitigates W-17.
- **CLI subcommand refactor** (`tt-lang-t27-catalog count|list|cluster
  NAME|status LABEL|show ID|clusters|statuses|dump|anchor`) with
  `--json` as a global flag. Legacy `--count`/`--list`/etc. forms
  still work and are documented as deprecated. Mitigates W-16.

### Changed

- Catalog count: 83 -> 84.
- Microscaling cluster count: 3 -> 4.
- `tt_lang_t27.__version__`: 0.3.0 -> 0.3.1.
- JSON SHA-256:
  `01cd5d0b83b091bbd08345233a878c3402f6bac61db52a7b6f14b9c033677398`.
- All catalog docstrings/tests updated to say "84-format".

### Verified

- `pytest -q`: 55 tests pass (was 40 in 0.3.0; +15 new invariants).
- `tt-lang-t27-catalog count` returns 84.
- `tt-lang-t27-catalog cluster Microscaling` lists mxfp8/mxfp6/mxfp4/nvfp4.
- Anchor identity exact in IEEE-754 double: `phi^2 + 1/phi^2 == 3.0`.

## [0.3.0] - 2026-06-08

Full 83-format SSOT catalog from `gHashTag/t27` shipped inside the wheel.

### Added

- `tt_lang_t27.catalog` -- access to the full 83-format catalog from
  `gHashTag/t27/specs/numeric/formats_catalog.t27` (13 clusters,
  CI-enforced upstream).
- `Format` -- frozen dataclass with all 15 catalog fields plus typed
  accessors (`bits_int`, `s_int`, `e_int`, `m_int`, `bias_int`,
  `phi_distance_float`, `phi_distance_defined`).
- `CATALOG` -- tuple of all 83 `Format` objects in catalog order.
- Lookups: `by_id`, `find`, `by_cluster`, `by_status`, `clusters`,
  `statuses`, `count`, `as_dict`, `ssot_source`.
- Anchors: `ANCHOR = "phi^2 + 1/phi^2 = 3 = L_2"`, `ARXIV = "arXiv:2606.05017"`,
  `SSOT_URL` pointing at the upstream catalog file.
- `vectors/all_formats_v0.json` and shipped resource
  `tt_lang_t27/data/all_formats_v0.json` (SHA-256 canonical:
  `65c33c4b20318622dcd1538175c83dd4cfdf37341d78f926135ec0367a195b82`).
- `tt_lang_t27.cli_catalog` -- `tt-lang-t27-catalog` CLI entry
  (`--count`, `--list`, `--cluster`, `--status`, `--show`, `--clusters`,
  `--statuses`, `--json`, `--anchor`).
- 13 new tests, 40 total, all green on Python 3.10 / 3.11 / 3.12.

### Cluster summary (CI-enforced upstream)

```
Ieee754Binary       5  (binary16, 32, 64, 128, 256)
Ieee754Decimal      3  (decimal32, 64, 128)
ExtendedFloat       3  (x87_fp80, double-double, quad-double)
MlLowPrecision      7  (bfloat16, tf32, fp8 E4M3 / E5M2, fp6 / fp4)
Microscaling        3  (mxfp8, mxfp6, mxfp4)
QuantTuned          2  (nf4, afp)
PositUnumIII        8  (posit8/16/32/64, takum8/16/32/64)
Lns                 4  (lns8, 16, 32, 64)
GoldenFloat        22  (GFTernary, GF4..GF1024 + hybrids)
IntegerFixed        8  (int4..int128, q_format, bcd)
HistoricalVendor   10  (IBM HFP, VAX, Cray, x87, MS MBF, PDP-11...)
Theoretical         4  (minifloat, unum I/II, tapered)
CompressionTrick    4  (block_fp, shared_exp, per_channel, stoch_rnd)
----                 -
TOTAL              83
```

### Status labels (canonical)

`Verified`, `EmpiricalFit`, `Open`, `Risk`, `Retracted`, `Experimental`,
`Historical` -- mirrored from the upstream catalog header.

### Notes

- Catalog data is shipped as resource, not regenerated at install: the
  same SHA-256 is checked into both `vectors/` (repo-facing) and
  `src/tt_lang_t27/data/` (wheel-facing).
- Per-format codec implementations remain available only for `gf16` and
  `mxfp4` in this release; the catalog otherwise carries metadata only
  (bit layout, bias, cluster, status, standard, use case, gf_relation,
  source).  Codec implementations for additional formats will land in
  follow-up releases.
- Anchor `phi^2 + 1/phi^2 = 3` is exact in IEEE-754 double; reference
  arXiv:2606.05017.

[0.3.0]: https://github.com/gHashTag/tt-lang-t27/releases/tag/v0.3.0

## [0.2.0] - 2026-06-08

MXFP4 cross-validation against tt-metal `kMxFp4Params`.

### Added

- `tt_lang_t27.mxfp4` -- pure-Python reference codec for OCP MXFP4
  (S1E2M1, block_size=32, E8M0 shared scale).  Constants pinned to
  tenstorrent/tt-metal `tt_metal/impl/data_format/mxfp4.cpp`
  `kMxFp4Params`.
- `MxBlock` dataclass: `scale_byte` (E8M0, 0..255) + 32 4-bit elements.
- `encode_block` / `decode_block`: bit-precise codec, RNE rounding,
  saturation at `+-6.0 * 2^(scale-127)`.
- `pack_block_to_bytes` / `unpack_bytes_to_block`: 1 scale byte + 16
  packed nibble bytes (low nibble first).
- `encode_tensor` / `decode_tensor`: arbitrary-length flat tensors.
- `tt_lang_t27.conformance_mxfp4` -- vector pack runner returning
  `MxfpConformanceReport`.
- `tt_lang_t27.cli_mxfp4` -- `tt-lang-t27-mxfp4-conform` CLI entry.
- `vectors/mxfp4_conformance_v0.json` -- 12 reference blocks with
  expected scale byte + 32 nibbles + packed-bytes hex.
- `MXFP4` entry in `vectors/format-spec-001-sample.json`
  (`kind = ocp_microscaling`).
- Test suite extended: 11 new MXFP4 tests, 27 total, all green.

### Notes

- MXFP4 codec is bit-exact for the representable grid
  `{0, +-0.5, +-1, +-1.5, +-2, +-3, +-4, +-6} * 2^(scale-127)`.
- For value subset matching, parity with tt-metal's
  `pack_as_mxfp4_tiles<float>` can be verified externally; this repo
  provides the canonical conformance pack to do so.

[0.2.0]: https://github.com/gHashTag/tt-lang-t27/releases/tag/v0.2.0

## [0.1.0] - 2026-06-07

Initial public release.

### Added

- `tt_lang_t27.gf16` -- bit-precise GF16 encode/decode, anchored on the ASCII
  identity `phi^2 + 1/phi^2 = 3` (exact in IEEE-754 double).
- `tt_lang_t27.registry` -- format-spec loader (FORMAT-SPEC-001 shape).
- `tt_lang_t27.conformance` -- vector-pack runner returning `ConformanceReport`.
- `tt_lang_t27.decorator` -- `@t27_kernel` Python decorator emitting a
  deterministic provenance tag
  `sha256(kernel_name || ssot_commit || fmt || anchor_hash)`.
- `tt_lang_t27.cli` -- `tt-lang-t27-conform` CLI entry point.
- `vectors/gf16_conformance_v0.json` -- 21 reference vectors,
  SHA-256 `7aea5b9e86ea71a54ae0c1601cea13e2d90d95fecaf2ae969eac1349cf7a2b42`.
- `vectors/format-spec-001-sample.json` -- minimal sample registry entry.
- Test suite: 16 unit tests including the anchor identity exact-equality check.
- `AGENTS.md`, `CONTRIBUTING.md`, `LICENSE` (Apache-2.0).

### Numeric reference

- arXiv:2606.05017 (cs.AR) -- GoldenFloat preprint (anchor-format family).

[0.1.0]: https://github.com/gHashTag/tt-lang-t27/releases/tag/v0.1.0
