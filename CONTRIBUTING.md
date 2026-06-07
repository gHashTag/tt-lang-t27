# Contributing to tt-lang-t27

Thanks for considering a contribution. This project is Apache-2.0 and
contributor-friendly: no CLA, no copyright assignment.

## Quick start

```
git clone https://github.com/gHashTag/tt-lang-t27
cd tt-lang-t27
pip install -e .
pip install pytest
PYTHONPATH=src python -m pytest tests/ -v
```

All tests must pass before opening a PR. The anchor identity test
(`test_anchor_identity_ieee754_exact`) must pass with zero ulp distance.

## Code style

- ASCII only (per `AGENTS.md`).
- Python stdlib only for `src/` (no runtime dependencies).
- Tests may use `pytest`.
- Type hints encouraged.
- Keep modules small and single-purpose.

## Pull requests

- One topic per PR.
- Include tests for new behavior.
- Update `README.md` if the public surface changes.
- Commit message format: see `AGENTS.md`.

## Issues

Open issues for bugs, schema questions, or vector-pack proposals. Async
discussion only. No call/Zoom/sync offers.

## Vector packs

New conformance vector packs follow the JSON shape in
`vectors/gf16_conformance_v0.json`. Pin the pack with a SHA-256 in the
README. Do not modify existing pinned packs in-place; bump to v1, v2, etc.
