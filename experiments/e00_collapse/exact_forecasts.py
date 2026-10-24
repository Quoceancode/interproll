"""e00 EXPLORATORY: exact-distribution forecasts for arms A and B at L=512 (no sampling; not pre-registered).

For each context, one forward pass gives the first decoder step's logits over all 4096 tokens. Token id t decodes
to centers[clamp(t - 3, 0, 4092)] * scale, as in MeanScaleUniformBins.output_transform; scale = mean |context|.
Ids 0 (pad) and 1 (EOS) are special tokens.

Variants (value bins = ids 2..4095, special tokens excluded, probabilities renormalised over the kept bins):
  full_*   all value bins
  top50_*  the 50 value bins with the highest logits, renormalised (mimics top_k=50)
  *_mean   expectation of the decoded value; *_median the smallest value with CDF >= 0.5; *_mode the argmax bin.
Also stored per forecast: probability mass on pad and EOS under the raw softmax over all 4096 tokens.

Usage (from repo root, PY=~/venvs/tsfm-interp/bin/python):
  $PY experiments/e00_collapse/exact_forecasts.py --check   # exact vs many-sample means on a small sample
  $PY experiments/e00_collapse/exact_forecasts.py --arm A    # writes cache/e00/exact_A_L512.parquet
  $PY experiments/e00_collapse/exact_forecasts.py --analyze  # ICs, paired A-B -> results/exploratory_exact.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

EXP = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))
from analyze import CACHE, REPO, RESULTS, block_bootstrap_mean, daily_spearman  # noqa: E402
from run_forecasts import CONFIG, build_tasks, load_chronos  # noqa: E402

CONTEXT, TOP = 512, 50
BATCH = 256  # one forward pass per context (no sample expansion), so larger batches fit
VARIANTS = ["full_mean", "full_median", "full_mode", "top50_mean", "top50_median", "top50_mode"]


def first_step_logits(pipe, contexts: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Logits (n, 4096) of the first generated token, and the per-context scale (n,)."""
    token_ids, attention_mask, scale = pipe.tokenizer.context_input_transform(contexts)
    t5 = pipe.model.model
    device = pipe.model.device
    start = torch.full((len(contexts), 1), t5.config.decoder_start_token_id, dtype=torch.long, device=device)
    with torch.no_grad():
        out = t5(input_ids=token_ids.to(device), attention_mask=attention_mask.to(device), decoder_input_ids=start)
    return out.logits[:, 0, :].float(), scale.to(device)


def token_values(pipe, device) -> torch.Tensor:
    """Decoded value (in scaled units) of every token id 0..4095, exactly as output_transform maps it."""
    centers = pipe.tokenizer.centers.to(device)
    n_special = pipe.model.config.n_special_tokens
    ids = torch.arange(pipe.model.config.n_tokens, device=device)
    return centers[torch.clamp(ids - n_special - 1, 0, len(centers) - 1)]


def distribution_stats(probs: torch.Tensor, values: torch.Tensor) -> dict:
    """Mean, median and mode of a discrete distribution over values sorted ascending (probs rows sum to 1)."""
    cdf = probs.cumsum(dim=1)
    median_idx = torch.searchsorted(cdf, torch.full((len(probs), 1), 0.5, device=probs.device)).clamp(
        max=len(values) - 1)[:, 0]
    return {"mean": probs @ values, "median": values[median_idx], "mode": values[probs.argmax(dim=1)]}


def exact_batch(pipe, contexts: torch.Tensor) -> dict:
    logits, scale = first_step_logits(pipe, contexts)
    values_all = token_values(pipe, logits.device)
    n_special = pipe.model.config.n_special_tokens
    raw = torch.softmax(logits, dim=1)
    value_logits, values = logits[:, n_special:], values_all[n_special:]  # ids 2..4095, values ascending

    out = {"mass_pad": raw[:, pipe.model.config.pad_token_id], "mass_eos": raw[:, pipe.model.config.eos_token_id]}
    full = distribution_stats(torch.softmax(value_logits, dim=1), values)
    keep = torch.full_like(value_logits, float("-inf"))
    top_idx = value_logits.topk(TOP, dim=1).indices
    keep.scatter_(1, top_idx, value_logits.gather(1, top_idx))
    top = distribution_stats(torch.softmax(keep, dim=1), values)
    for name, stats in (("full", full), ("top50", top)):
        for stat, v in stats.items():
            out[f"{name}_{stat}"] = v * scale
    return {k: v.cpu().numpy() for k, v in out.items()}


def run_arm(arm: str) -> None:
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    tasks = build_tasks(panel, CONTEXT)
    pipe = load_chronos(CONFIG["models"][arm], CONFIG["revisions"][CONFIG["models"][arm]])
    contexts = tasks["ret_ctx"]  # arms A and B both forecast excess returns directly
    parts = [exact_batch(pipe, torch.from_numpy(contexts[i:i + BATCH])) for i in range(0, len(contexts), BATCH)]
    frame = pd.DataFrame({k: np.concatenate([p[k] for p in parts]) for k in parts[0]})
    frame.insert(0, "target", tasks["target"])
    frame.insert(0, "ticker", tasks["ticker"])
    frame.insert(0, "target_date", tasks["target_date"])
    frame.to_parquet(CACHE / f"exact_{arm}_L{CONTEXT}.parquet", index=False)
    print(f"wrote {len(frame)} exact forecasts for arm {arm}", flush=True)


