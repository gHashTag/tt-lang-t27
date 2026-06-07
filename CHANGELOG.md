# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
