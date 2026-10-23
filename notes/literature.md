# Literature

## Finance-pretrained TSFMs (the models we interpret)
- **Re(Visiting) Time Series Foundation Models in Finance** — Rahimikia, Ni, Wang (arXiv 2511.18578).
  Off-the-shelf TSFMs do poorly on daily excess returns zero-shot and fine-tuned; pretraining from scratch on
  financial data gives substantial forecasting and economic gains. Models released via FinText.ai.
  Treat their headline backtest Sharpe with skepticism (costs, capacity).
- **Pretrained TSFMs for Financial Return Forecasting** — Noguer i Alonso & Pereira Franklin (arXiv 2606.27100).
  Generic TSFMs win most rankings but gains over random walk are small and sparse; not reliable alpha engines.
  Five US equities only; significance (p<0.05) in just two cases. Per a search summary (not yet read in full) it
  concludes generic pretraining is "not a substitute for finance-native pretraining" — so it doesn't contradict
  our premise as much as it first seemed. Verify against the PDF before citing.

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
  Tested on PatchTST / ETT, not finance.
- **time2time** — Sanyal et al., Birla AI Labs (arXiv 2509.05801, NeurIPS 2025). **Closest neighbour.**
  "Activation transplantation" (match mean/std of hidden states at a layer) moves forecasts crash<->calm on
  **daily NASDAQ-100** (calm 2007/2017/2019, crash 2000/2008/2020) plus synthetic jump-diffusion; latent norm tracks
  shock severity. Models: **generic** Chronos-T5 (tiny-large) and Toto. No finance-pretrained checkpoint, no SAEs,
  no supervised probes (PCA + cosine only), no finance-factor mapping. Code: github.com/birla-ai-labs/time2time.
  -> Prior art for "causal intervention on TSFM hidden states using equity data". Cite it; our novelty is
  finance-pretrained vs generic + factor mapping, not interventions on market data per se.
- **Dynamical Parameters** — Yang, Dong, Han, Srivastava (arXiv 2609.34316, Sep 2026). 9 frozen TSFMs, 13 dynamical
  laws (trend slope, frequency, AR dependence): parameters are linearly accessible (42/63 cells >0.95) but forecasts
  respond weakly (median 0.46); input-level interventions push hidden state off the causal direction. Not finance.
  -> Directly relevant to Q2/Q4: decodable != used. Supports requiring interventions, not just probes.
- **Non-Stationarity in the Embedding Space of TSFMs** — Choi, Shook, Dubrawski (arXiv 2604.16428, Apr 2026).
  Linear probes for mean shift, variance change, trend, near-unit-root persistence; detectability degrades smoothly
  with shift strength. Not finance. Useful probe design reference for volatility-regime targets.
- **Superposition Is Not Necessary** (arXiv 2605.05151). Mechanistic analysis of PatchTST; finds no strong
  superposition in post-GELU FFN activations. Not finance, not a foundation model. (Abstract-level only.)
- **Towards Interpretable TSFMs** (arXiv 2507.07439) and **Decoding Latent Spaces** (arXiv 2504.20099): earlier
  generic TSFM interpretability; not read in detail.

## Finance x TSFM, no internals (checked, not interpretability)
- **Forecast Collapse in TSFMs** (arXiv 2608.14106). 1,000 US equities (Finance1K): TSFM return forecasts go flat;
  disappears for volume. Behavioural only. Relevant: our probes must check the generic model isn't just collapsed.
- **Forecasting Realized Volatility with TSFMs** — Brini (arXiv 2607.05291). Performance only.
- **VAIOM** (arXiv 2607.13929). Finance sequence model trained from scratch; performance/ablations, no interp.
- **Kronos** (arXiv 2508.02739, AAAI). Finance K-line foundation model; no interpretability work found on it.
  Possible second finance-pretrained model for a robustness check (different tokenizer, though).
- **Toward Structured Financial Foundation Models** — Raman, Mishra, Potluru, Ganesh (arXiv 2610.26516, Oct 2026).
  Position paper / research agenda. Mentions specialists "may learn incompatible representations" but no analysis.
  Watch these authors for follow-ups.

## Analogy for our framing
- **Pathology foundation model SAEs** (arXiv 2407.10785). Domain-specific features appear in the domain-pretrained
  model but not in a natural-image model. Our analogue: finance-pretrained vs generic Chronos.
- Domain-pretrained vs generic TSFM comparisons exist in other domains, but at performance/ablation level, not
  mechanistic: STAMP (EEG, arXiv 2511.10848), PE-TSFM (power converters, 2511.08250), MMR (PPG, 2601.12215).

## Rahimikia / Ni / Wang — recent work (checked 2026-10-23)
- arXiv author listing for Rahimikia: only 2511.18578 (TSFMs in finance), 2404.18543 (Time Machine GPT),
  2108.00480 (RV forecasting with financial word embeddings; v7 updated 2026-08-31).
- Google Scholar profile: newest item is "Machine learning for realised volatility forecasting"
  (J. Empirical Finance, 2026, art. 101739). No interpretability work.
- No newer arXiv papers found for Hao Ni or Weiguan Wang on finance TSFMs.
- 2511.18578 is also SSRN 5770562. Scholar: cited by 18; Semantic Scholar lists 10 citing papers, none analyse internals.

## Search log
### 2026-10-23 — novelty re-check (Claude, for Chase)
Sources: arXiv API (abstract keyword queries, sorted by date; cs.LG/q-fin/all), arXiv author query
(Rahimikia / Ni / Wang), Google Scholar (profile + one query; then rate-limited with CAPTCHA, not pursued),
Semantic Scholar citations API for 2511.18578, SSRN via web search, general web search.
Queries included: TSFM + {interpretability, sparse autoencoder, probing, mechanistic, ablation};
foundation model + {interpretability, SAE, probe} + {financial, stock, returns}; FinText Chronos interpretability;
Kronos interpretability; Chronos-2 SAE.
Coverage limits: Scholar citing-papers list not read (CAPTCHA), so up to 8 citing papers unchecked; most hits
judged from abstracts only; SSRN search returned no finance-TSFM interpretability papers but SSRN search via web
engine is shallow.

## Open gap (as of 2026-10-23, re-verified above)
Still no work found that (a) interprets a finance-pretrained TSFM (FinText or Kronos), (b) maps TSFM features to
finance factors (momentum, reversal, vol clustering, drawdown), or (c) compares finance vs generic checkpoints
mechanistically. Nearest: time2time (interventions on generic Chronos/Toto with NASDAQ-100 crash regimes).
Claim novelty narrowly: "first mechanistic comparison of finance-pretrained vs generic TSFMs", and cite time2time.
