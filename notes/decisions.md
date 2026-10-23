# Decisions

_One line per decision: date — decision — reason. Revisit, don't silently change._

- 2026-10-23 — WSL2 over native Windows — interp tooling and research repos are Linux-first; matches cloud/MATS setups.
- 2026-10-23 — nnsight over TransformerLens — Chronos's custom tokenizer and experimental T5 support in TL; nnsight wraps any PyTorch model.
- 2026-10-23 — Start with Chronos (T5) family — prior SAE work exists on Chronos-T5-Large (comparable), and FinText released finance-pretrained Chronos variants.
- 2026-10-23 — Free daily data (yfinance/Stooq) — enough for probing; no need for the 94-country research set.
- 2026-10-23 — certifi pinned at 2026.10.19 (not the same-day 2026.10.23) — has the eMudhra CA key-compromise fix (GHSA-6q48-6c7w-9gw2) and passes the release-age rule. Do not go below it.
- 2026-10-23 — python-dateutil held at 2.9.0.post0 (downgraded from 3.0.0) — 3.0.0 has no matching GitHub release, so it's unverified; only pandas needs it (>=2.9.0). Revisit when a verified 3.0.0 exists.
- 2026-10-23 — Model pair: FinText/Chronos_Small_<YYYY>_US vs amazon/chronos-t5-small (configs identical field by field; see literature.md). Tiny/Mini pairs available for robustness. Skip Augmented checkpoints (undefined, card year inconsistent).
- 2026-10-23 — Input preprocessing (PROVISIONAL, Chase to confirm) — match FinText's paper where stated: daily excess returns in decimals (total return incl. dividends minus daily risk-free), winsorized to [-1, 1], no extra scaling (Chronos mean-abs scaling only), context 512 (robustness: 252), next-day horizon, point forecast = mean of samples (paper says "conditional expectation via Monte Carlo"; also store median). Risk-free source not stated by FinText -> use Fama-French daily RF (Ken French library) for US. Same inputs fed to both models so the comparison is like-for-like. Can't replicate CRSP filters exactly with free data; apply price >= $5 and drop |ret| > 10x.
- 2026-10-23 — Post-cutoff test data — use the FinText year-YYYY model only on data after YYYY (paper protocol: model t forecasts t+1). For e00 default: Chronos_Small_2023_US on 2024-01-01 onward.
- 2026-10-23 — Preprocessing approved by Chase (the PROVISIONAL entry above is now final).
- 2026-10-23 — e00 universe fixed as of 2023-12-31: S&P 500 constituents on that date (not today's list) — avoids survivorship bias. Source still to choose (e.g. reconstruct from a dated constituents-change history); record it when picked. Residual bias: names delisted after 2023 may be missing from free data — log every ticker with missing/short history rather than silently dropping it.
- 2026-10-23 — Units: returns fed in decimals, clipped to [-1, 1] via `src/returns.py::prepare_returns`, which first fails if median |r| > 0.1 (percent or prices). Check runs before clipping, since clipping would hide percent input. Tests: `tests/test_returns.py`.
- 2026-10-23 — e00 collapse metrics: for each forecast, record sample mean, sample median, and the spread of the forecast samples; compare cross-sectional/time-series variance of each against realised returns, both models.
- 2026-10-23 — Keep httpx2 / httpcore2 2.16.0 — verified genuine Pydantic packages (github.com/pydantic/httpx2); required by huggingface_hub 2.3.0.
