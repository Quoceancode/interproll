# e00 — Agent interpretation (AI-WRITTEN)

> **Written by Claude (Opus 5.5), 2026-10-23.** This is the implementing agent's reading, not Chase's. Chase's
> interpretation (`RESULTS_CHASE.md`) is authoritative. Numbers come from `RESULTS_FACTS.md`. Rule for this file:
> it is not edited once Chase starts his own interpretation. New results are appended as dated sections.

Evidence labels: **strong** (holds across seeds, contexts, years and statistics, with tight CIs and a clear
mechanism-free reading); **moderate** (robust but with a known caveat or a post-hoc test); **weak** (single
analysis, wide CIs, or rests on an untested assumption); **speculative** (a hypothesis to test, not a result).

## 1. What the results mean

### 1.1 FinText has small, stable next-day skill; generic Chronos does not — strong
- A's mean daily rank IC is about 0.02 in every cell:
  - L512 and L252, seeds 0 and 1, mean and median.
  - 2024, 2025 and 2026 separately, each year's CI above 0.
- B's IC is about 0.007, with every pre-registered CI touching or crossing 0 at L512 and Holm p ≥ 0.076.
- C's IC is about 0.
- In magnitude, 0.02 is in the range usually called economically meaningful for a daily cross-sectional signal.
  It is not large: R² ≈ IC² ≈ 0.04%.

### 1.2 The A−B gap is real and consistent — strong (moderate on the "pre-registered" axis)
- The paired difference A−B is 0.012–0.015 with CIs well above 0 in all four cells (L512/L252 × mean/median).
- The per-year ICs show A above B in every year, seed and context.
- Caveat: the paired test is post hoc. The pre-registered evidence is only the non-overlapping CIs at L512 s0
  (mean), which is a weaker and stricter-than-needed comparison.
- The A−B gap is what the project premise needed ("finance pretraining adds something measurable").

### 1.3 A's edge is about the size of one classic factor — moderate
- **Raw-input baselines:** 1-day reversal −r_t scores 0.015 [0.002, 0.028], 5-day reversal 0.014, 12-1 momentum
  0.027 [0.015, 0.040].
- A (0.023) beats reversal in point estimate, but the CIs overlap. It does not beat momentum.
- **Reading:** a large part of A's skill may be known factors. The model may have learned a version of reversal
  and/or momentum from its pretraining returns.
- This is not yet shown, because:
  - A's forecast and the factors have not been jointly regressed (that is the e01 pre-step).
  - A and the factors could be complementary rather than redundant.
- **Alternative:** A captures a non-linear or regime-dependent mix whose average IC happens to be similar to one
  factor. Only the residual test distinguishes these.

### 1.4 Candidate mechanism: reversal vs extrapolation — speculative (but the correlation itself is strong)
- **Observed:** A's forecasts correlate +0.21 with −r_t (it leans toward reversing yesterday's move); B's correlate
  −0.21 (it leans toward continuing it).
- In the 2024–26 S&P sample, 1-day reversal has positive IC (0.015). So a forecaster that reverses gains IC, and
  one that extrapolates loses it.
- That is roughly the sign and size of the A−B gap, but it is arithmetic plausibility, not a decomposition.
- **Alternative 1:** B's extrapolation is the generic TSFM prior learned on trending M4/level data ("the last move
  persists"), and finance pretraining overwrote it. Under this reading the "mechanism" is the removal of a wrong
  prior, not the gain of a finance feature.
- **Alternative 2:** both correlations are by-products of how each model handles the most recent token (recency
  weighting), not a learned "reversal" concept.
- **Testable:**
  - Ablate or patch the representation of the last context position(s) from A into B (and vice versa) and
    measure the change in IC and in corr(f, −r_t).
  - Condition on |r_t| large vs small.

### 1.5 H2 is falsified, but the test was weak — moderate
- C (levels) is far more dispersed than B (D 0.30 vs 0.105) and has no IC.
- **Likely cause:** arm C's tokenizer resolution. One bin is about 0.66% of price, 37% of next-day moves are smaller
  than one bin.
  - C's extra dispersion is most plausibly quantisation noise around the last price, not information.
  - This was flagged before the runs. The pre-registered "inconclusive" escape only covered the Ties route, and
    Ties stayed at its minimum, because forecasts differ across stocks even though each stock's samples are coarse.
