# e00 — Results: facts

_Factual record only. Interpretation is in `RESULTS_AGENT_INTERPRETATION.md` (AI-written) and `RESULTS_CHASE.md`._
_All ICs are means of daily values with 95% moving-block bootstrap CIs (Definitions, below)._

## 1. Setup

| Item | Value |
|---|---|
| Arm A | FinText/Chronos_Small_2023_US @ f60a282f3dbead8e054154b8bc8d83b227f8693b; input: daily excess returns |
| Arm B | amazon/chronos-t5-small @ a971ba21945c4f1796b17a91fe69214b5f4ad472; input: daily excess returns |
| Arm C | amazon/chronos-t5-small @ a971ba21…; input: total-return index (cumprod(1+R)) normalised to 1 at window start; each sample P̂ → P̂/P_t − 1 − RF_{t+1}, clipped to [−1, 1] |
| Universe | S&P 500 as of 2023-12-31: fja05680/sp500 @ a2430f2a (row 2023-12-18) and Wikipedia rev 1192789360, 503 = 503; GOOG, FOX, NWS dropped → 500 |
| Usable stocks | 474 of 500 (26 missing, 5.2%: 20 HTTP 404, 5 Yahoo truncated, 1 excluded data error (PARA)) |
| Prices / RF | Yahoo chart v8 adjclose; Ken French daily RF (percent / 100) |
| Preprocessing | excess return = R − RF; `src/returns.py::prepare_returns` (unit check, clip to [−1, 1]); 1 value clipped (MRNA 2026-08-19) |
| Targets | next-day excess return, target dates 2024-01-02 .. 2026-08-31 (668 trading days) |
| Contexts / seeds | L = 512 (seeds 0, 1), L = 252 (seed 0); full context required (no padding) |
| Sampling | `ChronosPipeline.predict(prediction_length=1, num_samples=20)`, model-config defaults: temperature 1.0, top_k 50, top_p 1.0 |
| Forecasts per run | 315,558 (L = 512); 316,353 (L = 252) |
| Point statistics | mean and median of the 20 samples |
| Runs | 9; tmux session e00, 2026-10-23 16:44:37 – 20:44:02 (−07:00); all exit code 0 |

## 2. Definitions

Notation: f_{i,t} = point forecast (sample mean or median) for stock i, made at origin t for target date t+1;
r_{i,t+1} = realised excess return. "Day" = target date. N_t = number of stocks with a forecast on day t.

- **D (dispersion ratio, cross-sectional)** = median over days of [std_i(f_{i,t}) / std_i(r_{i,t+1})]
  (pandas std, ddof = 1).
- **D_timeseries** = median over stocks of [std_t(f_{i,t}) / std_t(r_{i,t+1})].
- **Ties** = median over days of [count of the most frequent value of f_{·,t} / N_t]. Minimum possible value
  is 1/N_t (all values distinct).
- **Daily IC** = Spearman rank correlation across stocks of (f_{·,t}, r_{·,t+1}) on day t (average ranks for ties).
  Days with undefined correlation would be set to 0 and counted (`ic_days_undefined`); there were 0 such days.
- **Mean IC** = mean of daily ICs over the evaluation days (or over the days of one calendar year).
- **Moving-block bootstrap** (all ICs, spread IC and paired differences): from the n daily values, draw
  ceil(n/20) block start positions uniformly from {0, …, n−20}; concatenate blocks of 20 consecutive days;
  truncate to n; take the mean. Repeat 2,000 times (numpy default_rng, seed 0). 95% CI = 2.5% and 97.5%
  quantiles of the 2,000 means. One-sided p (`ic_p_le_zero`) = share of bootstrap means ≤ 0 (resolution
  1/2000 = 0.0005; p = 0 means none of the 2,000 was ≤ 0).
- **Holm correction**: family = the 12 seed-0 tests (3 arms × {mean, median} × {L512, L252}) of IC > 0, using the
  one-sided bootstrap p. Sort p ascending p_(1) ≤ … ≤ p_(12); adjusted p_(k) = max_{j ≤ k} min(1, (12 − j + 1)·p_(j)).
