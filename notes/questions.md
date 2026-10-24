# Research questions

_Ranked. Each must be testable with what the model actually sees._

## Claim (narrowed 2026-10-23 after novelty re-check)
First mechanistic comparison of finance-pretrained vs generic TSFMs, mapping features to finance factors;
builds on time2time (2509.05801).

## e01 — first target (recorded 2026-10-23; ON HOLD pending Chase's foundations work)
**Target:** A's reversal vs B's extrapolation. In e00, A's forecasts correlate +0.21 with −r_t and B's −0.21
(RESULTS_FACTS.md §4.3). Which internal computation sets the sign of each model's reaction to the last return?
- **Pre-step:**
  - Regress A's forecasts (daily cross-sectional) on short-term reversal (−r_t; also 5-day) and 12-1 momentum.
  - Test whether the residual still predicts r_{t+1}: mean daily IC of the residual with a moving-block bootstrap
    CI (as in e00).
  - Pre-register the hypothesis, the falsifier and numeric thresholds before running.
- **Method note:** probing for yesterday's return is trivial, since r_t is in the input. e01 must rely on
  interventions (ablation and activation patching between A and B, e.g. at the last context positions), not only
  on probes. Probes still need the three CLAUDE.md baselines.

## Core
1. Which features exist in the finance-pretrained model but not the generic one (SAE dictionary comparison)?
2. Are momentum, short-term reversal, volatility, and drawdown linearly decodable from activations, beyond what
   the same probe gets from raw recent returns? At which layer do they appear?
3. Do probes on intermediate layers predict next-day returns better than the model's own output head?
4. Are the candidate factor features causal (ablate / steer -> forecast moves as theory predicts)?
5. Which internal features prevent forecast collapse in the finance model but not the generic one?
   (Collapse = near-flat return forecasts, per Forecast Collapse in TSFMs, 2608.14106. Gated on e00.)
6. Readable-vs-used gap per finance factor, compared across the two models: for each factor, probe
   accessibility vs forecast response to an intervention (cf. Dynamical Parameters, 2609.34316).

## Future interp questions
- FinText constant-input behaviour: given a constant return series (0.001 x 512), FinText Chronos_Small_2023_US
  forecasts its lowest bin (median -0.015, i.e. -15 x scale) while generic chronos-t5-small returns ~0.001.
  On realistic returns it is sane (e00 model_checks, 2026-10-23). Which features/heads produce the jump to the
  extreme bin? Is it a learned "zero-variance context = OOD -> crash" feature, a volatility-normalisation
  artefact (mean-scaling of a series with no variance), or tied to how FinText saw flat/missing segments in
  pretraining? Test: vary constant level and add tiny noise; locate the layer where the residual stream diverges
  from generic.

## Controls to add
- Generic-skill cost: run both models on synthetic generic series (trend, seasonality, cf. SimpleTimeBench in
  "Foundations without Fundamentals", ICML 2026). Did finance pretraining cost generic skills? Also separates
  "learned finance structure" from "lost the ability to extrapolate".

## Phase 2
- Feature trajectories across FinText's yearly checkpoints (2000–2023): track matched features as crises enter
  the training data, e.g. Chronos_Small_2007_US vs 2008/2009_US. Do crash/vol-regime features appear only after
  2008 is in the corpus? Needs a feature-matching method across separately trained SAEs.

## From Quocean experience (check the input constraint first)
- Univariate Chronos only sees one price/return series. It cannot "see" divergence against volume, RSI from other
  inputs, funding rates, or macro data. Reframe accordingly:
  - Divergence: does the model represent price-momentum decay (price making new highs while recent return
    magnitude shrinks)? That's the part of divergence computable from one series.
  - Macro: do internal regime features align with external macro regimes (VIX buckets, rate-hike periods,
    March 2020) even though macro was never an input? Probe/label with macro, don't feed it.
  - Model disagreement: does internal uncertainty (forecast quantile spread) track realized volatility,
    and which features drive it?
- Multivariate models with covariates (Chronos-2, Moirai) could take volume or funding as inputs: possible phase 2.
- Crypto as out-of-distribution test: FinText pretraining is equities. Do the same features fire on BTC/ETH?
