# v0.4.0 (2026-06-08)

## New packs (4)

- `vectors/bf16_conformance_v0.json` — 21 vectors, 21/21 match with `ml_dtypes.bfloat16` 0.5.4
- `vectors/fp8_e4m3_conformance_v0.json` — 16 vectors, 15/16 match with `ml_dtypes.float8_e4m3fn`. One documented interpretation gap on overflow saturation (tt-metal/AMD vs JAX/TPU convention).
- `vectors/fp8_e5m2_conformance_v0.json` — 17 vectors, 17/17 match with `ml_dtypes.float8_e5m2`
- `vectors/e8m0_block_conformance_v0.json` — 11 vectors, OCP MX v1.0 scale format, cross-validated against `ml_dtypes.float8_e8m0fnu`

## P3109 cross-walk

`docs/conformance/p3109_crosswalk.md` — full mapping between this suite and IEEE SA P3109 v3.2.0 Configured Formats (Binary8p3se, Binary8p4se, Binary4p{1,2,3}sf), plus P3109 StandardOperations.yaml category overview for the Q3 2026 operation-layer extension (Track 2).

## Manifest

`docs/conformance/MANIFEST_v0.4.0.json` lists all 6 packs (2 LIVE + 4 NEW) with per-pack self-SHA-256 fingerprints, ml_dtypes ground-truth validation, and documented divergences.

## Schema

`t27-conformance/v0.1` (unchanged). All new packs add an optional `validation` field and an optional `interpretation_gap` flag per vector.

## Anchor

All packs cite `phi^2 + 1/phi^2 = 3 = L_2` (GoldenFloat preprint arXiv:2606.05017) as a cross-pack sanity check.
