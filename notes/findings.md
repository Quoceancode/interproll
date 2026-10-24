# Findings

_Only confirmed results. Each entry: claim, evidence, baselines it beat, exact provenance (commit, config, command). Include negative results._

## F1 (2026-10-23) — e00: no arm collapses under the pre-registered rule; only FinText has detectable skill
**Claim.** Under the pre-registered collapse definition, none of the three arms is collapsed at L=512 or L=252.
FinText (A) has a positive daily rank IC of about 0.02 in every year, every seed and both contexts. Generic
Chronos on returns (B) and on levels (C) has no IC distinguishable from zero after Holm correction. B and C avoid
"collapse" only because their forecasts are dispersed (D > 0.05), not because they are informative.

**Verdicts (pre-registered, `results/summary.json`).** Stop condition: "Neither A nor B collapsed -> report and wait."

| Arm, L=512 seed 0 | D mean / median | Ties | Mean daily IC [95% CI], mean | median | Holm p (mean) | Verdict |
|---|---|---|---|---|---|---|
| A FinText, returns | 0.065 / 0.070 | 0.002 | 0.0227 [0.0151, 0.0290] | 0.0202 [0.0138, 0.0257] | < 0.001 | not collapsed |
| B generic, returns | 0.105 / 0.113 | 0.002 | 0.0074 [-0.0003, 0.0138] | 0.0068 [-0.0008, 0.0127] | 0.21 | not collapsed (by D only) |
| C generic, levels | 0.299 / 0.297 | 0.002 | -0.0002 [-0.0052, 0.0051] | 0.0006 [-0.0045, 0.0054] | 0.83 | not collapsed (by D only) |

- Ties = 0.002 = 1/474: all forecasts are distinct on a typical day, so the tokenizer-resolution rule for C does
  not apply.
- **Seed 1** agrees on every verdict. A: IC 0.0211 [0.0134, 0.0281]; B: 0.0071 [-0.0007, 0.0135];
  C: 0.0006 [-0.0044, 0.0056] (means).
- **L=252** agrees. A: 0.0232 [0.0166, 0.0303]; B: 0.0087 [0.0014, 0.0148], Holm p 0.076; C: 0.0020 [-0.0024, 0.0065].
- **Per year, A, L512 s0, mean:**
  - 2024 (primary): 0.0220 [0.0114, 0.0328]
  - 2025: 0.0215 [0.0100, 0.0349]
  - 2026 (to Aug): 0.0254 [0.0123, 0.0395]
- **B per year:** 2024 0.0069 [-0.0067, 0.0167]; 2025 0.0072 [-0.0023, 0.0177]; 2026 0.0084 [-0.0029, 0.0276].
- **C per year:** all CIs include 0.
- For scale, daily cross-sectional ICs of 0.01–0.03 are typically economically meaningful.

**Hypotheses.**
- **H1: supported, in its "weaker" form.** A is not collapsed. B is not collapsed either, but is weaker. A's IC CI
  lies entirely above B's: [0.0151, 0.0290] vs [-0.0003, 0.0138]. The exploratory paired difference A−B is
  0.0153 [0.0081, 0.0229]. Caveat: "weaker" had no numeric definition in the pre-registration.
- **H2: falsified (negative result).** C has higher D (0.30 vs 0.105) but not a higher IC (-0.0002 vs 0.0074; the
  exploratory paired B−C is 0.0077 [-0.0016, 0.0150]). Feeding generic Chronos levels instead of returns gives
  more dispersed forecasts but no information. Confound: arm C's tokenizer step is about 0.66% of price, and 37%
  of daily moves are smaller than one bin, so C's extra dispersion is plausibly quantisation noise.
- **Spread: no arm is spread-collapsed by the rule.**
  - S: A 0.116, B 0.115, C 0.884.
  - Spread-|r| IC: A 0.194 [0.184, 0.202], B 0.203 [0.194, 0.211], C 0.200 [0.190, 0.210].
  - A and B pass the S ≥ 0.1 threshold only narrowly; see the open observation below.

**Raw-input baselines (exploratory, `results/exploratory.json`; not pre-registered).**
- **Point forecasts:** IC of -r_t (1-day reversal) 0.0149 [0.0025, 0.0281]; IC of -(5-day return) 0.0135
  [0.0029, 0.0248]; IC of 12-1 momentum 0.0273 [0.0152, 0.0397].
  - A beats the reversal baselines in point estimate but **not** 12-1 momentum. A's skill is in the range of a
    single classic factor, not beyond it.
- **Uncertainty:** trailing 21-day volatility alone predicts |r_{t+1}| with Spearman 0.220 [0.208, 0.230].
  That is **higher than every arm's sample spread** (0.19–0.20). The models' uncertainty adds nothing beyond
  trailing volatility. Negative result.
- **Reaction to the last return:** mean daily Spearman(forecast, -r_t) is +0.21 for A, -0.21 for B and +0.05 for C
  (L512). FinText leans toward reversing yesterday's move; generic Chronos leans toward continuing it. This is a
  candidate mechanism for the A−B gap. It is a hypothesis for e01, not a finding.

**Open observation (unexplained, not a verdict).**
- A and B predictive distributions are far too narrow. The 80% sample interval [q10, q90] covers 14.6% (A) and
  13.5% (B) of outcomes; C covers 67.5%. Median sample std is 0.0019 vs a target std of 0.021.
- Candidate cause: the sampling default top_k=50 (from the model config) truncating return-scale distributions.
  For C it is harmless, because 50 bins span about 35% of price.
- Not confirmed: the median sample range is 70 bins, so the kept tokens are not one contiguous block. It needs a
  top_k-disabled rerun to test.
- The S and spread metrics for A and B, and possibly the mean forecasts, depend on this setting.

**Provenance.**
- Commit 538df76 (code identical to 8a12738 for forecasts and analysis; 538df76 adds results and explore.py).
- Config `experiments/e00_collapse/config.json`; models pinned per decisions.md.
- Commands:
  - `bash experiments/e00_collapse/run_all.sh` (tmux session e00, 2026-10-23 16:44–20:44; all 9 runs exit 0)
  - `~/venvs/tsfm-interp/bin/python experiments/e00_collapse/analyze.py`
  - `cd experiments/e00_collapse && ~/venvs/tsfm-interp/bin/python explore.py`
- Data: 474 stocks; 315,558 forecasts per L512 run and 316,353 per L252 run; targets 2024-01-02..2026-08-31.
- Logs: `cache/e00/logs/`.
