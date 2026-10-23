"""Safetensors-only loading of the Chronos checkpoints we compare.

Security rules (CLAUDE.md / e00 plan): only allowlisted repos, pinned 40-char commit SHAs, only
config/generation_config/model.safetensors downloaded, and the snapshot is checked for pickle-capable
or code files before anything is loaded. trust_remote_code is never passed.
"""

from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO_ROOT / "cache" / "models"

KNOWN_REPOS = {"FinText/Chronos_Small_2023_US", "amazon/chronos-t5-small"}
ALLOW_PATTERNS = ["config.json", "generation_config.json", "model.safetensors"]
FORBIDDEN_SUFFIXES = (".bin", ".pt", ".pth", ".pkl", ".pickle", ".ckpt", ".py", ".pyc", ".so")


def check_snapshot(local_dir: Path) -> list[str]:
    """Raise if `local_dir` lacks model.safetensors or contains any pickle/code file. Returns file list."""
    files = sorted(
        str(p.relative_to(local_dir)) for p in local_dir.rglob("*")
        if p.is_file() and ".cache" not in p.relative_to(local_dir).parts  # skip hub download metadata
    )
    bad = [f for f in files if f.lower().endswith(FORBIDDEN_SUFFIXES)]
    if bad:
        raise RuntimeError(f"refusing to load {local_dir}: non-safetensors/code files present: {bad}")
    if "model.safetensors" not in files:
        raise RuntimeError(f"refusing to load {local_dir}: no model.safetensors (only {files})")
    return files


def download(repo_id: str, revision: str) -> Path:
    """Download only the allowlisted files at a pinned commit into cache/models/<repo>/<sha>."""
    from huggingface_hub import snapshot_download

    if repo_id not in KNOWN_REPOS:
        raise ValueError(f"{repo_id!r} is not an approved repo: {sorted(KNOWN_REPOS)}")
    if len(revision) != 40:
        raise ValueError("revision must be a full 40-character commit SHA")
    local_dir = MODEL_DIR / repo_id.replace("/", "__") / revision
    snapshot_download(repo_id=repo_id, revision=revision, allow_patterns=ALLOW_PATTERNS, local_dir=local_dir)
    return local_dir


def load_chronos(repo_id: str, revision: str, device: str = "cuda"):
    """Download (if needed), check, and load a ChronosPipeline in float32."""
    from chronos import ChronosPipeline

    local_dir = download(repo_id, revision)
    check_snapshot(local_dir)
    return ChronosPipeline.from_pretrained(
        str(local_dir), device_map=device, dtype=torch.float32, use_safetensors=True
    )