- **Pooled Pearson** = Pearson correlation of f and r over all stock-days of a run.
- **S (spread ratio)** = median over all stock-days of the sample std (20 samples, ddof = 0) / median over all
  stock-days of trailing realised vol, where trailing vol = std (ddof = 1) of the stock's last 21 excess returns
  through the origin t.
- **Spread IC** = mean daily Spearman(sample std_{·,t}, |r_{·,t+1}|), with bootstrap CI as above.
- **Point collapse** (arm, statistic, L, seed) = (D < 0.05 AND the IC 95% CI includes 0) OR Ties > 0.5.
- **Spread collapse** (arm, L, seed) = S < 0.1 OR the spread-IC 95% CI includes 0.
- **Arm verdict** = "collapsed" if point collapse holds under both mean and median at L = 512 seed 0, with seed 1
  agreeing ("ambiguous (seeds disagree)" otherwise). For arm C: "inconclusive (tokenizer resolution)" if it is
  collapsed only via the Ties clause.
- **Stop condition**: stop (no e01) if A and B are both "collapsed" at L = 512; every other outcome → report and wait.
- **H1**: A is not collapsed; B is collapsed or weaker than A. Pre-registered falsifier: A is collapsed.
- **H2**: C is less collapsed than B: higher D and higher mean IC (L = 512, seed 0). Pre-registered falsifier:
  C's D and IC are not both above B's.

## 3. Pre-registered results

### 3.1 Point-forecast metrics, all runs

| Arm | L | Seed | Stat | D | D_ts | Ties | Mean IC [95% CI] | p (one-sided) | Holm p | Pooled Pearson | Point collapse |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 512 | 0 | mean | 0.0650 | 0.0537 | 0.0021 | 0.0227 [0.0151, 0.0290] | 0.0000 | 0.0000 | 0.0221 | False |
| A | 512 | 0 | median | 0.0697 | 0.0535 | 0.0106 | 0.0202 [0.0138, 0.0257] | 0.0000 | 0.0000 | 0.0187 | False |
| B | 512 | 0 | mean | 0.1054 | 0.0741 | 0.0021 | 0.0074 [−0.0003, 0.0138] | 0.0345 | 0.2070 | −0.0079 | False |
| B | 512 | 0 | median | 0.1127 | 0.0806 | 0.0084 | 0.0068 [−0.0008, 0.0127] | 0.0445 | 0.2225 | −0.0076 | False |
| C | 512 | 0 | mean | 0.2985 | 0.2551 | 0.0021 | −0.0002 [−0.0052, 0.0051] | 0.5115 | 0.8300 | 0.0009 | False |
| C | 512 | 0 | median | 0.2967 | 0.2527 | 0.0021 | 0.0006 [−0.0045, 0.0054] | 0.4150 | 0.8300 | −0.0007 | False |
| A | 512 | 1 | mean | 0.0652 | 0.0544 | 0.0021 | 0.0211 [0.0134, 0.0281] | 0.0000 | — | 0.0210 | False |
| A | 512 | 1 | median | 0.0694 | 0.0527 | 0.0106 | 0.0183 [0.0115, 0.0240] | 0.0000 | — | 0.0233 | False |
| B | 512 | 1 | mean | 0.1047 | 0.0737 | 0.0021 | 0.0071 [−0.0007, 0.0135] | 0.0400 | — | −0.0083 | False |
| B | 512 | 1 | median | 0.1125 | 0.0808 | 0.0084 | 0.0057 [−0.0021, 0.0118] | 0.0775 | — | −0.0086 | False |
| C | 512 | 1 | mean | 0.3003 | 0.2562 | 0.0021 | 0.0006 [−0.0044, 0.0056] | 0.4170 | — | 0.0004 | False |
| C | 512 | 1 | median | 0.2982 | 0.2557 | 0.0021 | −0.0027 [−0.0073, 0.0022] | 0.8475 | — | −0.0039 | False |
| A | 252 | 0 | mean | 0.0724 | 0.0573 | 0.0021 | 0.0232 [0.0166, 0.0303] | 0.0000 | 0.0000 | 0.0180 | False |
| A | 252 | 0 | median | 0.0749 | 0.0574 | 0.0084 | 0.0194 [0.0134, 0.0257] | 0.0000 | 0.0000 | 0.0163 | False |
| B | 252 | 0 | mean | 0.1088 | 0.0790 | 0.0021 | 0.0087 [0.0014, 0.0148] | 0.0095 | 0.0760 | −0.0088 | False |
| B | 252 | 0 | median | 0.1135 | 0.0846 | 0.0063 | 0.0075 [0.0004, 0.0131] | 0.0175 | 0.1225 | −0.0097 | False |
| C | 252 | 0 | mean | 0.3108 | 0.2643 | 0.0021 | 0.0020 [−0.0024, 0.0065] | 0.1865 | 0.5595 | 0.0025 | False |
| C | 252 | 0 | median | 0.3067 | 0.2624 | 0.0021 | 0.0024 [−0.0014, 0.0059] | 0.0960 | 0.3840 | 0.0025 | False |

