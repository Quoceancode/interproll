"""Return preprocessing shared by every experiment.

FinText models were pretrained on daily excess returns in decimal units (0.01 = 1%),
winsorized to [-1, 1] (Rahimikia et al. 2025, Eq. 14). We feed both the FinText and the
generic Chronos checkpoints exactly this, so any difference comes from the weights.
"""

import numpy as np

CLIP_LOW = -1.0
CLIP_HIGH = 1.0

# A real daily return series in decimals has a median absolute move well under 0.1
# (typical large caps: ~0.01). The same data in percent has a median near 1.
# 0.1 sits far from both, so the check is robust to volatile stocks and crises.
MAX_MEDIAN_ABS_DECIMAL = 0.1


def check_decimal_returns(returns: np.ndarray, name: str = "returns") -> None:
    """Raise ValueError if `returns` don't look like daily decimal returns.

    Run this BEFORE clipping: clipping percent data to [-1, 1] would hide the mistake.
    Catches: percentages (x100), prices passed instead of returns, NaN/inf, empty input.
    """
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        raise ValueError(f"{name}: empty series")
    if not np.all(np.isfinite(r)):
        raise ValueError(f"{name}: contains NaN or inf; drop or mask them first")

    median_abs = float(np.median(np.abs(r)))
    if median_abs > MAX_MEDIAN_ABS_DECIMAL:
        if np.all(r > 0):
            hint = "all values positive: these look like prices, not returns"
        else:
            hint = "these look like percentages; divide by 100"
        raise ValueError(
            f"{name}: median |r| = {median_abs:.3g} > {MAX_MEDIAN_ABS_DECIMAL} ({hint})"
        )


def clip_returns(returns: np.ndarray) -> np.ndarray:
    """Winsorize to [-1, 1], matching FinText's preprocessing."""
    return np.clip(np.asarray(returns, dtype=float), CLIP_LOW, CLIP_HIGH)


def prepare_returns(returns: np.ndarray, name: str = "returns") -> np.ndarray:
    """Check units, then clip. The single entry point experiments should use."""
    check_decimal_returns(returns, name)
    return clip_returns(returns)
