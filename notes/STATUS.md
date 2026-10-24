# Status

_Overwrite this file at the end of each session. Keep it under one screen. For the full picture read
[PROJECT_STATE.md](PROJECT_STATE.md) first._

**Last updated:** 2026-10-23

## Current state
- e00 done. Results in `experiments/e00_collapse/results/` (facts, agent interpretation, Chase template).
  Verdicts: no arm collapsed; A IC 0.023 (significant), B 0.007 (not), C ≈ 0; H2 falsified.
- Exploratory top_k-off rerun (A, B; L512 s0): intervals near nominal coverage; A IC 0.004, B 0.003, A−B 0.001
  (CI includes 0). Facts in RESULTS_FACTS.md, last section. Open: whether to run an exact-logit (no sampling)
  forecast before e01 (agent interpretation, appended section).
- Chase is pausing experiments to build foundations (roadmap phase 1).

## Blockers
- e01 on hold pending Chase's foundations work and his own e00 interpretation (`RESULTS_CHASE.md`).

## Next steps
1. Chase: foundations (ARENA, transformer from scratch, toy SAE), then fill in `RESULTS_CHASE.md`.
2. Before e01: research the 20 Yahoo 404s and 5 truncated tickers (AVB, EA, EQR, QRVO, WBD) with cited sources;
   map confirmed same-security renames in `experiments/e00_collapse/ticker_map.csv` (candidates, unverified:
   CDAY->DAY, FLT->CPAY, PEAK->DOC; BK, MMC, FI, CTRA unexplained). See data/raw/e00/missing_tickers.csv.
3. e01 (when resumed): factor-regression pre-step, then reversal vs extrapolation (questions.md).