- Ties 0.0021 = 1/474 (all values distinct on the median day).
- Holm p is defined only for the seed-0 family. `results/metrics.csv` repeats the seed-0 Holm values in its seed-1
  rows (the lookup key omits the seed). Those seed-1 values are not Holm tests.
- No row meets the D-and-IC clause (every D ≥ 0.05) or the Ties clause.

### 3.2 IC by calendar year (mean IC [95% CI])

2026 = 2026-01-02 .. 2026-08-31.

| Arm | L | Seed | Stat | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| A | 512 | 0 | mean | 0.0220 [0.0114, 0.0328] | 0.0215 [0.0100, 0.0349] | 0.0254 [0.0123, 0.0395] |
| A | 512 | 0 | median | 0.0179 [0.0091, 0.0271] | 0.0211 [0.0118, 0.0321] | 0.0222 [0.0097, 0.0351] |
| B | 512 | 0 | mean | 0.0069 [−0.0067, 0.0167] | 0.0072 [−0.0023, 0.0177] | 0.0084 [−0.0029, 0.0276] |
| B | 512 | 0 | median | 0.0054 [−0.0083, 0.0150] | 0.0066 [−0.0024, 0.0156] | 0.0091 [−0.0027, 0.0275] |
| C | 512 | 0 | mean | −0.0004 [−0.0039, 0.0071] | 0.0006 [−0.0101, 0.0101] | −0.0013 [−0.0107, 0.0101] |
| C | 512 | 0 | median | 0.0014 [−0.0026, 0.0104] | −0.0001 [−0.0088, 0.0100] | 0.0003 [−0.0086, 0.0088] |
| A | 512 | 1 | mean | 0.0219 [0.0109, 0.0345] | 0.0178 [0.0068, 0.0326] | 0.0248 [0.0125, 0.0390] |
| A | 512 | 1 | median | 0.0181 [0.0086, 0.0292] | 0.0142 [0.0049, 0.0262] | 0.0248 [0.0142, 0.0369] |
| B | 512 | 1 | mean | 0.0061 [−0.0077, 0.0155] | 0.0083 [−0.0008, 0.0184] | 0.0067 [−0.0043, 0.0273] |
| B | 512 | 1 | median | 0.0032 [−0.0101, 0.0124] | 0.0077 [−0.0012, 0.0168] | 0.0065 [−0.0037, 0.0266] |
| C | 512 | 1 | mean | 0.0029 [−0.0028, 0.0113] | −0.0005 [−0.0092, 0.0103] | −0.0015 [−0.0110, 0.0065] |
| C | 512 | 1 | median | −0.0012 [−0.0067, 0.0062] | −0.0049 [−0.0125, 0.0053] | −0.0015 [−0.0122, 0.0071] |
| A | 252 | 0 | mean | 0.0256 [0.0175, 0.0377] | 0.0206 [0.0080, 0.0344] | 0.0236 [0.0117, 0.0369] |
| A | 252 | 0 | median | 0.0199 [0.0125, 0.0308] | 0.0171 [0.0061, 0.0293] | 0.0223 [0.0101, 0.0353] |
| B | 252 | 0 | mean | 0.0078 [−0.0050, 0.0178] | 0.0091 [−0.0013, 0.0198] | 0.0096 [−0.0018, 0.0259] |
| B | 252 | 0 | median | 0.0062 [−0.0066, 0.0158] | 0.0080 [−0.0019, 0.0176] | 0.0088 [−0.0019, 0.0244] |
| C | 252 | 0 | mean | 0.0088 [0.0021, 0.0169] | −0.0021 [−0.0090, 0.0029] | −0.0020 [−0.0097, 0.0056] |
| C | 252 | 0 | median | 0.0073 [0.0019, 0.0133] | −0.0020 [−0.0077, 0.0017] | 0.0016 [−0.0058, 0.0080] |

