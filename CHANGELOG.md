# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
