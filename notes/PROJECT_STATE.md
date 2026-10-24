# Project state — interproll

_The one document to read to understand the whole project. Last updated 2026-10-23. Short-term status lives in
`STATUS.md`; detail lives in the files linked below._

## Working rule
**Chase's interpretation is authoritative.** Claude implements and reports; it doesn't decide what results mean.
Every experiment's results use three files (CLAUDE.md, "Results convention"):
- `RESULTS_FACTS.md`: facts only.
- `RESULTS_AGENT_INTERPRETATION.md`: AI-written, frozen once Chase starts.
- `RESULTS_CHASE.md`: Chase's own.

## Research question
What does finance pretraining add, mechanistically? FinText's Chronos models (Rahimikia et al.) have the same
architecture as generic Chronos-T5 but are pretrained from scratch on financial returns. Find the internal
features responsible for any difference, and test whether they correspond to known finance factors (momentum,
short-term reversal, volatility clustering, drawdown) or to something else.

**Narrowed claim** (after the 2026-10-23 novelty re-check): *first mechanistic comparison of finance-pretrained vs
generic TSFMs, mapping features to finance factors; builds on time2time (arXiv 2509.05801)*. time2time intervenes on
generic Chronos/Toto hidden states with equity crash regimes. It is the nearest prior work and must be cited.

## What has been done

### Setup and security (detail: [decisions.md](decisions.md))
- **Environment:**
  - WSL2 Ubuntu, venv `~/venvs/tsfm-interp`, torch 2.11.0+cu128 on an RTX 5070 Ti.
  - nnsight 0.8.1, chronos-forecasting 2.3.2.
  - All packages pinned in `requirements.txt`.
- **Supply-chain audit of the initial install:**
  - certifi pinned at 2026.10.19 (eMudhra fix).
  - python-dateutil held at 2.9.0.post0 (3.0.0 unverified).
  - httpx2/httpcore2 verified genuine.
  - pillow 13.0.0 taken as a deliberate security exception, provenance checked via PyPI attestations.
  - New packages are installed only from reviewed dry-run hashes (`--require-hashes --no-deps`).
- **Permission guard** (`.claude/settings.json` + `.claude/hooks/ask_guard.sh`): always asks for pip
  install/uninstall, sudo, git push, deletes outside `cache/`/`data/`, and downloads piped to a shell.
  Known gap: commands inside Python scripts are invisible to it.
- **Model loading** (`src/models.py`): safetensors only, approved repo ids, pinned 40-char SHAs, no
  `trust_remote_code`, post-download file allowlist.

### Novelty searches (detail: [literature.md](literature.md))
- **Before the project:** Chase's own search. No interpretation of finance-pretrained TSFMs found.
- **2026-10-23 re-check (Claude):**
  - Sources: arXiv API, author queries (Rahimikia / Ni / Wang), Google Scholar (CAPTCHA-limited), Semantic Scholar
    citations of 2511.18578, SSRN via web search.
  - **Gap still open.** No work interprets a finance-pretrained TSFM, maps TSFM features to finance factors, or
    compares finance vs generic checkpoints mechanistically.
  - **Remaining coverage holes:** up to 8 Scholar-citing papers unread; most hits judged from abstracts; SSRN
    search shallow.
  - Re-check before any write-up.

### e00 — forecast-collapse check (done; facts: [RESULTS_FACTS.md](../experiments/e00_collapse/results/RESULTS_FACTS.md))
- **Design:** S&P 500 as of 2023-12-31 (474 usable stocks); next-day excess returns, 2024-01-02 .. 2026-08-31.
  - Arm A: FinText Chronos_Small_2023_US on returns.
  - Arm B: generic chronos-t5-small on returns.
  - Arm C: generic chronos-t5-small on a total-return index.
  - Contexts 512 (2 seeds) and 252; 20 samples. Pre-registered collapse rule, hypotheses H1/H2 and stop condition.
- **Factual outcome:**
  - No arm collapsed under the pre-registered rule; the stop condition was not triggered.
  - Mean daily IC: A 0.023 [0.015, 0.029] (Holm-significant); B 0.007 [−0.000, 0.014] (not significant);
    C ≈ 0.
  - H2 falsified.
  - Exploratory checks (paired IC differences, factor baselines, calibration) are in the facts file §4.
  - **Exploratory top_k sensitivity** (A and B, L512 s0, top_k off instead of the default 50):
    - 80% interval coverage 0.72–0.73 (default 0.14).
    - A IC 0.0038 [−0.0003, 0.0071]; B IC 0.0025 [−0.0015, 0.0062].
    - A−B 0.0013 [−0.0032, 0.0051].
    - See the facts file, last section.
- Chase's interpretation: pending (`RESULTS_CHASE.md`).

## Changes from the original plan
1. **e00 added before e01.** The original first step was e01 (activation caching). A collapse check was put first,
   because if neither model forecasts anything there is nothing to explain.
2. **Arm C added** as a confound control: generic Chronos was trained on levels, never returns, so it is also fed
   a levels representation of the same information.
3. **Full daily evaluation** for all 9 runs, instead of the pre-specified every-5th-day fallback. Fixed by Chase
   before any results.
4. **e01's first target is now A's reversal vs B's extrapolation** (forecast vs −r_t: +0.21 vs −0.21), preceded by
   a factor-regression pre-step. See [questions.md](questions.md).

## Where Chase is
Pausing experiments to build foundations, then interpreting e00 himself before e01. e01 is on hold.

## Roadmap (at 10–15 hrs/week)

| Phase | Duration | Content | Who |
|---|---|---|---|
| 1. Foundations | 4–8 weeks | ARENA fundamentals; transformer from scratch by hand; train a toy SAE | Chase |
| 2. Own e00 | 1–2 weeks | Fill in `RESULTS_CHASE.md`, then compare with the agent interpretation | Chase |
| 3. e01 probes and interventions | 4–6 weeks | Factor-regression pre-step; reversal vs extrapolation via ablation / activation patching; probes with all three baselines | Chase writes probe code; Claude handles plumbing |
| 4. SAEs and causal tests | 6–10 weeks | SAE dictionaries for both models; feature comparison; causal tests of factor features | Chase + Claude |
| 5. Write-up | 3–4 weeks | Paper or report with outside review; novelty re-check | Chase |

**Milestone:** a defensible first result after phases 1–3 (about 3 months). Full project: 5–7 months.

## Open tasks carried forward
- Research the 20 Yahoo 404s and 5 truncated tickers with cited sources before e01 (see STATUS.md).
- Unexplained FinText constant-input behaviour (questions.md, future interp question).
