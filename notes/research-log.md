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

## 2026-10-23 — e00 forecast-collapse check: pre-registration (written before any forecast)
Plan: experiments/e00_collapse/ (README + config.json once written). Arms: A = FinText/Chronos_Small_2023_US on
excess returns; B = amazon/chronos-t5-small on excess returns; C = amazon/chronos-t5-small on a total-return
index (same information as B, levels representation). S&P 500 as of 2023-12-31, next-day targets from 2024-01-02,
context 512 (robustness 252), 20 samples, seeds {0,1} at 512.
Hypothesis:
- H1: arm A is not collapsed; arm B is collapsed or weaker than A.
- H2: arm C is less collapsed than arm B (higher D and higher mean IC).
Collapse (per arm x {sample mean, sample median} x L): (D < 0.05 AND mean daily rank-IC 95% block-bootstrap CI
includes 0) OR Ties > 0.5. D = median over days of cross-sectional std(forecast)/std(realised). Arm collapsed =
point collapse under both mean and median at L=512 (seeds must agree, else ambiguous). Spread collapse:
S < 0.1 OR spread-vs-|r| CI includes 0. Arm C collapsing only via Ties -> "inconclusive (tokenizer resolution)".
Would be falsified by: H1 — arm A collapsed. H2 — C's D and IC not above B's.
Stop: A and B both collapsed at L=512 -> stop, report, no e01. Every other outcome (incl. neither collapsing)
-> report and wait for Chase. Every verdict reported with its mean IC + CI (daily ICs ~0.01–0.03 are typically
meaningful).
Ran: nothing yet.

## 2026-10-23 — e00 step 3: data (no models, no forecasts)
Ran: `experiments/e00_collapse/fetch_data.py {constituents,rf,prices}`, `universe.py`, `build_panel.py`.
Result:
- Universe: fja05680 (commit a2430f2a, row 2023-12-18) and Wikipedia rev 1192789360 agree exactly: 503 = 503
  (after fixing my parser for `{{BZX link|CBOE}}`). Minus GOOG/FOX/NWS -> 500. Not independent sources
  (fja uses Wikipedia changes since 2019).
- Yahoo: 20 HTTP 404; 5 truncated stubs (AVB, EA, EQR, QRVO, WBD: firstTradeDate 2026-07-17, 1–62 days;
  same on one retry); PARA symbol now Banzai International (history is Banzai's) -> excluded.
  474/500 usable (26 = 5.2% missing). Some 404s are likely renames (unverified), see STATUS.
- Panel: 2024-01-02..2026-08-31 (RF ends 2026-08-31), 668 days x 474 stocks = 316,632 stock-days, no missing
  RF days. Median |exret| 0.0099, std 0.0205; 1 clip (MRNA 2026-08-19 +177%, level persists: unverified).
  Spot checks: NVDA 2025-01-27 -16.97% (known ~-17%); GL 2024-04-11 -53% (known short-report drop).
Next: Chase reviews missing tickers / renames; then models (step 4).
