# e00 — Forecast-collapse check

Do FinText Chronos_Small_2023_US and generic chronos-t5-small give informative next-day forecasts on 2024+
S&P 500 excess returns, or do their forecasts collapse (flat and uninformative)? Gate for all later interp work.
Full plan: pre-registration entry in `notes/research-log.md` (2026-10-23); decisions in `notes/decisions.md`.

## Hypotheses (logged before any forecast)
- H1: arm A (FinText, returns) is not collapsed; arm B (generic, returns) is collapsed or weaker.
- H2: arm C (generic, total-return index levels) is less collapsed than B: higher D and higher mean IC.
- Falsified: H1 if A is collapsed; H2 if C's D and IC are not both above B's. Stop if A and B both collapse.

## Arms
| Arm | Model @ revision | Input |
|---|---|---|
| A | FinText/Chronos_Small_2023_US @ f60a282f | daily excess returns, clipped [-1, 1] |
| B | amazon/chronos-t5-small @ a971ba21 | same as A |
| C | amazon/chronos-t5-small @ a971ba21 | total-return index normalised to 1; samples -> P̂/P_t - 1 - RF |

Contexts 512 (seeds 0, 1) and 252 (seed 0); 20 samples, model-config sampling defaults (temperature 1, top_k 50).

## Commands (from repo root, Python = `~/venvs/tsfm-interp/bin/python`)
```
python experiments/e00_collapse/fetch_data.py constituents | rf | prices
python experiments/e00_collapse/universe.py
python experiments/e00_collapse/build_panel.py
python experiments/e00_collapse/check_moves.py
python experiments/e00_collapse/model_checks.py
python experiments/e00_collapse/armC_resolution.py
python experiments/e00_collapse/run_forecasts.py --bench 1000
bash   experiments/e00_collapse/run_all.sh           # 9 runs, in tmux session e00; logs in cache/e00/logs/
python experiments/e00_collapse/analyze.py           # pre-registered metrics + verdicts
cd experiments/e00_collapse && python explore.py     # EXPLORATORY follow-ups (not pre-registered)
```

## Outputs
- `results/metrics.csv`, `results/summary.json`: pre-registered metrics and verdicts.
- `results/exploratory.json`: paired IC differences, raw-input baselines (not pre-registered).
- `figs/*.png` with sidecar JSON configs.
- Forecasts (git-ignored): `cache/e00/forecasts_{arm}_L{L}_s{seed}.parquet`.

## Result
See `notes/findings.md` (e00 entry) for verdicts, numbers and provenance.