Per-year CIs are not multiplicity-corrected.

### 3.3 Spread metrics

| Arm | L | Seed | S | Spread IC [95% CI] | Spread collapse |
|---|---|---|---|---|---|
| A | 512 | 0 | 0.1161 | 0.1937 [0.1841, 0.2018] | False |
| B | 512 | 0 | 0.1151 | 0.2026 [0.1935, 0.2109] | False |
| C | 512 | 0 | 0.8838 | 0.2000 [0.1896, 0.2090] | False |
| A | 512 | 1 | 0.1161 | 0.1939 [0.1849, 0.2022] | False |
| B | 512 | 1 | 0.1150 | 0.2028 [0.1941, 0.2115] | False |
| C | 512 | 1 | 0.8832 | 0.2001 [0.1898, 0.2097] | False |
| A | 252 | 0 | 0.1171 | 0.1900 [0.1809, 0.1983] | False |
| B | 252 | 0 | 0.1107 | 0.2127 [0.2033, 0.2211] | False |
| C | 252 | 0 | 0.8920 | 0.2018 [0.1909, 0.2116] | False |

### 3.4 Verdicts (`results/summary.json`)

| Arm | Verdict L512 | Collapsed L252 | L512 and L252 agree | Seeds agree |
|---|---|---|---|---|
| A | not collapsed | False | True | True |
| B | not collapsed | False | True | True |
| C | not collapsed | False | True | True |

- **Stop condition:** "Neither A nor B collapsed -> report and wait for Chase."
- **H1:**
  - Falsifier (A collapsed): not met.
  - Clause "B collapsed": not met.
  - Clause "B weaker": no numeric criterion was pre-registered. Recorded comparison (L512 s0, mean): A IC 0.0227
    [0.0151, 0.0290] vs B IC 0.0074 [−0.0003, 0.0138]; the CIs do not overlap.
- **H2:**
  - L512 s0, mean: C D 0.2985 > B D 0.1054 (true); C IC −0.0002 > B IC 0.0074 (false); IC CIs overlap.
  - L512 s0, median: C D 0.2967 > B D 0.1127 (true); C IC 0.0006 > B IC 0.0068 (false).
  - The pre-registered falsifier is met: **H2 falsified**.
- **Arm C tokenizer-resolution rule:** not triggered (C is not collapsed by any clause).

## 4. Exploratory results (not pre-registered; analyses written after the pre-registered results were seen)

### 4.1 Paired daily IC differences (`explore.py`, `results/exploratory.json`)
Daily IC_x − IC_y on the same days; mean [95% block-bootstrap CI]; one-sided p = share of bootstrap means ≤ 0.

