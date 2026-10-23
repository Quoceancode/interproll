# Literature

## Finance-pretrained TSFMs (the models we interpret)
- **Re(Visiting) Time Series Foundation Models in Finance** — Rahimikia, Ni, Wang (arXiv 2511.18578).
  Off-the-shelf TSFMs do poorly on daily excess returns zero-shot and fine-tuned; pretraining from scratch on
  financial data gives substantial forecasting and economic gains. Models released via FinText.ai.
  Treat their headline backtest Sharpe with skepticism (costs, capacity).
- **Pretrained TSFMs for Financial Return Forecasting** — Noguer i Alonso & Pereira Franklin (arXiv 2606.27100).
  Generic TSFMs win most rankings but gains over random walk are small and sparse; not reliable alpha engines.
  Five US equities only; significance (p<0.05) in just two cases.
  Quote verified 2026-10-23 against arxiv.org/html/2606.27100 (v1, 25 Jun 2026; page dated 24 Aug 2026),
  Sec. 6 "Discussion and Limitations": "generic TSFM pretraining is useful but not a substitute for finance-native
  pretraining" (sentence opens "Finally, the results are consistent with contemporaneous evidence...", read
  alongside Rahimikia et al. 2025). Caveat: they do NOT test finance-native pretraining themselves; it is an
  interpretation consistent with Rahimikia et al. Their Sec. 2 also summarises Rahimikia et al. as "finance-native
  pretraining closes much of the gap". Conclusion (Sec. 7): TSFMs are "strong practical defaults for low-data,
  per-asset financial return forecasting" "but they do not solve the fundamental difficulty of financial return
  prediction." -> Not in tension with our premise; it's independent support only for "generic alone is weak".

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

## FinText checkpoints on Hugging Face (checked 2026-10-23; nothing downloaded)
Sources: HF API `api/models?author=FinText`, model cards + `config.json` for Chronos_{Tiny,Mini,Small}_2011_US,
Chronos_Small_2011_Global, Chronos_Small_2011_Augmented; paper arxiv.org/html/2511.18578 (Sec. 2.2, 3.1, 4.1–4.3, 5).
- **Repos:** `FinText/<Family>_<YYYY>_<Region>`, YYYY = 2000..2023, Region in {US, Global, Augmented}
  (Augmented is named `<Family>_<YYYY>_Augmented`). Families: Chronos_Tiny, Chronos_Mini, Chronos_Small,
  TimesFM_8M, TimesFM_20M. 5 families x 24 years x 3 = 360 repos. No Chronos Base/Large/Bolt.
  Collections updated 2025-11-11 (e.g. huggingface.co/collections/FinText/chronos-small-us).
- **License:** apache-2.0 on every repo listed.
- **Sizes:** Chronos_Small 46.2M params (F32 safetensors). Tiny/Mini ~8M/20M per paper footnote 11.
- **"2011" / "US":** card: "pre-trained on U.S. financial time series data up to the year 2011 ... spans from
  1990–2011 ... all U.S. excess return data". Paper: expanding window; "the model estimated for year t is employed
  to produce forecasts for year t+1". US = CRSP, NYSE/AMEX/NASDAQ. Global = 94 countries (CRSP for US +
  Compustat Global, primary venue only). Exact end date (Dec 31?) not stated.
- **"Augmented":** card text says only "augmented financial time series data"; region not stated; undefined on card.
  Paper mentions "synthetic data augmentation" (abstract) and "JKP-augmented" global data (JKP factors, Jensen et
  al. 2023) but the method isn't in the text I could read. Card inconsistency: Chronos_Small_2011_Augmented says
  "up to the year 2012 ... 1990–2012". Avoid Augmented checkpoints until clarified.
- **Input preprocessing (paper):**
  - Daily **excess** returns: return incl. dividends, "net of the local risk-free rate". Risk-free source: **not stated**.
  - Filters: drop nonpositive/missing prices; US price < $5 removed; bottom 5% market cap per country-day removed;
    |ret| > 1000% treated as errors; delisting with missing return -> -30%.
  - Winsorized to [-1, 1] (Eq. 14), returns in decimal units. No x100 scaling stated.
  - Scaling: only Chronos's own mean-absolute scaling inside the tokenizer (Sec. 2.2). Nothing extra stated.
  - Context windows evaluated: 5, 21, 252, 512 trading days; horizon: next-day excess return.
  - Point forecast: "conditional expectation ... via Monte Carlo sampling"; sample count and mean-vs-median **not stated**.
  - Pretraining window/prediction length used during FinText pretraining: **not stated** (config keeps Chronos
    defaults: context_length 512, prediction_length 64, num_samples 20).
- **Architectural matches (config.json compared field by field):**
  | FinText | generic match | T5 config (layers enc/dec, d_model, d_ff, heads) |
  |---|---|---|
  | Chronos_Tiny_* | amazon/chronos-t5-tiny | 4/4, 256, 1024, 4 |
  | Chronos_Mini_* | amazon/chronos-t5-mini | 4/4, 384, 1536, 8 |
  | Chronos_Small_* | amazon/chronos-t5-small | 6/6, 512, 2048, 8 |
  Identical chronos_config too (MeanScaleUniformBins, limits ±15, 4096 tokens, ctx 512, pred 64). FinText
  `_name_or_path` = google/t5-efficient-{tiny,mini,small}. Like-for-like comparisons are possible for
  Tiny/Mini/Small only; Dissecting Chronos used Large, which has no FinText counterpart.
  TimesFM_8M/20M have no generic Google checkpoint of the same size (Google released 200M/500M) -> random-init
  baseline only for those.

## Overlap check against our claim (2026-10-23)
- **Toward Structured Financial Foundation Models** — Raman, Mishra, Potluru, Ganesh (arXiv 2610.26516, Oct 2026): position paper proposing modular, domain-specialised financial foundation models; no experiments or internal analysis. **No overlap** (watch authors for follow-ups).
- **Foundations without Fundamentals: Zero-Shot Blind Spots in Time Series FMs** — Ghoroghchian et al. (ICML 2026): SimpleTimeBench "unit tests" show Chronos-2, Moirai, Toto fail simple trends/periodicity/leading-indicator covariates zero-shot, and fine-tuning fixes one pattern while degrading others; behavioural only, no finance data. **No overlap**; relevant caution that fine-tuned/finance-trained models may trade off generic skills (check in e01).

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
