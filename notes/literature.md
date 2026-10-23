# Literature

## Finance-pretrained TSFMs (the models we interpret)
- **Re(Visiting) Time Series Foundation Models in Finance** — Rahimikia, Ni, Wang (arXiv 2511.18578).
  Off-the-shelf TSFMs do poorly on daily excess returns zero-shot and fine-tuned; pretraining from scratch on
  financial data gives substantial forecasting and economic gains. Models released via FinText.ai.
  Treat their headline backtest Sharpe with skepticism (costs, capacity).
- **Pretrained TSFMs for Financial Return Forecasting** — Noguer i Alonso & Pereira Franklin (arXiv 2606.27100).
  Generic TSFMs win most rankings but gains over random walk are small and sparse; not reliable alpha engines.

## Interpretability of TSFMs (what's already done)
- **Dissecting Chronos** — Mishra (arXiv 2603.10071, ICLR 2026 TSALM workshop). TopK SAEs on Chronos-T5-Large,
  six layers, 392 single-feature ablations. Early layers: frequency; mid-encoder: causally critical change-detection;
  final encoder: rich but less causal. Generic checkpoint, generic benchmark.
- **Finding the Zeitgeist in TSFMs** (ICLR 2026 workshop). SAEs on pretrained TSFMs; features align with temporal patterns.
- **On the Internal Semantics of TSFMs** — Pandey et al. (arXiv 2511.15324, NeurIPS 2025 workshop).
  Linear probes for seven synthetic concepts (AR1, level shift, random walk, spectral, warp, trend, variance shift).
- **Universal Redundancies in TSFMs** — Bao et al. (PMLR v306). Ablations + direct logit attribution across
  Chronos, TimesFM, Toto, Moirai; ~28% of heads removable for <=6% loss. Has a code toolbox.
- **Exploring Representations and Interventions in TSFMs** (arXiv 2409.12915). Probing + steering along concept directions.
- **TSAE** (arXiv 2610.04925, Oct 2026). Structured SAE for forecasting models; cites TimeSAE (Oublal et al., 2026).

## Analogy for our framing
- **Pathology foundation model SAEs** (arXiv 2407.10785). Domain-specific features appear in the domain-pretrained
  model but not in a natural-image model. Our analogue: finance-pretrained vs generic Chronos.

## Open gap (as of 2026-10-23, re-verify)
No work found interpreting a finance-pretrained TSFM or mapping features to finance factors, or comparing
finance vs generic checkpoints mechanistically.