| Pair | L512 s0, mean | L512 s0, median | L252 s0, mean | L252 s0, median |
|---|---|---|---|---|
| A − B | 0.0153 [0.0081, 0.0229], p 0.0000 | 0.0134 [0.0071, 0.0206], p 0.0005 | 0.0145 [0.0092, 0.0220], p 0.0000 | 0.0119 [0.0068, 0.0188], p 0.0000 |
| A − C | 0.0229 [0.0153, 0.0288], p 0.0000 | 0.0196 [0.0122, 0.0256], p 0.0000 | 0.0212 [0.0131, 0.0296], p 0.0000 | 0.0171 [0.0099, 0.0243], p 0.0000 |
| B − C | 0.0077 [−0.0016, 0.0150], p 0.054 | 0.0062 [−0.0030, 0.0138], p 0.1005 | 0.0067 [−0.0022, 0.0144], p 0.0785 | 0.0052 [−0.0027, 0.0117], p 0.1105 |

### 4.2 Raw-input baselines (same days and stocks as arm A, L512 s0)
Features are computed from excess returns known at origin t.

| Feature | Definition | Mean daily IC vs r_{t+1} [95% CI] |
|---|---|---|
| 1-day reversal | −r_t | 0.0149 [0.0025, 0.0281] |
| 5-day reversal | −(r_{t−4} + … + r_t) | 0.0135 [0.0029, 0.0248] |
| 12-1 momentum | r_{t−251} + … + r_{t−21} | 0.0273 [0.0152, 0.0397] |
| Trailing 21-day vol vs \|r_{t+1}\| (spread baseline) | std of r_{t−20..t} | 0.2200 [0.2076, 0.2303] |

The L252 rows are equal to 3 decimals; see `exploratory.json`.

### 4.3 Correlation of forecasts with −r_t
Mean over days of the daily Spearman(f mean, −r_t).

| Arm | L512 s0 | L252 s0 |
|---|---|---|
| A | +0.2095 | +0.1562 |
| B | −0.2054 | −0.2398 |
| C | +0.0486 | +0.0220 |

### 4.4 Calibration of sample distributions (`calibration.py`, `results/calibration.json`)

| Run | Coverage [q10, q90] | Coverage [q25, q75] | Median sample std | Median q90 − q10 | Median sample range (bins) | Rows with an extreme-bin sample |
|---|---|---|---|---|---|---|
| A_L512_s0 | 0.1455 | 0.0856 | 0.00187 | 0.00473 | 70.0 | 0.29% |
| B_L512_s0 | 0.1352 | 0.0797 | 0.00186 | 0.00466 | 69.0 | 0.003% |
| C_L512_s0 | 0.6755 | 0.4061 | 0.01427 | 0.03134 | — | — |
| A_L512_s1 | 0.1457 | 0.0855 | 0.00188 | 0.00473 | 70.0 | 0.28% |
| B_L512_s1 | 0.1349 | 0.0800 | 0.00186 | 0.00466 | 69.0 | 0.003% |
| C_L512_s1 | 0.6761 | 0.4065 | 0.01426 | 0.03136 | — | — |
| A_L252_s0 | 0.1471 | 0.0866 | 0.00189 | 0.00475 | 72.0 | 0.31% |
| B_L252_s0 | 0.1287 | 0.0755 | 0.00179 | 0.00446 | 69.0 | 0.004% |
| C_L252_s0 | 0.6812 | 0.4107 | 0.01439 | 0.03175 | — | — |

- Nominal coverage of [q10, q90] is 0.80; nominal coverage of [q25, q75] is 0.50.
- Realised target: std 0.0209; median |r| 0.0096. In tokenizer bins for A/B, median |r| is 105 (L512) and
  107 (L252).
- Bins = sample range / (0.007331 × mean |context|). p99 of the sample range: A 225 bins, B 115 bins (L512 s0).
- "Extreme bin" = |sample| ≥ (15 − 0.007331) × mean |context|.

### 4.5 Observations recorded before the runs (step 4, `results/model_checks.json`, `results/armC_resolution.json`)
- **Constant input** (0.001 × 512): generic chronos-t5-small median forecast 0.000997; FinText median forecast
  −0.015 (the lowest bin). On 64 real 2023 contexts, FinText had 0 samples at the lowest bin.
- **Tokenizer step in return units** (L512; quantiles 5 / 50 / 95%):
  - Arm C: 0.475% / 0.662% / 1.021% of price.
  - Arms A/B: 0.0063% / 0.0090% / 0.0154%.
  - Realised |r| median: 0.96%.
