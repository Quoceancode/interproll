"""e00 EXPLORATORY top_k sensitivity (not pre-registered): arms A and B, L=512, seed 0, top_k off vs default.

Applies the same pre-registered metric functions (analyze.run_metrics: D, Ties, IC + CI, S, spread IC) to the
top_k-off runs and to the matching main runs, plus the paired daily IC difference (top_k off - default) per arm
and statistic, and A-B under top_k off. Writes results/exploratory_topk.json.

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/explore_topk.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import CACHE, REPO, RESULTS, block_bootstrap_mean, daily_spearman, run_metrics, trailing_vol  # noqa: E402

COLS = ["target_date", "ticker", "target", "mean", "median", "std"]


def load(name: str, vol: pd.DataFrame) -> pd.DataFrame:
    frame = pd.read_parquet(CACHE / f"forecasts_{name}.parquet", columns=COLS)
    frame = frame.merge(vol, on=["target_date", "ticker"], how="left")
    return frame.sort_values(["target_date", "ticker"]).reset_index(drop=True)


def paired(x: pd.DataFrame, y: pd.DataFrame, stat: str) -> dict:
    assert x[["target_date", "ticker"]].equals(y[["target_date", "ticker"]])
    dx, _ = daily_spearman(x, stat, "target")
    dy, _ = daily_spearman(y, stat, "target")
    m, lo, hi, p = block_bootstrap_mean(dx - dy)
    return {"mean": m, "lo": lo, "hi": hi, "p_le_zero": p}


def main() -> None:
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    vol = trailing_vol(panel)
    names = ["A_L512_s0", "B_L512_s0", "A_L512_s0_topkoff", "B_L512_s0_topkoff"]
    frames = {n: load(n, vol) for n in names}
    out: dict = {"note": "EXPLORATORY, not pre-registered. top_k off = top_k set to the full vocabulary (4096).",
                 "metrics": {}, "paired_ic_diff": {}}
    for name, frame in frames.items():
        years = sorted(frame["target_date"].dt.year.unique())
        out["metrics"][name] = run_metrics(frame, years)
    for stat in ("mean", "median"):
        for arm in "AB":
            out["paired_ic_diff"][f"{arm}_topkoff-{arm}_default_{stat}"] = paired(
                frames[f"{arm}_L512_s0_topkoff"], frames[f"{arm}_L512_s0"], stat)
        out["paired_ic_diff"][f"A-B_topkoff_{stat}"] = paired(
            frames["A_L512_s0_topkoff"], frames["B_L512_s0_topkoff"], stat)
    path = RESULTS / "exploratory_topk.json"
    path.write_text(json.dumps(out, indent=2, default=float))
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
