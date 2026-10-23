"""e00 step 4b: how finely can each arm express a next-day return? (pre-registered, before any forecast)

Chronos mean-scales the context by s = mean|context| and quantizes to bins of width w (scaled units).
  Arm C (levels):  next-day return resolution ~= w * mean(P over context) / P_t   (normalisation cancels)
  Arms A/B (returns): resolution ~= w * mean(|r| over context), already in return units
Compared with realised |R_{t+1}| on every eval stock-day with a full context.
Writes results/armC_resolution.json and figs/armC_resolution_hist_L{L}.png (+ sidecar JSON).

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/armC_resolution.py
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
CONFIG = json.loads((EXP / "config.json").read_text())
# Read from the loaded tokenizer in model_checks.py (MeanScaleUniformBins, 4093 centers on [-15, 15]).
BIN_WIDTH = json.loads((EXP / "results" / "model_checks.json").read_text())["tokenizer"]["bin_width_scaled_units"]


def resolution_frame(panel: pd.DataFrame, context: int) -> pd.DataFrame:
    """One row per (origin date t, ticker) with a full context and a realised next-day return."""
    price = panel.pivot(index="date", columns="ticker", values="adjclose")
    exret = panel.pivot(index="date", columns="ticker", values="exret")
    ret = panel.pivot(index="date", columns="ticker", values="ret")

    # min_periods=context: only full windows, no padding (as in the forecast runs).
    width_levels = BIN_WIDTH * price.rolling(context, min_periods=context).mean() / price
    width_returns = BIN_WIDTH * exret.abs().rolling(context, min_periods=context).mean()
    next_abs_ret = ret.abs().shift(-1)  # realised |R_{t+1}|, aligned to origin t

    eval_targets = price.index[price.index >= pd.Timestamp(CONFIG["eval_start"])]
    origins = price.index[price.index.get_indexer(eval_targets) - 1]  # day before each target

    frame = pd.DataFrame({
        "width_levels": width_levels.loc[origins].stack(),
        "width_returns": width_returns.loc[origins].stack(),
        "next_abs_ret": next_abs_ret.loc[origins].stack(),
    }).dropna()
    return frame


def summarize(frame: pd.DataFrame) -> dict:
    q = [0.05, 0.25, 0.5, 0.75, 0.95]
    per_stock_median_move = frame.groupby(level="ticker")["next_abs_ret"].median()
    per_stock_width = frame.groupby(level="ticker")["width_levels"].median()
    return {
        "n_stock_days": int(len(frame)),
        "armC_width_quantiles": dict(zip(map(str, q), frame["width_levels"].quantile(q).round(5))),
        "armAB_width_quantiles": dict(zip(map(str, q), frame["width_returns"].quantile(q).round(7))),
        "realised_abs_ret_quantiles": dict(zip(map(str, q), frame["next_abs_ret"].quantile(q).round(5))),
        "armC_width_over_stock_median_move_quantiles": dict(
            zip(map(str, q), (per_stock_width / per_stock_median_move).quantile(q).round(3))),
        "armC_share_moves_smaller_than_one_bin": float((frame["next_abs_ret"] < frame["width_levels"]).mean()),
        "armC_share_moves_smaller_than_half_bin": float((frame["next_abs_ret"] < frame["width_levels"] / 2).mean()),
        "armAB_share_moves_smaller_than_one_bin": float((frame["next_abs_ret"] < frame["width_returns"]).mean()),
    }


def plot(frame: pd.DataFrame, context: int, figs: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.logspace(-6, 0, 80)
    ax.hist(frame["next_abs_ret"], bins=bins, alpha=0.5, label="realised |R(t+1)|")
    ax.hist(frame["width_levels"], bins=bins, alpha=0.6, label="arm C bin width (return units)")
    ax.hist(frame["width_returns"], bins=bins, alpha=0.6, label="arms A/B bin width (return units)")
    ax.set_xscale("log")
    ax.set_xlabel("return (log scale)")
    ax.set_ylabel("stock-days")
    ax.set_title(f"Chronos tokenizer resolution vs daily moves, context {context}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    name = f"armC_resolution_hist_L{context}"
    fig.savefig(figs / f"{name}.png", dpi=120)
    plt.close(fig)
    (figs / f"{name}.json").write_text(json.dumps({"script": "armC_resolution.py", "context": context,
                                                   "bin_width_scaled": BIN_WIDTH,
                                                   "eval_start": CONFIG["eval_start"]}, indent=2))


def main() -> None:
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    figs = EXP / "figs"
    figs.mkdir(exist_ok=True)
    report = {"bin_width_scaled_units": BIN_WIDTH}
    for context in CONFIG["contexts"]:
        frame = resolution_frame(panel, context)
        report[f"L{context}"] = summarize(frame)
        plot(frame, context, figs)
    (EXP / "results" / "armC_resolution.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