- **Conclusion:** e00 does not show that the levels representation is useless for generic Chronos. It shows that
  levels at Chronos-small's resolution, with 512-day mean scaling, do not help.
- **Alternative:** generic Chronos simply has no next-day skill on any representation. The B−C difference
  (0.008, CI crossing 0) cannot separate these.
- The confound question ("is B weak because it never saw returns?") stays open.

### 1.6 Uncertainty forecasts add nothing beyond trailing volatility — moderate
- All arms' sample spreads rank next-day |r| at about 0.19–0.20; trailing 21-day vol alone ranks it at 0.22.
- The models' spread is mostly a noisy copy of recent volatility in the context. Not surprising for mean-scaled
  inputs: the scale is a trailing-volatility proxy.
- **Caveat:** the spread is measured on distributions that are clearly truncated or miscalibrated (§1.7), so this
  may change with different sampling settings.

### 1.7 The predictive intervals for A and B are far too narrow — the observation is strong; the cause is speculative
- **Observation:** the 80% interval covers about 14% of outcomes and the 50% interval about 8%, in every seed and
  context. That is extreme miscalibration, about 10× too narrow.
- **Suspicion: top_k = 50** (the model-config sampling default). Sampling keeps only the 50 most probable of
  4,096 tokens. For return-scale inputs a realistic next-day distribution spans hundreds of bins (median |r| is
  about 105 bins), so truncating to 50 tokens would cut the tails and shrink the spread.
- **Against it:** the median sample range is 70 bins (> 50), so the kept tokens are not a single contiguous block.
  The truncation story is incomplete.
- **Alternatives:**
  1. The models genuinely put most probability mass near 0 (overconfident).
  2. A mismatch between our inputs and the pretraining preprocessing (FinText was checked against its paper;
     generic Chronos never saw returns).
  3. Mean-scaling interacting with heavy-tailed returns.
- If top_k is the cause, it also affects the point forecasts (mean of truncated samples) and the S metric, which
  A and B passed only narrowly (0.116 and 0.115 vs a threshold of 0.1).
- The step-6 sensitivity run tests this.

## 2. Weaknesses in the design

1. **Collapse-rule gap:** "spread but uninformative" has no category.
   - The rule is (D < 0.05 AND IC ∋ 0) OR Ties > 0.5. A forecaster that outputs dispersed noise (B, C) is "not
     collapsed".
   - The rule answered the question it was built for (are forecasts flat?), not the question that matters for the
     project (are they informative?).
2. **H1's "weaker" had no numeric threshold.** The H1 verdict therefore cannot be applied mechanically; any
   statement about it is a judgment call.
3. **H2 confounded by tokenizer resolution**, known in advance. The pre-registered escape (Ties-only →
   inconclusive) did not cover the way resolution actually showed up (dispersion, not ties).
4. **The Holm family covers only "IC > 0" per arm**, not between-arm differences, which are the comparisons that
   matter. The A−B paired test is post hoc.
5. **Sampling settings were model-config defaults** (top_k = 50) and were not varied. Spread and calibration
   results depend on them.
6. **Universe and survivorship:** 474/500 stocks; 26 missing (mostly acquisitions and renames). Acquired names
   tend to have distinct return behaviour. The bias is small (5%) but unmeasured.
7. **One model size and one FinText vintage** (Small, 2023). Generalisation to Tiny/Mini or other years is untested.
8. **No random-init baseline in e00** (CLAUDE.md requires it for probes, not for this forecast check). It would
   show what IC a model with no training gets from the same pipeline (should be about 0).
9. **Per-year CIs are uncorrected.** C at L252 2024 has a CI above 0 (0.0088 [0.0021, 0.0169]). Among 54 per-year
   cells, one or two such excursions are expected by chance.

## 3. Recommended next steps (Chase decides)
1. **Read the top_k sensitivity result** (appended below when available) before trusting any spread or
   calibration number.
2. **e01 pre-step (cheap, decisive for framing):** regress A's forecast on −r_t, 5-day reversal and 12-1 momentum
   (daily cross-sectional regressions). Then test whether the residual still has IC > 0 (block-bootstrap CI).
   - Residual IC about 0: A ≈ known factors, and the interp question becomes "how does it compute reversal and
     momentum?"
   - Residual IC > 0: there is something beyond known factors to find.
