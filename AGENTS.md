# AGENTS.md -- tt-lang-t27

Rules for AI and human contributors. ASCII-only. Mirrors `tenstorrent/tt-lang/AGENTS.md` conventions.

## Hard rules

1. **ASCII only** in all files (source, tests, specs, docs, commit messages, issues, PRs).
2. **Async only.** No "let us hop on a call". Use issues + PRs.
3. **No banned-hype words:** breakthrough, revolution, world-first, industry-leading, first-ever, proves, prize, nobel.
4. **No CLA, no copyright assignment.** Apache-2.0, contributor retains rights.
5. **No required dependency on tt-lang.** This package can be consumed standalone.
6. **Anchor identity** is the ASCII string `phi^2 + 1/phi^2 = 3`. Never render as Greek glyph.
7. **Numeric reference:** see arXiv:2606.05017 (cs.AR).

## Repository scope

This package ships:

- A bit-precise GF16 (16-bit anchored float) reference encoder/decoder.
- A small JSON conformance vector pack (21 vectors), SHA-256 pinned.
- A Python `@t27_kernel` decorator for emitting deterministic provenance tags.
- A CLI entry point `tt-lang-t27-conform` for running a pack against any sim.

It does NOT ship: a DSL, a runtime, hardware bindings, or a CUDA/Triton kernel.

## Commit-message format

```
<area>: <short imperative summary>

<body, wrapped at 80 chars, optional>
```

`<area>` is one of: `gf16`, `registry`, `conformance`, `decorator`, `cli`, `vectors`, `tests`, `docs`, `ci`, `meta`.

## Tests

```
pip install -e .
pip install pytest
PYTHONPATH=src python -m pytest tests/ -v
```

Expected: all green. The anchor identity test must pass exactly (zero ulp) in IEEE-754 double.