- **Share of next-day moves smaller than one bin:** arm C 37.3% (smaller than half a bin: 19.5%); arms A/B 0.59%.
- **Arm C step / the stock's median |move|:** median 0.72 (5–95%: 0.41–0.96).

## 5. Provenance

| Step | Script (last commit) | Command (repo root, `PY=~/venvs/tsfm-interp/bin/python`) |
|---|---|---|
| Data | fetch_data.py, universe.py, build_panel.py (bc35869); src/returns.py (e2b43a2) | `$PY experiments/e00_collapse/fetch_data.py {constituents,rf,prices}`; `universe.py`; `build_panel.py` |
| Models | src/models.py, model_checks.py, armC_resolution.py, config.json (8fcf044) | `$PY experiments/e00_collapse/model_checks.py`; `armC_resolution.py` |
| Forecasts | run_forecasts.py (8fcf044), run_all.sh (8a12738) | `bash experiments/e00_collapse/run_all.sh` (tmux session e00) |
| Pre-registered analysis | analyze.py (8a12738) | `$PY experiments/e00_collapse/analyze.py` |
| Exploratory 4.1–4.3 | explore.py (538df76) | `cd experiments/e00_collapse && $PY explore.py` |
| Exploratory 4.4 | calibration.py (518fc2b) | `$PY experiments/e00_collapse/calibration.py <run names>` |

- **Pre-registration:** `notes/research-log.md`, entry "e00 forecast-collapse check: pre-registration", committed
  before any forecast.
- **Logs:** `cache/e00/logs/` (run logs unfiltered; run_all.log; analyze.log; explore.log; calibration.log).
- **Forecasts:** `cache/e00/forecasts_{arm}_L{L}_s{seed}.parquet` (git-ignored).
- **Environment:** `requirements.txt`; torch 2.11.0+cu128; chronos-forecasting 2.3.2; RTX 5070 Ti; batch size 32.

## Exploratory: top_k sensitivity (added 2026-10-23; not pre-registered)

### Setup
- **Runs:** arms A and B, L = 512, seed 0, with `top_k` = 4096 (the full vocabulary; no truncation).
- **Unchanged from the main runs:** temperature 1.0, top_p 1.0, 20 samples, the same tasks, batch size 32 and seed.
- **Default-path check:** with `top_k` unset, the modified script reproduces the stored B_L512_s0 samples exactly
  (first 64 rows).
- **Runs:** tmux session `e00_topk`, 2026-10-23 21:09:56 – 22:12:53 (−07:00); both exit 0; 315,558 forecasts each.
- **Metrics:** the same functions as §3 (`analyze.run_metrics`; Definitions §2). Holm is not applied (outside the
  pre-registered family).

### Calibration (`calibration.py`)

| Run | Coverage [q10, q90] | Coverage [q25, q75] | Median sample std | Median q90 − q10 | Median sample range (bins) | p99 range (bins) | Rows with an extreme-bin sample |
|---|---|---|---|---|---|---|---|
| A, top_k 50 (main) | 0.1455 | 0.0856 | 0.00187 | 0.00473 | 70.0 | 225 | 0.29% |
| A, top_k off | 0.7219 | 0.4475 | 0.01559 | 0.03414 | 698.2 | 2277 | 0.64% |
| B, top_k 50 (main) | 0.1352 | 0.0797 | 0.00186 | 0.00466 | 69.0 | 115 | 0.003% |
| B, top_k off | 0.7273 | 0.4595 | 0.01528 | 0.03482 | 673.2 | 2060 | 0.31% |

Nominal coverage: 0.80 for [q10, q90] and 0.50 for [q25, q75]. Realised target std: 0.0209.

### Point and spread metrics