3. **e01 first target:** the sign of the reaction to r_t (A reverses, B extrapolates). Use interventions (ablation,
   activation patching between A and B on the last positions), not only probes. Probing for r_t is trivial: it is
   in the input.
4. **For future pre-registrations:** give every comparative hypothesis a numeric threshold, and add a "spread but
   uninformative" category to collapse-style rules (recorded in decisions.md).
5. **Optional:** a random-init arm (one run, about 30 min) to anchor the IC scale.

---

## Appended 2026-10-23 — top_k sensitivity (AI-WRITTEN)
Facts: `RESULTS_FACTS.md`, "Exploratory: top_k sensitivity". This section changes several readings above. The
sections above are left as written.

### What changed
- **Calibration:** with top_k off, A and B intervals are close to calibrated. The 80% interval covers 72–73% (it
  was 14%) and the 50% interval covers 45–46%; sample std is about 0.0155 vs a target std of 0.021.
  - **The top_k suspicion (§1.7) is confirmed as the main cause of the narrow intervals** — strong.
  - The models' full distributions are roughly right in width (slightly narrow). The default top_k = 50 cut them
    about 8× too narrow.
- **Point skill:** with top_k off, A's IC falls from 0.023 to 0.004 (CI touching 0). B falls from 0.007 to 0.002.
  The A−B gap is 0.001–0.002 with a CI around 0.
  - Under full sampling, e00 no longer shows that FinText forecasts better than generic Chronos.

### Two competing explanations — the key open question
1. **Monte Carlo noise in the point forecast** (my leading explanation — moderate):
   - The point forecast is the mean (or median) of only 20 samples. With top_k off, each sample has std about
     0.0155, so the sample mean has a standard error of about 0.0155/√20 ≈ 0.0035.
   - The cross-sectional spread of A's informative signal under top_k 50 was only about 0.065 × 0.021 ≈ 0.0014.
     Sampling noise is then about 2.5× the signal, which would wipe out most of the rank IC even if the model's
     conditional mean were unchanged.
   - Under top_k 50 the samples were concentrated (std about 0.0019, SE about 0.0004), so the 20-sample mean
     tracked the model's central tendency closely.
   - Consistent with this: D rose from 0.065 to 0.27, roughly what adding noise of SE ≈ 0.0035 to a signal of
     spread 0.0014 would do.
2. **Truncation itself creates the signal** (alternative — weak to moderate):
   - top_k 50 keeps the most probable tokens, so the default point forecast tracks the *mode* region of the
     predicted distribution.
   - FinText's skill could live in the location of the mode (e.g. a shift toward reversal near 0), not in the full
     mean, which would be dominated by the tails.
   - In that case the "skill" is a property of mode-seeking decoding, still real and usable, but it changes what
     the interp target is.

These are distinguishable cheaply and without sampling noise. Compute the **exact** predictive mean and median
(and mode) of the next token from the model's logits: one forward pass per context, softmax over the 4,096 bins,
expectation over bin centres × scale.
- If A's exact-mean IC is about 0.02 and the A−B gap returns → explanation 1. The default-run finding stands and
  the top_k-off drop is a measurement artefact.
- If only the exact mode or median shows the gap → explanation 2.
- If neither shows it → A's e00 edge depended on truncated decoding.

### Revised strength of earlier claims
- §1.1 and §1.2 (A has skill; the A−B gap is real): **downgraded from strong to moderate.** They hold under the
  pre-registered (default) decoding across seeds, years and contexts. They do not hold under full sampling with 20
  samples, and why is unresolved.
- §1.4 (reversal vs extrapolation): still **speculative**. The exact-logit check should precede it, since the
  contrast itself was measured on default-decoded forecasts.
- §1.6 (spread adds nothing beyond trailing vol): **unchanged.** Spread IC under top_k off is 0.199 / 0.204,
  still below trailing vol's 0.220.
- The pre-registered verdicts themselves are unaffected (they were defined on the default decoding).

### Recommended next step (before e01; Chase decides)
- **An exact-logit forecast for A and B** at L512 over the same tasks. No sampling, so no seed or top_k choice.
  Report IC for the exact mean, median and mode, and the A−B paired difference.
- Cost: about 1 GPU-hour or less (one forward pass instead of 20 samples).
- This also gives e01 a deterministic point forecast to intervene on, which interventions need anyway.
