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

## 2026-10-23 — e00 step 4: models, sanity checks, arm C resolution, bench (no eval forecasts yet)
Ran: `model_checks.py`, `armC_resolution.py`, `run_forecasts.py --bench 1000`; tests/test_models.py (7 ok).
Result:
- Both snapshots = config.json, generation_config.json, model.safetensors only. Configs equal field by field.
- Constant input (0.001 x 512): generic returns 0.000997; FinText forecasts the LOWEST bin (median -0.015).
  On realistic inputs (64 real 2023 S&P contexts, pre-eval; 64 synthetic t4 returns) FinText is sane: 0 samples
  at the lowest bin, median forecasts ~0. Interpretation: constant returns are out of distribution for a
  returns-only model; not evidence of a preprocessing mismatch. Unexplained, noted.
- Arm C round trip on synthetic random walks: implied-return std 0.0155 vs true 0.015.
- Arm C resolution (L=512): step = median 0.66% of price (5–95%: 0.48–1.02%) vs median |R| 0.96%; per stock,
  step / median move = 0.72 (0.41–0.96); 37% of next-day moves smaller than one bin, 20% smaller than half.
  Arms A/B step: median 0.009%; 0.6% of moves smaller than one bin. L=252 similar (38% / 0.6%).
  -> Arm C can barely express typical daily moves; its Ties may be high for tokenizer reasons (pre-registered
  "inconclusive (tokenizer resolution)" rule applies).
- Bench (batch 32): 165 series/s at L=512, 333 at L=252; all 9 runs est. 238.6 min.
Next: Chase approves -> full forecast runs.

## 2026-10-23 — e00 step 5: full forecast runs and pre-registered analysis
Ran: `run_all.sh` in tmux session e00 (16:44–20:44, about 4.0 h; 9/9 runs exit 0, full daily evaluation).
Then `analyze.py`, then `explore.py` (exploratory, written after seeing the results).
Result (details and provenance in findings.md F1):
- **Verdicts:** no arm collapsed, at either context or seed. Stop condition: "neither A nor B collapsed -> report and
  wait".
- **Arm A (FinText):** IC 0.023 [0.015, 0.029], D 0.065, Holm-significant. Every year 2024/25/26 is about 0.02 with
  a CI above 0.
- **Arm B (generic, returns):** IC 0.007 [-0.000, 0.014], D 0.105. Not significant after Holm.
- **Arm C (generic, levels):** IC -0.000 [-0.005, 0.005], D 0.30.
- B and C escape the collapse rule through dispersion, not information. The pre-registered rule was built for
  "flat AND uninformative" and has no category for "dispersed but uninformative". Reported as-is, not reclassified.
- **H1:** supported in its "weaker" form (A > B, paired diff 0.015 [0.008, 0.023]).
- **H2:** falsified (C is more dispersed, with no IC).
- **Exploratory baselines:**
  - A is about level with 12-1 momentum (0.027) and above 1-day reversal (0.015).
  - Trailing 21-day vol (0.220) beats all model spreads (0.19–0.20) at predicting |r|.
  - Forecasts correlate with -r_t at +0.21 (A) vs -0.21 (B): FinText reverses, generic extrapolates.
- **Surprise:** A and B 80% intervals cover only about 14%. Candidate cause: the top_k=50 sampling default.
  Unconfirmed.
Next: Chase reviews. Open choices: whether e01 proceeds on the IC gap; whether to rerun A/B with top_k disabled.

## 2026-10-23 — Records restructure + e00 top_k sensitivity (exploratory)
- **Records:**
  - Results convention added to CLAUDE.md.
  - e00 results split into RESULTS_FACTS / RESULTS_AGENT_INTERPRETATION / RESULTS_CHASE.
  - New notes/PROJECT_STATE.md with the roadmap.
  - e01 recorded and on hold (questions.md).
  - Pre-registration lessons added to decisions.md.
  - Chase is pausing experiments for foundations work.
- **Hypothesis (exploratory, stated before the run):** top_k = 50 causes the narrow A/B intervals. Falsified if
  coverage stays far below nominal with top_k off.
- **Ran:** `bash experiments/e00_collapse/run_topk.sh` (A and B, L512 s0, top_k = 4096), code 2de0de7.
- **Result:**
  - 80% coverage 0.722 (A) / 0.727 (B), up from 0.146 / 0.135.
  - IC A 0.0038 [−0.0003, 0.0071], B 0.0025 [−0.0015, 0.0062]; A−B 0.0013 [−0.0032, 0.0051].
  - A top_k off − A default: −0.0188 [−0.0251, −0.0122].
  - Facts: e00 RESULTS_FACTS.md, last section.
- **Next:** Chase's foundations work. Open choice: an exact-logit forecast check before e01.

## 2026-10-23 — e00 exact-distribution forecasts (exploratory, requested by Chase)
- **Question:** is the top_k-off IC drop sampling noise, or does truncation create the signal?
- **Ran:**
  - `exact_forecasts.py --check`: exact means vs 4,000-sample means on 64 contexts; z-scores consistent with
    noise; max |z| 3.17.
  - `bash experiments/e00_collapse/run_exact.sh` (1d46def): A and B, L512, first-step distribution, no sampling.
- **Result (mean daily IC):**
  - A: full mean 0.0167 [0.0097, 0.0228]; full median 0.0241; top50 mean 0.0254; mode 0.0053 [−0.0005, 0.0118].
  - B: 0.0015–0.0080.
  - A−B: full mean 0.0117 [−0.0010, 0.0227]; full median 0.0169 [0.0060, 0.0266];
    top50 mean 0.0175 [0.0097, 0.0254].
  - Facts: e00 RESULTS_FACTS.md, last section.
- **Next:** unchanged (Chase's foundations; e01 on hold).
