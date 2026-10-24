"""e00 EXPLORATORY follow-ups (NOT pre-registered; written after seeing analyze.py results, 2026-10-23).

1. Paired IC differences A-B, A-C, B-C (L=512 seed 0 and L=252 seed 0): daily IC_x - IC_y, same moving-block
   bootstrap as analyze.py. Tests whether "A beats B" holds day by day, not just via non-overlapping CIs.
2. Raw-input baselines (CLAUDE.md): daily Spearman IC of simple features known at the origin t:
   -r_t (1-day reversal), -(r_{t-4..t}) (5-day reversal), r_{t-251..t-21} (12-1 momentum).
   Spread baseline: Spearman(trailing 21d vol, |r_{t+1}|) vs each arm's spread informativeness.
3. How much of each arm's point forecast is 1-day reversal: mean daily Spearman(f, -r_t).
Outputs: results/exploratory.json.

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/explore.py
"""

import json

import numpy as np
import pandas as pd

from analyze import CACHE, REPO, RESULTS, block_bootstrap_mean, daily_spearman, trailing_vol


def load_run(arm: str, context: int, seed: int) -> pd.DataFrame:
    cols = ["target_date", "ticker", "target", "mean", "median", "std"]
    frame = pd.read_parquet(CACHE / f"forecasts_{arm}_L{context}_s{seed}.parquet", columns=cols)
    frame["target_date"] = pd.to_datetime(frame["target_date"])
    return frame.sort_values(["target_date", "ticker"]).reset_index(drop=True)


def origin_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Features known at origin t, keyed by target_date = next trading day t+1 (row shift, no look-ahead)."""
    wide = panel.pivot(index="date", columns="ticker", values="exret").sort_index()
    feats = {
        "rev1": -wide,                                              # -r_t
        "rev5": -wide.rolling(5, min_periods=5).sum(),              # -(r_{t-4} + ... + r_t)
        "mom12_1": wide.shift(21).rolling(231, min_periods=231).sum(),  # r_{t-251} .. r_{t-21}
    }
    out = []
    for name, f in feats.items():
        shifted = f.shift(1)  # row t+1 holds the value computed through t
        out.append(shifted.stack().rename(name))
    merged = pd.concat(out, axis=1).reset_index()
    return merged.rename(columns={"date": "target_date"})


def summarise(daily: np.ndarray) -> dict:
    m, lo, hi, p = block_bootstrap_mean(daily)
    return {"mean": m, "lo": lo, "hi": hi, "p_le_zero": p}


def main() -> None:
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    panel["date"] = pd.to_datetime(panel["date"])
    feats = origin_features(panel).merge(trailing_vol(panel), on=["target_date", "ticker"], how="left")
    out: dict = {"note": "EXPLORATORY, not pre-registered; written after seeing the pre-registered results."}

    for context in (512, 252):
        runs = {arm: load_run(arm, context, 0) for arm in "ABC"}
        base = runs["A"][["target_date", "ticker", "target"]].merge(feats, on=["target_date", "ticker"], how="left")
        key = f"L{context}_s0"
        out[key] = {"baselines": {}, "paired_diff": {}, "corr_with_rev1": {}, "n_rows": len(base)}

        for name in ("rev1", "rev5", "mom12_1"):
            sub = base.dropna(subset=[name])
            daily, _ = daily_spearman(sub, name, "target")
            out[key]["baselines"][f"ic_{name}"] = summarise(daily) | {"n_rows": len(sub)}
        base["absret"] = base["target"].abs()
        sub = base.dropna(subset=["trailing_vol"])
        daily, _ = daily_spearman(sub, "trailing_vol", "absret")
        out[key]["baselines"]["spread_ic_trailing_vol"] = summarise(daily)

        daily_ic = {}
        for arm, frame in runs.items():
            assert frame[["target_date", "ticker"]].equals(runs["A"][["target_date", "ticker"]])
            for stat in ("mean", "median"):
                daily_ic[(arm, stat)], _ = daily_spearman(frame, stat, "target")
            with_rev = frame.assign(rev1=base["rev1"].to_numpy()).dropna(subset=["rev1"])
            corr, _ = daily_spearman(with_rev, "mean", "rev1")
            out[key]["corr_with_rev1"][arm] = float(corr.mean())

        for x, y in (("A", "B"), ("A", "C"), ("B", "C")):
            for stat in ("mean", "median"):
                out[key]["paired_diff"][f"{x}-{y}_{stat}"] = summarise(daily_ic[(x, stat)] - daily_ic[(y, stat)])
        print(f"done {key}")

    path = RESULTS / "exploratory.json"
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
