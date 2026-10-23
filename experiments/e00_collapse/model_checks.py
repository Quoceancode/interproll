"""e00 step 4a: download both models (safetensors only, pinned) and run sanity checks.

Checks: snapshot file allowlist + sha256 of weights; configs equal field by field; a constant input
gives a near-constant forecast; arm C conversion on a synthetic random walk gives returns of the right scale.
Writes results/model_checks.json.

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/model_checks.py
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
sys.path.insert(0, str(REPO / "src"))
from models import check_snapshot, download, load_chronos  # noqa: E402

CONFIG = json.loads((EXP / "config.json").read_text())
# Fields expected to differ between checkpoints that share an architecture.
IGNORED_CONFIG_FIELDS = {"_name_or_path", "transformers_version", "classifier_dropout"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def compare_configs(a: dict, b: dict) -> dict:
    """Fields that differ, excluding ones that are expected to (names, library versions)."""
    keys = (set(a) | set(b)) - IGNORED_CONFIG_FIELDS
    return {k: (a.get(k), b.get(k)) for k in sorted(keys) if a.get(k) != b.get(k)}


def main() -> None:
    torch.manual_seed(0)
    report: dict = {"models": {}}
    pipelines = {}
    configs = {}
    for repo_id, revision in CONFIG["revisions"].items():
        local_dir = download(repo_id, revision)
        files = check_snapshot(local_dir)
        configs[repo_id] = json.loads((local_dir / "config.json").read_text())
        report["models"][repo_id] = {"revision": revision, "files": files,
                                     "model_safetensors_sha256": sha256(local_dir / "model.safetensors")}
        pipelines[repo_id] = load_chronos(repo_id, revision)
        print(f"loaded {repo_id}@{revision[:8]}: {files}")

    fin, gen = CONFIG["models"]["A"], CONFIG["models"]["B"]
    report["config_differences"] = compare_configs(configs[fin], configs[gen])
    report["ignored_config_fields"] = {k: (configs[fin].get(k), configs[gen].get(k)) for k in IGNORED_CONFIG_FIELDS}

    # Constant input: every token is the same bin, so a sane model should forecast ~the same value.
    constant = torch.full((1, 512), 0.001)
    report["constant_input"] = {}
    for repo_id, pipe in pipelines.items():
        samples = pipe.predict(constant, prediction_length=1, num_samples=20)[0, :, 0].numpy()
        report["constant_input"][repo_id] = {"input": 0.001, "median": float(np.median(samples)),
                                             "min": float(samples.min()), "max": float(samples.max())}

    # Arm C round trip: random-walk total-return index -> generic model -> implied next-day return.
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0, 0.015, size=(64, 512))
    index = np.cumprod(1.0 + returns, axis=1)
    samples = pipelines[gen].predict(torch.tensor(index, dtype=torch.float32), prediction_length=1,
                                     num_samples=20)[:, :, 0].numpy()
    implied = samples / index[:, -1:] - 1.0
    report["armC_roundtrip"] = {"true_daily_std": 0.015,
                                "median_abs_implied_return": float(np.median(np.abs(implied))),
                                "std_implied_return": float(implied.std()),
                                "share_exactly_zero": float(np.mean(implied == 0.0))}

    tokenizer = pipelines[gen].tokenizer
    centers = tokenizer.centers.numpy()
    report["tokenizer"] = {"class": type(tokenizer).__name__, "n_centers": int(len(centers)),
                           "center_min": float(centers.min()), "center_max": float(centers.max()),
                           "bin_width_scaled_units": float(np.median(np.diff(centers)))}

    (EXP / "results").mkdir(exist_ok=True)
    (EXP / "results" / "model_checks.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
