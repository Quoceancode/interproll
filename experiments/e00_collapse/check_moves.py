"""e00: wrong-company / bad-data screen on the panel (read-only; does not modify the panel).

Flags (the PARA lesson: a reused symbol can silently stitch two companies together):
  1. stock-days with |excess return| > 40%
  2. consecutive-day price-level ratio > 5x (either direction)
  3. series starting later than the first trading days of the request window
Writes experiments/e00_collapse/results/move_screen.csv for Chase to verify by hand.

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/check_moves.py
"""

from pathlib import Path

import pandas as pd

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]

BIG_MOVE = 0.40
LEVEL_RATIO = 5.0
EXPECTED_FIRST = pd.Timestamp("2021-06-07")  # first week of the 2021-06-01 request start


def screen(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["ticker", "date"]).copy()
    grouped = panel.groupby("ticker")
    panel["price_before"] = grouped["adjclose"].shift(1)
    panel["price_next"] = grouped["adjclose"].shift(-1)
    # Level ratio between consecutive days, >= 1 whichever way the price moved.
    ratio = panel["adjclose"] / panel["price_before"]
    panel["level_ratio"] = ratio.where(ratio >= 1, 1 / ratio)

    flags = []
    big = panel[panel["exret"].abs() > BIG_MOVE].assign(flag="abs_exret_gt_40pct")
    jump = panel[panel["level_ratio"] > LEVEL_RATIO].assign(flag="level_jump_gt_5x")
    flags += [big, jump]

    first = grouped["date"].min()
    late = first[first > EXPECTED_FIRST]
    late_rows = panel[panel.set_index(["ticker", "date"]).index.isin(list(late.items()))]
    flags.append(late_rows.assign(flag="late_first_date"))

    columns = ["flag", "ticker", "date", "price_before", "adjclose", "price_next", "ret", "exret", "level_ratio"]
    out = pd.concat(flags)[columns].rename(columns={"adjclose": "price_on_day"})
    return out.sort_values(["flag", "ticker", "date"])


if __name__ == "__main__":
    panel = pd.read_parquet(REPO / "data" / "processed" / "e00" / "panel.parquet")
    result = screen(panel)
    result.to_csv(EXP / "results" / "move_screen.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:.4f}".format):
        print(result.to_string(index=False))
    print(f"\n{len(result)} flagged rows: " + result["flag"].value_counts().to_dict().__repr__())