def check(n_contexts: int = 64, n_samples: int = 4000, chunk: int = 500) -> None:
    """Exact means vs the average of many sampled forecasts, top_k off and top_k=50, on the first contexts of
    evenly spaced days. The sampler-equivalent exact mean keeps pad (decoded to the lowest bin) and drops EOS
    (suppressed by min_new_tokens), so it is what the sampler's average converges to."""
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    tasks = build_tasks(panel, CONTEXT)
    pick = np.linspace(0, len(tasks["target"]) - 1, n_contexts).astype(int)
    report = {"n_contexts": n_contexts, "n_samples": n_samples}
    for arm in "AB":
        pipe = load_chronos(CONFIG["models"][arm], CONFIG["revisions"][CONFIG["models"][arm]])
        ctx = torch.from_numpy(tasks["ret_ctx"][pick])
        logits, scale = first_step_logits(pipe, ctx)
        values = token_values(pipe, logits.device)
        exact = exact_batch(pipe, ctx)
        sampler_logits = logits.clone()
        sampler_logits[:, pipe.model.config.eos_token_id] = float("-inf")
        sampler_mean = {
            "off": (torch.softmax(sampler_logits, dim=1) @ values * scale).cpu().numpy(),
        }
        kth = sampler_logits.topk(TOP, dim=1).values[:, -1:]
        top_logits = sampler_logits.masked_fill(sampler_logits < kth, float("-inf"))
        sampler_mean["top50"] = (torch.softmax(top_logits, dim=1) @ values * scale).cpu().numpy()
        for mode, top_k in (("off", pipe.model.config.n_tokens), ("top50", TOP)):
            torch.manual_seed(0)
            draws = np.stack([
                np.concatenate([pipe.predict(ctx[i:i + 1], prediction_length=1, num_samples=chunk, top_k=top_k)
                                [0, :, 0].numpy() for _ in range(n_samples // chunk)])
                for i in range(n_contexts)])
            mc_mean, mc_se = draws.mean(axis=1), draws.std(axis=1, ddof=1) / np.sqrt(n_samples)
            z = (mc_mean - sampler_mean[mode]) / mc_se
            excl = exact["full_mean" if mode == "off" else "top50_mean"]
            report[f"{arm}_{mode}"] = {
                "max_abs_z_vs_sampler_equivalent_exact_mean": float(np.abs(z).max()),
                "share_abs_z_gt_2.58": float(np.mean(np.abs(z) > 2.58)),
                "mean_z": float(z.mean()),
                "median_abs_diff_exact_excl_special_vs_sampler_equivalent": float(
                    np.median(np.abs(excl - sampler_mean[mode]))),
                "median_mc_se": float(np.median(mc_se)),
            }
            print(arm, mode, report[f"{arm}_{mode}"], flush=True)
    (RESULTS / "exact_check.json").write_text(json.dumps(report, indent=2))


def analyze() -> None:
    frames = {arm: pd.read_parquet(CACHE / f"exact_{arm}_L{CONTEXT}.parquet") for arm in "AB"}
    assert frames["A"][["target_date", "ticker"]].equals(frames["B"][["target_date", "ticker"]])
    out: dict = {"note": "EXPLORATORY, not pre-registered. Exact first-step distribution, no sampling.",
                 "n_forecasts": len(frames["A"]), "ic": {}, "paired_A_minus_B": {}, "special_mass": {}}
    daily = {}
    for arm, frame in frames.items():
        frame["target_date"] = pd.to_datetime(frame["target_date"])
        for col in VARIANTS:
            daily[(arm, col)], n_undef = daily_spearman(frame, col, "target")
            m, lo, hi, p = block_bootstrap_mean(daily[(arm, col)])
            out["ic"][f"{arm}_{col}"] = {"mean": m, "lo": lo, "hi": hi, "p_le_zero": p, "days_undefined": n_undef}
        for col in ("mass_pad", "mass_eos"):
            v = frame[col].to_numpy()
            out["special_mass"][f"{arm}_{col}"] = {"median": float(np.median(v)), "p99": float(np.quantile(v, 0.99)),
                                                   "max": float(v.max())}
    for col in VARIANTS:
        m, lo, hi, p = block_bootstrap_mean(daily[("A", col)] - daily[("B", col)])
        out["paired_A_minus_B"][col] = {"mean": m, "lo": lo, "hi": hi, "p_le_zero": p}
    (RESULTS / "exploratory_exact.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=["A", "B"])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    elif args.analyze:
        analyze()
    else:
        run_arm(args.arm)


if __name__ == "__main__":
    main()
