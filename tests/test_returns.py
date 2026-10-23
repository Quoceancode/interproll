"""Unit checks for src/returns.py. Run: ~/venvs/tsfm-interp/bin/python tests/test_returns.py

Plain asserts (no pytest dependency); exits non-zero on the first failure.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from returns import check_decimal_returns, clip_returns, prepare_returns  # noqa: E402

rng = np.random.default_rng(0)
# Roughly realistic daily returns: 2% vol, fat tails via Student-t.
DECIMAL = 0.02 * rng.standard_t(df=4, size=2000)


def expect_error(series: np.ndarray, fragment: str) -> None:
    try:
        check_decimal_returns(series)
    except ValueError as err:
        assert fragment in str(err), f"wrong message: {err}"
        return
    raise AssertionError(f"expected ValueError containing {fragment!r}")


def test_decimal_passes() -> None:
    check_decimal_returns(DECIMAL)


def test_volatile_decimal_passes() -> None:
    # A very volatile stock (8% daily vol) is still clearly decimal.
    check_decimal_returns(4 * DECIMAL)


def test_percent_fails() -> None:
    expect_error(100 * DECIMAL, "percentages")


def test_prices_fail() -> None:
    prices = 100 * np.exp(np.cumsum(DECIMAL))
    expect_error(prices, "prices")


def test_nan_fails() -> None:
    bad = DECIMAL.copy()
    bad[5] = np.nan
    expect_error(bad, "NaN")


def test_empty_fails() -> None:
    expect_error(np.array([]), "empty")


def test_clip_bounds() -> None:
    clipped = clip_returns(np.array([-3.0, -0.5, 0.0, 0.5, 2.0]))
    assert clipped.tolist() == [-1.0, -0.5, 0.0, 0.5, 1.0]


def test_prepare_checks_before_clipping() -> None:
    # Percent data must be rejected, not silently clipped into [-1, 1].
    try:
        prepare_returns(100 * DECIMAL)
    except ValueError:
        return
    raise AssertionError("prepare_returns accepted percentage input")


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"{len(tests)} passed")
