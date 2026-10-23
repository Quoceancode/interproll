# Research questions

_Ranked. Each must be testable with what the model actually sees._

## Claim (narrowed 2026-10-23 after novelty re-check)
First mechanistic comparison of finance-pretrained vs generic TSFMs, mapping features to finance factors;
builds on time2time (2509.05801).

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
