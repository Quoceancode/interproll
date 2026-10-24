# Status

_Overwrite this file at the end of each session. Keep it under one screen._

**Last updated:** 2026-10-23 (evening)

## Where things stand
- Environment: WSL2 + venv `~/venvs/tsfm-interp`; torch 2.11.0+cu128 on the RTX 5070 Ti; dependencies pinned
  (requirements.txt). Permission guard live (`.claude/`). Ask before installing or upgrading anything.
- Novelty re-check done 2026-10-23; nearest prior work is time2time (2509.05801). Claim narrowly.
- **e00 complete** (findings.md F1; commit 538df76):
  - No arm collapsed. Stop condition not triggered.
  - **FinText (A):** IC about 0.02, significant in every year, seed and context.
  - **Generic on returns (B):** IC 0.007, not significant. Dispersed but uninformative.
  - **Generic on levels (C):** IC about 0. H2 falsified.
  - **Exploratory:** A is about level with 12-1 momentum. FinText reverses the last return; generic extrapolates it.
  - **Exploratory:** model spreads are no better than trailing volatility.
- Unexplained: A/B predictive intervals far too narrow (80% interval covers about 14%). Candidate: top_k=50.

## Blockers
- **Waiting for Chase's review of e00** (per the "neither collapsed -> report and wait" rule).

## Decisions for Chase
1. Proceed to e01 on the A−B IC gap (0.015 [0.008, 0.023])? The rule has no "dispersed but uninformative" class.
2. Rerun A/B with top_k disabled to test the narrow-interval explanation? About 2 GPU-hours for L512 s0.
3. Should e01 target the reversal-vs-extrapolation difference (forecast vs -r_t: +0.21 vs -0.21) first?

## Tasks before e01
- Research the 20 Yahoo 404s and 5 truncated tickers (AVB, EA, EQR, QRVO, WBD) with cited sources; map confirmed
  same-security renames in `experiments/e00_collapse/ticker_map.csv` (candidates, unverified: CDAY->DAY,
  FLT->CPAY, PEAK->DOC; BK, MMC, FI, CTRA unexplained). See data/raw/e00/missing_tickers.csv.

## Next steps (after review)
1. e01: load both models with nnsight; cache encoder activations on e00 contexts (subset of tickers/days).
2. Probes for reversal / momentum / volatility with all three baselines (raw inputs, random init, generic).
