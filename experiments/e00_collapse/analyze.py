"""e00 analysis: pre-registered collapse metrics and verdicts (research-log 2026-10-23, before any forecast).

Per run (arm x context x seed) and point statistic s in {mean, median}:
  D        median over days of cross-sectional std(f) / std(target); also time-series version
  Ties     median over days of the share of stocks whose f equals that day's modal value
  IC       daily Spearman(f, target); mean with 95% moving-block bootstrap CI (block 20, 2000 resamples)
  Spread   S = median sample std / median trailing-21d realised std (known at origin);
           informativeness = mean daily Spearman(sample std, |target|) with bootstrap CI
Verdicts:
  point collapse  = (D < 0.05 and IC CI includes 0) or Ties > 0.5
  arm collapsed   = point collapse under both mean and median at L=512 seed 0, seed 1 agreeing (else ambiguous)
  arm C collapsing only via Ties -> "inconclusive (tokenizer resolution)"
  spread collapse = S < 0.1 or spread-informativeness CI includes 0
  Holm correction over the 12 arm x statistic x context tests of IC > 0 (seed 0).
Outputs: results/metrics.csv, results/summary.json, figs/*.png (+ sidecar JSON).

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/analyze.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
CACHE = REPO / "cache" / "e00"
RESULTS, FIGS = EXP / "results", EXP / "figs"

D_MAX, TIES_MAX, S_MIN = 0.05, 0.5, 0.1
BLOCK, N_BOOT, SEED = 20, 2000, 0
STATS = ["mean", "median"]
RUNS = [(a, 512, s) for s in (0, 1) for a in "ABC"] + [(a, 252, 0) for a in "ABC"]


# ---------- statistics ----------

def block_bootstrap_mean(daily: np.ndarray) -> tuple[float, float, float, float]:
    """Mean of a daily series with a 95% moving-block bootstrap CI, and one-sided p for mean <= 0."""
    rng = np.random.default_rng(SEED)
    n = len(daily)
    n_blocks = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, n_blocks))
    idx = (starts[:, :, None] + np.arange(BLOCK)).reshape(N_BOOT, -1)[:, :n]
    means = daily[idx].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    p_le_zero = float(np.mean(means <= 0.0))
    return float(daily.mean()), float(lo), float(hi), p_le_zero


def daily_spearman(frame: pd.DataFrame, x: str, y: str) -> tuple[np.ndarray, int]:
    """Cross-sectional Spearman per day. All-tied days (undefined rank corr) count as 0 and are counted."""
    ranks = frame.groupby("target_date")[[x, y]].rank()
    ranks["target_date"] = frame["target_date"]
    corr = ranks.groupby("target_date").apply(lambda g: g[x].corr(g[y]), include_groups=False)
    n_undefined = int(corr.isna().sum())
    return corr.fillna(0.0).to_numpy(), n_undefined


def dispersion(frame: pd.DataFrame, col: str) -> tuple[float, float, np.ndarray]:
    """D (cross-sectional, per day -> median) and the time-series version (per stock -> median)."""
    by_day = frame.groupby("target_date")
    daily_ratio = (by_day[col].std() / by_day["target"].std()).to_numpy()
    by_stock = frame.groupby("ticker")
    ts_ratio = (by_stock[col].std() / by_stock["target"].std()).median()
    return float(np.median(daily_ratio)), float(ts_ratio), daily_ratio


def ties(frame: pd.DataFrame, col: str) -> float:
    """Median over days of the share of stocks whose forecast equals the day's most common value."""
    share = frame.groupby("target_date")[col].agg(lambda v: v.value_counts().iloc[0] / len(v))
    return float(share.median())


def trailing_vol(panel: pd.DataFrame) -> pd.DataFrame:
    """Trailing 21-day std of exret known at the origin, keyed by (target_date, ticker)."""
    wide = panel.pivot(index="date", columns="ticker", values="exret")
    vol_at_origin = wide.rolling(21, min_periods=21).std().shift(1)  # row t+1 holds vol up to t
    out = vol_at_origin.stack().rename("trailing_vol").reset_index()
    return out.rename(columns={"date": "target_date"})


# ---------- per-run metrics ----------

