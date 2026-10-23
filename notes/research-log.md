# Research log

_Append-only. Newest at the bottom. One entry per session or experiment._

Template:
```
## YYYY-MM-DD — <short title>
Hypothesis: ...
Would be falsified by: ...
Ran: <command / notebook / commit>
Result: ...
Interpretation (Chase): ...
Next: ...
```

## 2026-10-23 — Project start
Hypothesis: n/a (setup).
Ran: environment setup in WSL; venv created; torch cu128 installed.
Result: RAM cap working (54Gi). NumPy warning on torch import -> install numpy.
Next: CUDA check, novelty re-check, e01 activation caching.

## 2026-10-23 — CUDA check, dependency audit, requirements pinned
Hypothesis: n/a (setup).
Ran:
- 12:22 — Chase's manual `pip install nnsight chronos-forecasting` (pulled in transformers 5.20.2,
  huggingface_hub 2.3.0, httpx2/httpcore2 2.16.0, certifi 2026.10.23, python-dateutil 3.0.0, etc.).
- Audit of the freeze: certifi dated same day; httpx2/httpcore2 looked like lookalikes; dateutil 3.0.0 unrecognised.
  Chase verified online: httpx2/httpcore2 genuine (Pydantic); dateutil 3.0.0 unverified.
- Startup hooks: only `_cuda_bindings_redirector.pth` (owned by cuda-bindings 12.9.7) and
  `distutils-precedence.pth` (setuptools 78.1.0); no sitecustomize/usercustomize. Both are benign.
- pip already 26.2.2 (no upgrade needed).
- `pip install --no-deps certifi==2026.10.19 python-dateutil==2.9.0.post0`; `pip check` clean.
- CUDA check (before and after): torch 2.11.0+cu128, CUDA 12.8, `cuda.is_available()` True, RTX 5070 Ti,
  capability (12, 0), GPU matmul finite.
- `pip freeze` -> requirements.txt (73 pins + PyTorch cu128 extra index).
Result: environment works on GPU; dependencies pinned. See decisions.md for certifi/dateutil choices.
Next: novelty re-check, then e01.
