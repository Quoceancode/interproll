"""e00 step 5: next-day forecasts for arms A/B/C.

Arms (config.json "models"):
  A  FinText/Chronos_Small_2023_US on excess returns
  B  amazon/chronos-t5-small on excess returns
  C  amazon/chronos-t5-small on a total-return index (the L most recent adjclose levels, normalised to 1 at the
     window start); each sample P_hat -> P_hat / P_t - 1 - RF(t+1), clipped to [-1, 1]
Every task = (origin t, ticker) with a full context ending at t and a realised target at t+1 in the eval window.

Usage (from repo root):
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/run_forecasts.py --bench 1000
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/run_forecasts.py --arm A --context 512 --seed 0
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
sys.path.insert(0, str(REPO / "src"))
from models import load_chronos  # noqa: E402

CONFIG = json.loads((EXP / "config.json").read_text())
OUT = REPO / "cache" / "e00"
QUANTILES = [0.1, 0.25, 0.75, 0.9]


def build_tasks(panel: pd.DataFrame, context: int) -> dict:
    """Arrays for every eval task: contexts for both input types, target, and RF at t+1."""
    exret = panel.pivot(index="date", columns="ticker", values="exret")
    price = panel.pivot(index="date", columns="ticker", values="adjclose")
    rf = panel.groupby("date")["rf"].first()
    dates = exret.index
    target_pos = np.flatnonzero(dates >= pd.Timestamp(CONFIG["eval_start"]))

    exret_np, price_np = exret.to_numpy(), price.to_numpy()
    rows = {"target_date": [], "ticker": [], "ret_ctx": [], "lvl_ctx": [], "target": [], "rf_next": [],
            "p_last": []}
    for pos in target_pos:
        origin = pos - 1
        start = origin - context + 1
        if start < 0:
            continue
        ret_window = exret_np[start:origin + 1]  # (context, n_tickers)
        lvl_window = price_np[start:origin + 1]
        ok = (~np.isnan(ret_window).any(axis=0) & ~np.isnan(lvl_window).any(axis=0)
              & ~np.isnan(exret_np[pos]))
        for j in np.flatnonzero(ok):
            lvl = lvl_window[:, j] / lvl_window[0, j]
            rows["target_date"].append(dates[pos])
            rows["ticker"].append(exret.columns[j])
            rows["ret_ctx"].append(ret_window[:, j])
            rows["lvl_ctx"].append(lvl)
            rows["target"].append(exret_np[pos, j])
            rows["rf_next"].append(rf.iloc[pos])
            rows["p_last"].append(lvl[-1])
    return {k: (np.asarray(v, dtype=np.float32) if k in ("ret_ctx", "lvl_ctx", "target", "rf_next", "p_last")
                else v) for k, v in rows.items()}


def forecast(pipe, contexts: np.ndarray, batch_size: int, num_samples: int) -> np.ndarray:
    """Samples of the next value for each context, shape (n, num_samples)."""
    out = []
    for i in range(0, len(contexts), batch_size):
        batch = torch.from_numpy(contexts[i:i + batch_size])
        out.append(pipe.predict(batch, prediction_length=1, num_samples=num_samples)[:, :, 0].numpy())
    return np.concatenate(out)


def to_excess_returns(arm: str, samples: np.ndarray, tasks: dict, idx: np.ndarray) -> np.ndarray:
    if arm in ("A", "B"):
        return samples
    implied = samples / tasks["p_last"][idx, None] - 1.0 - tasks["rf_next"][idx, None]
    return np.clip(implied, -1.0, 1.0)


def run(arm: str, context: int, seed: int, tasks: dict, pipe, limit: int | None = None) -> pd.DataFrame:
    torch.manual_seed(seed)
    n = len(tasks["target"]) if limit is None else min(limit, len(tasks["target"]))
    idx = np.arange(n)
    contexts = tasks["lvl_ctx" if arm == "C" else "ret_ctx"][idx]
    samples = to_excess_returns(arm, forecast(pipe, contexts, CONFIG["batch_size"], CONFIG["num_samples"]),
                                tasks, idx).astype(np.float32)
    frame = pd.DataFrame({"target_date": tasks["target_date"][:n], "ticker": tasks["ticker"][:n],
                          "target": tasks["target"][idx], "mean": samples.mean(axis=1),
                          "median": np.median(samples, axis=1), "std": samples.std(axis=1)})
    for q, values in zip(QUANTILES, np.quantile(samples, QUANTILES, axis=1)):
        frame[f"q{int(q * 100)}"] = values
    for k in range(samples.shape[1]):
        frame[f"s{k}"] = samples[:, k]
    return frame


def bench(n: int) -> None:
    """Time n forecasts per arm at each context; extrapolate to the full 9-run plan."""
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    pipes = {repo: load_chronos(repo, CONFIG["revisions"][repo]) for repo in set(CONFIG["models"].values())}
    runs_per_context = {512: 3 * 2, 252: 3 * 1}  # arms x seeds, as pre-registered
    report = {"n": n, "batch_size": CONFIG["batch_size"], "num_samples": CONFIG["num_samples"],
              "gpu": torch.cuda.get_device_name(0)}
    total_s = 0.0
    for context in CONFIG["contexts"]:
        tasks = build_tasks(panel, context)
        n_tasks = len(tasks["target"])
        for arm in ("A", "B", "C"):
            pipe = pipes[CONFIG["models"][arm]]
            run(arm, context, 0, tasks, pipe, limit=CONFIG["batch_size"])  # warm-up (CUDA init, kernels)
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            run(arm, context, 0, tasks, pipe, limit=n)
            torch.cuda.synchronize()
            per_series = (time.perf_counter() - t0) / n
            report[f"{arm}_L{context}"] = {"series_per_s": round(1 / per_series, 1), "tasks": n_tasks,
                                           "est_min_one_run": round(per_series * n_tasks / 60, 1)}
        mean_per_series = np.mean([1 / report[f"{a}_L{context}"]["series_per_s"] for a in "ABC"])
        total_s += mean_per_series * n_tasks * runs_per_context[context]
    report["est_total_min_all_9_runs"] = round(total_s / 60, 1)
    (EXP / "results" / "bench.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", type=int)
    parser.add_argument("--arm", choices=["A", "B", "C"])
    parser.add_argument("--context", type=int, choices=CONFIG["contexts"])
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.bench:
        bench(args.bench)
        return
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    tasks = build_tasks(panel, args.context)
    pipe = load_chronos(CONFIG["models"][args.arm], CONFIG["revisions"][CONFIG["models"][args.arm]])
    frame = run(args.arm, args.context, args.seed, tasks, pipe)
    OUT.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(OUT / f"forecasts_{args.arm}_L{args.context}_s{args.seed}.parquet", index=False)
    print(f"wrote {len(frame)} forecasts")


if __name__ == "__main__":
    main()
