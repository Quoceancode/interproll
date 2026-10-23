# Status

_Overwrite this file at the end of each session. Keep it under one screen._

**Last updated:** 2026-10-23

## Where things stand
- WSL2 + venv `~/venvs/tsfm-interp` set up; 54GB RAM to WSL confirmed.
- torch 2.11.0+cu128 with CUDA working on the RTX 5070 Ti; nnsight 0.8.1, chronos-forecasting 2.3.2 installed.
- Dependencies audited and pinned in `requirements.txt` (certifi 2026.10.19, dateutil 2.9.0.post0; see decisions.md).
- Ask before installing or upgrading anything else.
- Novelty re-check done 2026-10-23 (see literature.md "Search log"): gap still open; nearest prior work is
  time2time (2509.05801). Claim narrowly.

## Blockers
- None.

## Next steps
1. e00: measure forecast variance / collapse for the generic Chronos and FinText Chronos-Small on the same
   post-training-cutoff returns. **If both collapse, stop and report** before any interpretability work.
2. e01: load a generic Chronos and a FinText Chronos with nnsight; cache encoder activations on ~50 tickers of daily returns.