def run_metrics(frame: pd.DataFrame, years: list[int]) -> list[dict]:
    rows = []
    for stat in STATS:
        d, d_ts, _ = dispersion(frame, stat)
        ic_daily, n_undef = daily_spearman(frame, stat, "target")
        ic, lo, hi, p = block_bootstrap_mean(ic_daily)
        day_years = frame.groupby("target_date").size().index.year
        row = {"stat": stat, "D": d, "D_timeseries": d_ts, "ties": ties(frame, stat),
               "ic_mean": ic, "ic_lo": lo, "ic_hi": hi, "ic_p_le_zero": p, "ic_days_undefined": n_undef,
               "pooled_pearson": float(frame[stat].corr(frame["target"]))}
        for year in years:
            mask = np.asarray(day_years == year)
            if mask.sum() > 2 * BLOCK:
                y_ic, y_lo, y_hi, _ = block_bootstrap_mean(ic_daily[mask])
                row.update({f"ic_{year}": y_ic, f"ic_{year}_lo": y_lo, f"ic_{year}_hi": y_hi})
        row["point_collapse_D_IC"] = bool(d < D_MAX and lo <= 0.0 <= hi)
        row["point_collapse_ties"] = bool(row["ties"] > TIES_MAX)
        row["point_collapse"] = row["point_collapse_D_IC"] or row["point_collapse_ties"]
        rows.append(row)

    spread_daily, _ = daily_spearman(frame.assign(abs_target=frame["target"].abs()), "std", "abs_target")
    sp, sp_lo, sp_hi, _ = block_bootstrap_mean(spread_daily)
    s_ratio = float(frame["std"].median() / frame["trailing_vol"].median())
    for row in rows:
        row.update({"S": s_ratio, "spread_ic": sp, "spread_ic_lo": sp_lo, "spread_ic_hi": sp_hi,
                    "spread_collapse": bool(s_ratio < S_MIN or sp_lo <= 0.0 <= sp_hi)})
    return rows


def holm(pvalues: dict) -> dict:
    """Holm-adjusted p-values (step-down, monotone)."""
    keys = sorted(pvalues, key=pvalues.get)
    m, running, out = len(keys), 0.0, {}
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (m - i) * pvalues[k]))
        out[k] = running
    return out


# ---------- verdicts ----------

def arm_verdicts(metrics: pd.DataFrame) -> dict:
    out = {}
    for arm in "ABC":
        per_seed = {}
        for seed in (0, 1):
            sub = metrics[(metrics.arm == arm) & (metrics.context == 512) & (metrics.seed == seed)]
            both = bool(sub["point_collapse"].all())
            only_ties = bool(both and not sub["point_collapse_D_IC"].any())
            per_seed[seed] = (both, only_ties)
        (c0, ties0), (c1, _) = per_seed[0], per_seed[1]
        if c0 != c1:
            verdict = "ambiguous (seeds disagree)"
        elif c0 and arm == "C" and ties0:
            verdict = "inconclusive (tokenizer resolution)"
        else:
            verdict = "collapsed" if c0 else "not collapsed"
        l252 = metrics[(metrics.arm == arm) & (metrics.context == 252)]["point_collapse"].all()
        out[arm] = {"verdict_L512": verdict, "collapsed_L252": bool(l252),
                    "L512_vs_L252_agree": bool(c0 == l252)}
    return out


def stop_condition(verdicts: dict) -> str:
    a, b = verdicts["A"]["verdict_L512"], verdicts["B"]["verdict_L512"]
    if a == "collapsed" and b == "collapsed":
        return "STOP: arms A and B both collapsed at L=512 -> no e01; report."
    if a == "not collapsed" and b == "not collapsed":
        return "Neither A nor B collapsed -> report and wait for Chase."
    if a == "collapsed":
        return "A collapsed, B not -> contradicts premise; report and wait."
    if b == "collapsed":
        return "B collapsed, A not (consistent with H1); report and wait."
    return f"Ambiguous (A: {a}, B: {b}); report and wait."


def h2(metrics: pd.DataFrame) -> dict:
    """H2: arm C less collapsed than B — higher D and higher mean IC (L=512, seed 0), per statistic."""
    out = {}
    for stat in STATS:
        b = metrics.query("arm == 'B' and context == 512 and seed == 0 and stat == @stat").iloc[0]
        c = metrics.query("arm == 'C' and context == 512 and seed == 0 and stat == @stat").iloc[0]
        out[stat] = {"D_B": b.D, "D_C": c.D, "IC_B": [b.ic_mean, b.ic_lo, b.ic_hi],
                     "IC_C": [c.ic_mean, c.ic_lo, c.ic_hi],
                     "C_higher_D": bool(c.D > b.D), "C_higher_IC": bool(c.ic_mean > b.ic_mean),
                     "IC_CIs_overlap": bool(not (c.ic_lo > b.ic_hi or b.ic_lo > c.ic_hi))}
    return out


# ---------- figures ----------

def save_fig(fig, name: str, meta: dict) -> None:
    fig.tight_layout()
    fig.savefig(FIGS / f"{name}.png", dpi=120)
    plt.close(fig)
    (FIGS / f"{name}.json").write_text(json.dumps({"script": "analyze.py", **meta}, indent=2))


