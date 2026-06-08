# P3109 cross-walk -- mapping the 84-format catalog onto the IEEE WG draft

Status: descriptive, not normative.
Last reviewed: 2026-06-08 (catalog v0.3.1, 84 formats).
Anchor: phi^2 + 1/phi^2 = 3 = L_2 (arXiv:2606.05017).
Upstream SSoT: https://github.com/gHashTag/t27/blob/master/specs/numeric/formats_catalog.t27

## What P3109 is, in one paragraph

IEEE P3109 is the working group writing a portable interchange standard
for 8-bit and sub-8-bit floating-point formats used in machine
learning.  The public-facing wiki is at
https://sagroups.ieee.org/p3109wgpublic/.  As of mid-2026 the working
draft covers narrow floating-point binary formats (binary8, binary6,
binary4) with explicit fields for exponent width, significand width,
bias, finite/infinite encoding, and rounding rules.  It is the
successor effort to the OCP Microscaling-Formats spec
(Rouhani 2023, arXiv:2310.10537), which formalised MXFP8/MXFP6/MXFP4
with a block-scaled storage layout.

This document is a cross-walk: for every cluster in our 84-format
catalog, we state which rows are in P3109 scope, which are adjacent,
and which are outside.  We do NOT claim our catalog is normative; we
claim it is a complete, citeable inventory that lets a reviewer
compare any P3109 row against an equivalent third-party row in one
table look-up.

## Cluster-by-cluster mapping

| catalog cluster   | P3109 relation     | notes                                                           |
|-------------------|--------------------|-----------------------------------------------------------------|
| Ieee754Binary     | super-set          | binary16/32/64/128 are IEEE 754; P3109 narrows to <=8 bits.     |
| Ieee754Decimal    | out of scope       | decimal32/64/128 -- P3109 covers radix-2 only.                  |
| ExtendedFloat     | out of scope       | tf32, fp24 etc. -- vendor-specific extended widths.             |
| MlLowPrecision    | overlap            | bfloat16/fp16/fp8 family -- fp8_e4m3/e5m2 are P3109 candidates. |
| Microscaling      | aligned via MX spec| mxfp8/mxfp6/mxfp4 + nvfp4 -- OCP MX spec; P3109 cites.          |
| QuantTuned        | adjacent           | nf4, bitnet -- quant-tuned post-hoc, not P3109 binary.          |
| PositUnumIII      | out of scope       | posit8..256 -- Posit Standard, separate track.                  |
| Lns               | out of scope       | LNS family -- different number system.                          |
| GoldenFloat       | out of scope       | gf4..gf1024 -- phi-anchored tapered, separate manuscript.       |
| IntegerFixed      | out of scope       | int4..int64, q-format, bcd.                                     |
| HistoricalVendor  | out of scope       | IBM Hex Float, Cray, VAX, Burroughs etc.                        |
| Theoretical       | out of scope       | minifloat (family), unum I/II, tapered FP.                      |
| CompressionTrick  | adjacent           | block FP, shared-exponent, stochastic rounding.                 |

## P3109-scope rows (the short list)

The narrow set of rows that a P3109 reviewer cares about, in our
catalog terms, is:

- fp8_e4m3 (MlLowPrecision, Verified)
- fp8_e5m2 (MlLowPrecision, Verified)
- fp8 (MlLowPrecision umbrella, Open)
- fp6_e3m2 (MlLowPrecision, Experimental)
- fp6_e2m3 (MlLowPrecision, Experimental)
- fp4_e2m1 (MlLowPrecision, Experimental)
- mxfp8 (Microscaling, Verified)
- mxfp6 (Microscaling, Experimental)
- mxfp4 (Microscaling, Verified)
- nvfp4 (Microscaling, Experimental)

10 rows out of 84.  These are the formats the working group is
actively shaping; everything else in our catalog is either a
super-set (IEEE 754 wider), an alternative number system (Posit,
LNS, GoldenFloat), or a vendor/historical row.

## What this cross-walk is NOT

- It is not a proposal.  P3109 is an IEEE working group; we do not
  claim a seat or a vote.  We claim a public, citeable substrate
  any reviewer can use without asking us first.
- It is not a benchmark.  We do not assert any format is "better".
  The catalog records `status` (Verified / EmpiricalFit / Open /
  Risk / Retracted / Experimental / Historical) and a single
  `source` URL per row.  Numerical comparisons live in the
  conformance vector files (`vectors/*.json`), not here.
- It is not a competitor to the OCP MX spec.  OCP MX is upstream.
  Our Microscaling cluster cites Rouhani 2023 (arXiv:2310.10537)
  verbatim; NVFP4 cites NVIDIA developer blog 2025-06-24 and
  MR-GPTQ (arXiv:2509.23202) honestly as vendor-specific.

## How to use this document as a P3109 reviewer

1. Pick a row from "P3109-scope rows" above.
2. `tt-lang-t27-catalog --show <id>` returns the full record:
   bits, e, m, bias, storage layout, status, standard, use case,
   source URL.
3. Compare against the P3109 draft section for that format.
4. Discrepancies are bugs in the catalog; please file an issue at
   https://github.com/gHashTag/tt-lang-t27/issues.

## Provenance

- Catalog SHA-256 (v0.3.1):
  `01cd5d0b83b091bbd08345233a878c3402f6bac61db52a7b6f14b9c033677398`
- 84 formats, 13 clusters.
- Generated from the upstream t27 SSoT
  (`specs/numeric/formats_catalog.t27`) via
  `tools/gen_formats_catalog.py`.
- Anchor identity exact in IEEE-754 double:
  `phi^2 + 1/phi^2 == 3.0` (see `tests/test_catalog.py`).

## References

- IEEE P3109 working-group wiki:
  https://sagroups.ieee.org/p3109wgpublic/
- Rouhani et al. 2023, "Microscaling Data Formats for Deep Learning",
  arXiv:2310.10537.
- Egiazarian et al. 2025, "MR-GPTQ for NVFP4/MXFP4 calibration",
  arXiv:2509.23202.
- NVIDIA developer blog 2025-06-24, NVFP4 announcement.
- Vasilev et al. 2026, "GoldenFloat: a phi-anchored numeric ladder",
  arXiv:2606.05017.
- Hunhold 2024, "A Hardware Codec for Takum Arithmetic",
  arXiv:2408.10594.
