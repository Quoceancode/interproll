"""Unit checks for src/models.py (no downloads). Run: ~/venvs/tsfm-interp/bin/python tests/test_models.py"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from models import check_snapshot, download  # noqa: E402


def make_dir(files: list[str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for name in files:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes(b"x")
    return root


def expect_error(func, *args) -> None:
    try:
        func(*args)
    except (RuntimeError, ValueError):
        return
    raise AssertionError(f"{func.__name__}{args} did not raise")


def test_clean_snapshot_passes() -> None:
    files = check_snapshot(make_dir(["config.json", "generation_config.json", "model.safetensors"]))
    assert "model.safetensors" in files


def test_hub_metadata_ignored() -> None:
    check_snapshot(make_dir(["config.json", "model.safetensors", ".cache/huggingface/x.lock"]))


def test_bin_rejected() -> None:
    expect_error(check_snapshot, make_dir(["config.json", "model.safetensors", "pytorch_model.bin"]))


def test_code_rejected() -> None:
    expect_error(check_snapshot, make_dir(["config.json", "model.safetensors", "modeling_custom.py"]))


def test_missing_safetensors_rejected() -> None:
    expect_error(check_snapshot, make_dir(["config.json", "pytorch_model.bin"]))


def test_unknown_repo_rejected() -> None:
    expect_error(download, "someone/chronos-t5-smal1", "a" * 40)


def test_short_revision_rejected() -> None:
    expect_error(download, "amazon/chronos-t5-small", "main")


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"{len(tests)} passed")
