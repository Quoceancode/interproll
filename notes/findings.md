# Findings

_Only confirmed results. Each entry: factual verdicts plus a link to the experiment's `RESULTS_FACTS.md` (numbers,
definitions, provenance). Interpretation lives in the experiment's results folder, not here. Include negative results._

## F1 (2026-10-23) — e00 forecast-collapse check
Facts: [`experiments/e00_collapse/results/RESULTS_FACTS.md`](../experiments/e00_collapse/results/RESULTS_FACTS.md)

- **Pre-registered verdicts at L512** (seeds 0 and 1 agree; L252 agrees):
  - A (FinText, returns): not collapsed.
  - B (generic, returns): not collapsed.
  - C (generic, levels): not collapsed.
- **Stop condition:** not triggered ("neither A nor B collapsed -> report and wait").
- **Mean daily IC, L512 seed 0, sample mean:**
  - A 0.0227 [0.0151, 0.0290], Holm p 0.0000.
  - B 0.0074 [−0.0003, 0.0138], Holm p 0.207.
  - C −0.0002 [−0.0052, 0.0051], Holm p 0.830.
- **H1:** falsifier not met. Its "B weaker" clause has no pre-registered numeric criterion.
- **H2:** falsified (C's IC is not above B's). Negative result.
- **Spread collapse:** none (S: A 0.116, B 0.115, C 0.884).
- **Exploratory (not pre-registered):** paired A−B IC difference, raw-input baselines, correlation with −r_t,
  calibration, and the top_k sensitivity check are in the facts file, §4.
- **Exploratory top_k sensitivity (A, B; L512 s0; top_k off):**
  - 80% interval coverage 0.722 / 0.727.
  - IC A 0.0038 [−0.0003, 0.0071], B 0.0025 [−0.0015, 0.0062].
  - A−B 0.0013 [−0.0032, 0.0051].
- **Provenance:** forecasts from run_forecasts.py @ 8fcf044 via run_all.sh @ 8a12738; analysis analyze.py @ 8a12738.
