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

## Own language first

When this project publishes something about itself, it publishes in **this
project's own language and format** -- not translated into somebody else's.

Owner's rule, 2026-09-20: stop writing in other people's languages, we have our
own.

This bites on any file whose only reason to exist is that an outside tool
expects that shape: `llms.txt`, `agents.json`, `ai.txt`, `.well-known/*.json`,
A2A agent cards, `ai-plugin` manifests, OpenAPI stubs, JSON-LD blocks, a README
that restates a spec. The reflex is to write four of them in four foreign
formats, and the reflex is wrong: a project whose claim is "here is a language
worth writing" and which then describes itself in three of other people's
formats has published three documents that are not true of it.

**The move:** find the address the outside world already fetches, then serve our
own language at it. `/llms.txt` at t27.ai **is** a t27 module -- `llms.txt`
requires nothing but text, and every prose line of a `.t27` file is a `;`
comment, so it stays readable to anything that cannot compile it.

**Three qualifications, so the rule stays honest:**

- A format a resolver genuinely parses -- a sitemap, `package.json`, a lockfile
  -- is machinery, not a description. **Generate** it from our own source; never
  hand-write it into a second home for the truth.
- Code against someone else's API uses their types. Prose for a human who has
  never heard of the project uses that human's language.
- If a format demands a claim we cannot back, **publish nothing**. An A2A card
  with no A2A server behind it is a false claim, and a missing file is more
  honest than a lying one.

The test: *is this file the project speaking about itself?* If yes, it speaks
our language. If it is plumbing, it speaks the plumbing's.

**Worked example, compiler-checked rather than asserted:** in `gHashTag/trinity`,
`apps/website/public/t27/files/specs/catalog/onboarding.t27` generates
`/llms.txt` and `/agents.t27` byte-identically, gated in CI as
`check:onboarding`. The generator evaluates the spec's own `test` blocks --
`typecheck.ok` stays true for `assert 1 > 2`, so a compiler saying "this parses"
is not a compiler saying "this is true" -- and re-compiles the rendered document
before writing it.

**The full rule lives in exactly one place: the `own-language-first` skill**
(`~/.claude/skills/own-language-first/SKILL.md`). It carries the consent gate for
documents addressed to other people's agents, the six negative controls, and the
`;`-alone-on-a-line trap that silently discards a `module` declaration. This
section is a pointer, not a copy -- the recorded defect in this codebase family
is the hand-copied rule that only two of its three homes knew about.