| Run | Stat | D | D_ts | Ties | Mean IC [95% CI] | p (one-sided) | Pooled Pearson | S | Spread IC [95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| A, top_k 50 | mean | 0.0650 | 0.0537 | 0.0021 | 0.0227 [0.0151, 0.0290] | 0.0000 | 0.0221 | 0.1161 | 0.1937 [0.1841, 0.2018] |
| A, top_k 50 | median | 0.0697 | 0.0535 | 0.0106 | 0.0202 [0.0138, 0.0257] | 0.0000 | 0.0187 | 0.1161 | 0.1937 [0.1841, 0.2018] |
| A, top_k off | mean | 0.2708 | 0.2289 | 0.0021 | 0.0038 [−0.0003, 0.0071] | 0.0370 | 0.0046 | 0.9654 | 0.1986 [0.1884, 0.2085] |
| A, top_k off | median | 0.2547 | 0.2169 | 0.0042 | 0.0046 [−0.0003, 0.0085] | 0.0355 | 0.0065 | 0.9654 | 0.1986 [0.1884, 0.2085] |
| B, top_k 50 | mean | 0.1054 | 0.0741 | 0.0021 | 0.0074 [−0.0003, 0.0138] | 0.0345 | −0.0079 | 0.1151 | 0.2026 [0.1935, 0.2109] |
| B, top_k 50 | median | 0.1127 | 0.0806 | 0.0084 | 0.0068 [−0.0008, 0.0127] | 0.0445 | −0.0076 | 0.1151 | 0.2026 [0.1935, 0.2109] |
| B, top_k off | mean | 0.2636 | 0.2192 | 0.0021 | 0.0025 [−0.0015, 0.0062] | 0.1270 | −0.0048 | 0.9462 | 0.2036 [0.1939, 0.2125] |
| B, top_k off | median | 0.2674 | 0.2227 | 0.0042 | 0.0024 [−0.0025, 0.0065] | 0.1875 | −0.0017 | 0.9462 | 0.2036 [0.1939, 0.2125] |

Point collapse and spread collapse (rules in §2): False for all four top_k-off rows.

### IC by calendar year, top_k off (mean IC [95% CI])

| Run | Stat | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| A | mean | 0.0086 [0.0024, 0.0132] | 0.0015 [−0.0045, 0.0082] | 0.0002 [−0.0045, 0.0061] |
| A | median | 0.0080 [0.0016, 0.0132] | 0.0024 [−0.0029, 0.0108] | 0.0026 [−0.0049, 0.0111] |
| B | mean | 0.0063 [−0.0007, 0.0132] | 0.0004 [−0.0037, 0.0060] | −0.0001 [−0.0068, 0.0100] |
| B | median | 0.0046 [−0.0039, 0.0117] | 0.0015 [−0.0035, 0.0090] | 0.0001 [−0.0049, 0.0099] |

### Paired daily IC differences (mean [95% CI], one-sided p = share of bootstrap means ≤ 0)

| Difference | mean statistic | median statistic |
|---|---|---|
| A top_k off − A top_k 50 | −0.0188 [−0.0251, −0.0122], p 1.0000 | −0.0156 [−0.0207, −0.0105], p 1.0000 |
| B top_k off − B top_k 50 | −0.0049 [−0.0106, 0.0022], p 0.9035 | −0.0044 [−0.0099, 0.0021], p 0.8960 |
| A − B, both top_k off | 0.0013 [−0.0032, 0.0051], p 0.3135 | 0.0022 [−0.0019, 0.0064], p 0.1385 |

### Provenance
- Code: run_forecasts.py `--top-k-off`, run_topk.sh, explore_topk.py (2de0de7); calibration.py (518fc2b).
- Command: `bash experiments/e00_collapse/run_topk.sh` (tmux session e00_topk). It runs both forecasts,
  `calibration.py A_L512_s0_topkoff B_L512_s0_topkoff` and `explore_topk.py`.
- Outputs: `results/exploratory_topk.json`, `results/calibration.json`;
  `cache/e00/forecasts_{A,B}_L512_s0_topkoff.parquet`.
- Logs: `cache/e00/logs/run_topk.log`, `*_topkoff.log`, `calibration_topk.log`, `explore_topk.log`.
