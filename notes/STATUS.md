# Status

_Overwrite this file at the end of each session. Keep it under one screen._

**Last updated:** 2026-10-23

## Where things stand
- WSL2 + venv `~/venvs/tsfm-interp` set up; 54GB RAM to WSL confirmed.
- PyTorch installed (cu128). NumPy needed installing; CUDA check pending.

## Blockers
- None yet.

## Next steps
1. Confirm `torch.cuda.is_available()` and pin `requirements.txt`.
2. Re-check novelty: arXiv q-fin + recent work by Rahimikia / Ni / Wang (FinText).
3. e01: load a generic Chronos and a FinText Chronos with nnsight; cache encoder activations on ~50 tickers of daily returns.
