# P3109 v3.2.0 Cross-Walk

Mapping between this conformance suite and IEEE SA P3109 Working Group draft v3.2.0
([P3109/Public Interim Report](https://github.com/P3109/Public/blob/main/IEEE%20WG%20P3109%20Interim%20Report%20v3.2.1.pdf)).

## P3109 v3.2.0 Configured Formats

| P3109 Name | Bits | Exp | Mant | Saturation | Our Equivalent | Pack |
|---|---|---|---|---|---|---|
| Binary8p3se | 8 | 4 | 3 | OvfInf | FP8_E4M3 (close match, finite-only differs) | `fp8_e4m3_conformance_v0.json` |
| Binary8p4se | 8 | 3 | 4 | OvfInf | FP8_E3M4 (not yet generated, ml_dtypes has it) | `(future addition - ml_dtypes.float8_e3m4 reference)` |
| Binary4p1sf | 4 | 2 | 1 | SatFinite | MXFP4 element (S1E2M1 inside MX block) | `mxfp4_conformance_v0.json` |
| Binary4p2sf | 4 | 1 | 2 | SatFinite | no direct match | `(future addition)` |
| Binary4p3sf | 4 | 0 | 3 | SatFinite | no direct match | `(future addition)` |

## Our Formats and P3109 Coverage

| Our Format | P3109 Status |
|---|---|
| GF16 | GoldenFloat 16-bit, phi-anchored, S1E5M10 with phi-rotation - no P3109 equivalent |
| BF16 | S1E8M7 bias=127 - too wide for P3109 (P3109 focuses on 4/8-bit) |
| FP8_E4M3 | Maps to P3109 Binary8p3se with NaN/OvfInf differences |
| FP8_E5M2 | No direct P3109 v3.2.0 match (Binary8p2se would correspond but not in current Profiles) |
| MXFP4 | Block format with 32-element groups; element is P3109 Binary4p1sf |
| E8M0_BLOCK | OCP MX scale format; orthogonal to P3109 representation layer |

## Operational Conformance (P3109 StandardOperations.yaml)

P3109 defines ~80 operations across 7 categories:

- **Classification** (8): IsZero, IsOne, IsNan, IsSignMinus, IsFinite, IsInfinite, IsNormal, IsSubnormal
- **Comparison** (7): CompareLess..CompareGreater, TotalOrder
- **Extrema** (10+): Minimum, Maximum, Clamp, MinimumMagnitude, ...
- **Projection rounding** (6): NearestTiesToEven, NearestTiesToAway, ToOdd, TowardNegative, TowardPositive, TowardZero, plus 3 Stochastic modes
- **Math arithmetic** (10): Negate, Abs, Recip, Sqrt, Add, Subtract, Multiply, Divide, FMA, FAA
- **Math transcendental** (~25): Exp, Log, Sin, Cos, Tan, ArcSin, ArcCos, Sinh, Cosh, Tanh, ...
- **Block** (40+): BlockAdd, BlockFMA, BlockReduceAdd, BlockDotProduct, BlockExp, ...

**Current coverage of this suite v0.1:** representation-layer only (encode/decode bit-exactness).
**Track 2 (Q3 2026)** will extend to operation-layer conformance vectors,
covering at minimum NearestTiesToEven rounding for Add/Multiply/FMA across all 6 formats.

## Anchor

All our packs cite the identity `phi^2 + 1/phi^2 = 3 = L_2` (GoldenFloat preprint
[arXiv:2606.05017](https://arxiv.org/abs/2606.05017)) as a single-line cross-pack
sanity check. In each pack, the vector named `anchor_*` encodes 3.0 (exact in all
binary formats with sufficient exponent range) and verifies decode == 3.0.

## Reference

- IEEE SA P3109 WG: https://sagroups.ieee.org/p3109wgpublic/
- P3109/Public: https://github.com/P3109/Public
- Open Compute Project Microscaling spec: https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf
- ml_dtypes (Google/JAX) ground-truth library: https://github.com/jax-ml/ml_dtypes