def figures(frames: dict) -> None:
    colors = {"A": "tab:blue", "B": "tab:orange", "C": "tab:green"}
    for context in (512, 252):
        fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
        for ax, stat in zip(axes, STATS):
            for arm in "ABC":
                _, _, daily = dispersion(frames[(arm, context, 0)], stat)
                ax.plot(np.sort(daily), np.linspace(0, 1, len(daily)), color=colors[arm], label=f"arm {arm}")
            ax.axvline(D_MAX, color="k", ls="--", lw=1, label="D = 0.05")
            ax.set_xscale("symlog", linthresh=1e-3)
            ax.set_xlabel(f"daily std(forecast)/std(realised), {stat}")
            ax.set_title(f"Dispersion ratio CDF, L={context}")
        axes[0].set_ylabel("share of days")
        axes[0].legend(fontsize=8)
        save_fig(fig, f"dispersion_D_by_arm_L{context}", {"context": context, "seed": 0})

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax, stat in zip(axes, STATS):
        for arm in "ABC":
            frame = frames[(arm, 512, 0)]
            ic, _ = daily_spearman(frame, stat, "target")
            dates = np.sort(frame["target_date"].unique())
            ax.plot(dates, pd.Series(ic).rolling(60).mean(), color=colors[arm], label=f"arm {arm}")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_title(f"Rolling 60-day mean daily rank IC ({stat}), L=512")
    axes[0].legend(fontsize=8)
    fig.autofmt_xdate()
    save_fig(fig, "ic_timeseries_by_arm_L512", {"context": 512, "seed": 0, "window_days": 60})

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.linspace(-0.1, 0.1, 201)
    ax.hist(frames[("A", 512, 0)]["target"], bins=bins, histtype="step", color="k", label="realised")
    for arm in "ABC":
        ax.hist(frames[(arm, 512, 0)]["median"], bins=bins, histtype="step", color=colors[arm],
                label=f"arm {arm} median forecast")
    ax.set_yscale("log")
    ax.set_xlabel("excess return")
    ax.legend(fontsize=8)
    ax.set_title("Forecast vs realised distribution, L=512")
    save_fig(fig, "forecast_vs_realised_hist_L512", {"context": 512, "seed": 0})

    fig, ax = plt.subplots(figsize=(7, 4))
    for arm in "ABC":
        frame = frames[(arm, 512, 0)]
        deciles = pd.qcut(frame["std"].rank(method="first"), 10, labels=False)
        binned = frame.assign(abs_t=frame["target"].abs()).groupby(deciles)[["std", "abs_t"]].mean()
        ax.plot(binned["std"], binned["abs_t"], "o-", color=colors[arm], label=f"arm {arm}")
    ax.set_xscale("log")
    ax.set_xlabel("forecast sample std (decile mean)")
    ax.set_ylabel("mean realised |excess return|")
    ax.legend(fontsize=8)
    ax.set_title("Spread vs realised |return|, L=512")
    save_fig(fig, "spread_vs_absret_L512", {"context": 512, "seed": 0, "bins": "deciles of sample std"})


# ---------- main ----------

def main() -> None:
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    vol = trailing_vol(panel)
    frames, rows = {}, []
    for arm, context, seed in RUNS:
        path = CACHE / f"forecasts_{arm}_L{context}_s{seed}.parquet"
        frame = pd.read_parquet(path, columns=["target_date", "ticker", "target", "mean", "median", "std"])
        frame = frame.merge(vol, on=["target_date", "ticker"], how="left")
        frames[(arm, context, seed)] = frame
        years = sorted(frame["target_date"].dt.year.unique())
        for row in run_metrics(frame, years):
            rows.append({"arm": arm, "context": context, "seed": seed, "n_forecasts": len(frame), **row})
        print(f"done {arm} L{context} s{seed}", flush=True)
    metrics = pd.DataFrame(rows)

    seed0 = metrics[metrics.seed == 0]
    adjusted = holm({f"{r.arm}_L{r.context}_{r.stat}": r.ic_p_le_zero for r in seed0.itertuples()})
    metrics["ic_p_holm"] = [adjusted.get(f"{r.arm}_L{r.context}_{r.stat}", np.nan) for r in metrics.itertuples()]

    verdicts = arm_verdicts(metrics)
    summary = {"verdicts": verdicts, "stop_condition": stop_condition(verdicts), "H2_C_vs_B": h2(metrics),
               "thresholds": {"D": D_MAX, "ties": TIES_MAX, "S": S_MIN, "block": BLOCK, "n_boot": N_BOOT},
               "ic_context_note": "daily cross-sectional rank ICs of ~0.01-0.03 are typically economically meaningful"}
    RESULTS.mkdir(exist_ok=True)
    FIGS.mkdir(exist_ok=True)
    metrics.to_csv(RESULTS / "metrics.csv", index=False)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    figures(frames)
    cols = ["arm", "context", "seed", "stat", "D", "ties", "ic_mean", "ic_lo", "ic_hi", "ic_p_holm",
            "point_collapse", "S", "spread_ic", "spread_ic_lo", "spread_ic_hi", "spread_collapse"]
    with pd.option_context("display.width", 250, "display.float_format", "{:.4f}".format):
        print(metrics[cols].to_string(index=False))
    print(json.dumps(summary, indent=2, default=float))


if __name__ == "__main__":
    main()
