# interproll — Mechanistic interpretability of finance-pretrained time series foundation models

## Start of every session
1. Read `notes/STATUS.md` (where things stand, what's next).
2. Skim the latest entries in `notes/research-log.md`.
3. Check `notes/decisions.md` before changing setup, data, or method.
Do not re-derive context that is already written down in `notes/`.

## End of every session (or when asked to "wrap up")
1. Update `notes/STATUS.md` (current state, blockers, next 1–3 steps).
2. Append a dated entry to `notes/research-log.md`.
3. Record any choice of method/data/hyperparameter in `notes/decisions.md` with the reason.
4. Move any confirmed result into `notes/findings.md` with the exact command, config, and commit that produced it.

## Research question
What does finance pretraining add, mechanistically? Off-the-shelf TSFMs (e.g. Chronos) forecast
stock returns poorly; the same architecture pretrained from scratch on financial returns (FinText
models, Rahimikia et al.) does much better. Find the internal features responsible, and test whether
they correspond to known finance factors (momentum, short-term reversal, volatility clustering,
drawdown) or to something else.

Prior work (see `notes/literature.md`): SAEs and probes have been applied to generic TSFMs on
generic/synthetic data. As far as Chase's search found, nobody has interpreted a finance-pretrained
TSFM or compared it mechanistically with its generic counterpart. Re-check before claiming novelty.

## Owner
Chase (flipbit). Chase designs the experiments and interprets results. Claude implements, runs, and
reports. When a result is ambiguous, report it as ambiguous; do not round up.

## Environment
- WSL2 Ubuntu, Python 3.12, venv at `~/venvs/tsfm-interp`.
- Run Python as `~/venvs/tsfm-interp/bin/python`, install with `~/venvs/tsfm-interp/bin/pip`. Never install globally.
- GPU: RTX 5070 Ti 16GB (Blackwell; needs a CUDA 12.8+ PyTorch build). CPU: Ryzen 9 9950X. RAM: 54GB to WSL.
- Keep data, caches, and checkpoints under `~/` (WSL filesystem), never `/mnt/c/`.

## Package and security rules
- Ask before installing any new package. Name it, its source, and why.
- Pin exact versions in `requirements.txt` once something works. Do not upgrade without asking.
- Avoid releases less than a few days old (supply-chain attacks, Oct 2026). Never install `litellm`.
- Copy package names from official docs only; watch for lookalike names.
- No API keys, cloud credentials, or SSH keys in this project; it doesn't need them.

## Tooling
- Activations / interventions: nnsight (preferred) or plain PyTorch forward hooks; pyvene for causal interventions.
- SAEs: dictionary_learning (Sam Marks) or a small hand-written TopK SAE.
- Not TransformerLens: Chronos uses a custom value tokenizer and T5 support there is experimental.
- Data: free daily OHLCV (yfinance / Stooq) cached locally as parquet in `data/raw/`; never re-download in a loop.

## Research hygiene (non-negotiable)
- Write the hypothesis and the result that would falsify it in the log BEFORE running an experiment.
- Time-based splits only. No random shuffles across time. Watch for look-ahead leakage in every feature.
- Every probe result needs baselines: (a) the same probe on raw input features (e.g. the last N returns),
  (b) a randomly initialized model of the same architecture, (c) the generic (non-finance) checkpoint.
  A probe that decodes momentum from activations means little if it decodes it equally well from raw inputs.
- Causal claims need interventions (ablation / steering), not just correlations.
- Report effect sizes with confidence intervals across seeds and time periods; correct for multiple comparisons.
- Negative results go in `findings.md` too.

## Layout
```
CLAUDE.md          this file
notes/             persistent memory across sessions (markdown, committed to git)
  STATUS.md        current state + next steps (overwrite each session)
  research-log.md  dated append-only log: hypothesis -> run -> result
  decisions.md     choices and why
  findings.md      confirmed results with provenance
  literature.md    papers, what they did, what's left open
  questions.md     research questions, ranked
src/               reusable code (loading, caching, probes, SAEs)
experiments/       one folder or notebook per experiment, numbered (e01_, e02_ ...)
data/              raw/ and processed/ (git-ignored)
cache/             activation caches (git-ignored, large)
```

## Style
- Small, readable functions; type hints; no clever one-liners Chase can't explain.
- Explain non-obvious code briefly in comments. Chase must be able to defend every line.
- Plots saved to `experiments/<id>/figs/` with the config in the filename or a sidecar JSON.
