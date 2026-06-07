# tt-lang-t27

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![arXiv:2606.05017](https://img.shields.io/badge/arXiv-2606.05017-b31b1b.svg)](https://arxiv.org/abs/2606.05017)

Open numeric-format SSOT bridge from [gHashTag/t27](https://github.com/gHashTag/t27)
(GoldenFloat family, Apache-2.0, Tiny Tapeout silicon) into
[tenstorrent/tt-lang](https://github.com/tenstorrent/tt-lang) kernel author workflows.

## What this is

A pure-Python side-package -- **zero coupling with tt-lang upstream**.
Reads the t27 `FORMAT-SPEC-001.json` registry, validates kernel functions
against bit-precise conformance vectors, and (optionally) hands off to a
Coq formal oracle.

## What this is NOT

- Not a fork of tt-lang.
- Not a patch to tt-lang.
- Not a build-time dependency of tt-lang.
- Not a CLA / copyright crossing.

Both repos remain Apache-2.0, separately governed.

## Install

```bash
pip install tt-lang-t27       # from PyPI (planned)
# or
pip install git+https://github.com/gHashTag/tt-lang-t27
```

No Coq / no MLIR / no ttnn dependencies.

## Quickstart

```python
from tt_lang_t27 import t27_kernel, load_registry, load_vectors

@t27_kernel(
    fmt="GF16",
    registry_path="format-spec-001.json",
    vectors_path="gf16_conformance_v0.json",
)
def my_matmul(a, b):
    return a @ b
```

Every call logs a deterministic provenance tag:

```
[t27] kernel=my_matmul fmt=GF16 ssot=d9b76c5 tag=0a5ecb845def
[t27]   vector-check n=21 fmt=GF16
```

## CLI

```bash
tt-lang-t27-conform \
  --registry format-spec-001.json \
  --vectors  gf16_conformance_v0.json \
  --kernel   path/to/user_kernel.py::my_matmul
# OK conform=true reasons=0 sha256=<hex>
```

## Provenance tag formula

```
sha256(kernel_name || ssot_commit || fmt || anchor_hash)
```

`anchor_hash = SHA-256("phi^2 + 1/phi^2 = 3")`.

## References

- [arXiv:2606.05017 -- GoldenFloat](https://arxiv.org/abs/2606.05017)
- [t27 FORMAT_REGISTRY.md](https://github.com/gHashTag/t27/blob/master/FORMAT_REGISTRY.md)
- [t27 FORMAT-SPEC-001.json](https://github.com/gHashTag/t27/blob/master/conformance/FORMAT-SPEC-001.json)
- [tenstorrent/tt-lang](https://github.com/tenstorrent/tt-lang)

## Anchor

phi^2 + 1/phi^2 = 3 = L_2 (Lucas number).
