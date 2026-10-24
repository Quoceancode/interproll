"""e00 EXPLORATORY: calibration of the forecast sample distributions (not pre-registered).

For each run: coverage of the [q10, q90] and [q25, q75] sample intervals by the realised target, median sample std,
median (q90 - q10), median sample range in tokenizer bins (arms A/B only; scale = mean |context| as in Chronos
mean scaling), and the share of rows with any sample at the extreme bins (|sample| >= 15 x scale - 1 bin).

Run (from repo root):
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/calibration.py A_L512_s0 B_L512_s0 C_L512_s0
Writes results/calibration.json (merged with existing entries, keyed by run name).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
OUT = EXP / "results" / "calibration.json"
BIN = 30 / 4093  # MeanScaleUniformBins: 4093 centers on [-15, 15] in scaled units (model_checks: 0.007331)


def context_scale(context: int) -> pd.DataFrame:
    """mean |exret| over the `context` days ending at the origin, keyed by (target_date, ticker)."""
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    wide = panel.pivot(index="date", columns="ticker", values="exret").sort_index()
    scale = wide.abs().rolling(context, min_periods=context).mean().shift(1)  # row t+1 holds context through t
    out = scale.stack().rename("scale").reset_index().rename(columns={"date": "target_date"})
    out["target_date"] = pd.to_datetime(out["target_date"])
    return out


def calibrate(name: str) -> dict:
    arm, ctx_tag = name.split("_")[0], name.split("_")[1]
    frame = pd.read_parquet(REPO / "cache" / "e00" / f"forecasts_{name}.parquet")
    frame["target_date"] = pd.to_datetime(frame["target_date"])
    samples = frame[[f"s{i}" for i in range(20)]].to_numpy()
    target = frame["target"].to_numpy()
    row = {
        "n_forecasts": len(frame),
        "coverage_q10_q90": float(np.mean((target >= frame["q10"]) & (target <= frame["q90"]))),
        "coverage_q25_q75": float(np.mean((target >= frame["q25"]) & (target <= frame["q75"]))),
        "median_sample_std": float(frame["std"].median()),
        "median_q90_minus_q10": float((frame["q90"] - frame["q10"]).median()),
        "target_std": float(np.std(target)),
        "median_abs_target": float(np.median(np.abs(target))),
    }
    if arm in ("A", "B"):
        merged = frame[["target_date", "ticker"]].merge(context_scale(int(ctx_tag[1:])),
                                                        on=["target_date", "ticker"], how="left")
        scale = merged["scale"].to_numpy()
        range_bins = (samples.max(axis=1) - samples.min(axis=1)) / (BIN * scale)
        extreme = np.abs(samples) >= (15 - BIN) * scale[:, None]
        row.update({
            "median_sample_range_bins": float(np.nanmedian(range_bins)),
            "p99_sample_range_bins": float(np.nanquantile(range_bins, 0.99)),
            "median_abs_target_bins": float(np.nanmedian(np.abs(target) / (BIN * scale))),
            "share_rows_with_extreme_bin_sample": float(extreme.any(axis=1).mean()),
        })
    return row


def main(names: list[str]) -> None:
    results = json.loads(OUT.read_text()) if OUT.exists() else {}
    results["note"] = "EXPLORATORY, not pre-registered."
    for name in names:
        results[name] = calibrate(name)
        print(name, json.dumps(results[name]), flush=True)
    OUT.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
