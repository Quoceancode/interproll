"""e00 step 3b: daily excess-return panel from cached Yahoo prices + Fama-French RF.

Outputs:
  data/processed/e00/panel.parquet          long table: date, ticker, adjclose, ret, rf, exret
  data/raw/e00/missing_tickers.csv          every ticker with a data problem, and why
  experiments/e00_collapse/results/data_summary.json

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/build_panel.py
"""

import io
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
sys.path.insert(0, str(REPO / "src"))
from returns import prepare_returns  # noqa: E402
from universe import load_universe  # noqa: E402

CONFIG = json.loads((EXP / "config.json").read_text())
RAW = REPO / "data" / "raw" / "e00"
PROCESSED = REPO / "data" / "processed" / "e00"
RESULTS = EXP / "results"

FF_MEMBER = "F-F_Research_Data_Factors_daily.csv"
MIN_DAYS = 252  # fewer trading days than this in a 2021-06 -> now request means a truncated response
NAME_STOPWORDS = {"inc", "corp", "corporation", "co", "company", "the", "holdings", "holding", "group", "plc",
                  "ltd", "incorporated", "&", "and", "class", "cl", "a", "b", "com", "new", "sa", "nv", "llc"}


def load_rf() -> pd.Series:
    """Daily RF in decimals, indexed by date. Read in memory from the single CSV member (no extraction)."""
    with zipfile.ZipFile(RAW / "ff" / "F-F_Research_Data_Factors_daily_CSV.zip") as z:
        names = z.namelist()
        assert names == [FF_MEMBER], f"unexpected zip members: {names}"
        text = z.read(FF_MEMBER).decode("latin-1")
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 5 and re.fullmatch(r"\d{8}", parts[0]):  # data rows only; skips headers/footer
            rows.append((pd.Timestamp(parts[0]), float(parts[4]) / 100.0))  # file is in percent
    rf = pd.Series(dict(rows), name="rf").sort_index()
    assert rf.between(0.0, 0.001).all(), "daily RF outside [0, 0.1%]: unit problem?"
    return rf


def load_yahoo(symbol: str) -> tuple[pd.Series | None, dict]:
    """Adjusted close indexed by exchange-local date, plus Yahoo meta. None if not available."""
    path = RAW / "yahoo" / f"{symbol}.json"
    marker = path.with_name(path.name + ".status.json")
    if marker.exists() and not path.exists():
        return None, {"http_status": json.loads(marker.read_text())["http_status"]}
    chart = json.loads(path.read_text())["chart"]
    if chart.get("error") or not chart.get("result"):
        return None, {"error": str(chart.get("error"))}
    result = chart["result"][0]
    meta = result["meta"]
    timestamps = result.get("timestamp") or []
    adj = result["indicators"]["adjclose"][0]["adjclose"]
    # Yahoo timestamps are the session open in UTC; shift by the exchange offset to get the local date.
    offset = int(meta.get("gmtoffset", 0))
    dates = [pd.Timestamp(datetime.fromtimestamp(t + offset, tz=timezone.utc).date()) for t in timestamps]
    series = pd.Series(adj, index=dates, dtype=float, name=symbol)
    series = series[~series.index.duplicated(keep="last")].sort_index()
    return series, meta


def name_tokens(name: str) -> set[str]:
    words = re.findall(r"[a-z0-9&]+", name.lower())
    return {w for w in words if w not in NAME_STOPWORDS}


def build() -> None:
    rf = load_rf()
    universe = load_universe()
    eval_start = pd.Timestamp(CONFIG["eval_start"])
    min_first = pd.Timestamp(CONFIG["min_first_date"])

    frames, problems, prices_end = [], [], []
    for row in universe.itertuples():
        adj, meta = load_yahoo(row.yahoo_symbol)
        base = {"ticker": row.ticker, "yahoo_symbol": row.yahoo_symbol, "wiki_name": row.wiki_name}
        if row.ticker in CONFIG["exclude"]:  # hand-reviewed data errors, reason in config.json
            problems.append({**base, "reason": "excluded_data_error", "first_date": "", "last_date": "",
                             "n_days": 0, "note": CONFIG["exclude"][row.ticker]})
            continue
        if adj is None:
            problems.append({**base, "reason": "http_404" if meta.get("http_status") == 404 else "yahoo_error",
                             "first_date": "", "last_date": "", "n_days": 0, "note": json.dumps(meta)})
            continue

        n_null = int(adj.isna().sum())
        adj = adj.dropna()
        # Some responses are stubs: a few days of history and firstTradeDate 2026-07-17 for decades-old
        # listings (AVB, EA, EQR, QRVO, WBD on 2026-10-23; a one-off retry returned the same). Exclude.
        if len(adj) < MIN_DAYS:
            first_trade = datetime.fromtimestamp(meta.get("firstTradeDate") or 0, tz=timezone.utc).date()
            problems.append({**base, "reason": "yahoo_truncated",
                             "first_date": adj.index[0].date() if len(adj) else "",
                             "last_date": adj.index[-1].date() if len(adj) else "", "n_days": len(adj),
                             "note": f"yahoo firstTradeDate {first_trade}; name {meta.get('longName')}"})
            continue
        yahoo_name = meta.get("longName") or meta.get("shortName") or ""
        note = []
        if n_null:
            note.append(f"{n_null} null adjclose dropped")
        # Symbol reuse check: the Yahoo company name should share a word with the Wikipedia name.
        if yahoo_name and not (name_tokens(yahoo_name) & name_tokens(row.wiki_name)):
            problems.append({**base, "reason": "name_mismatch_check", "first_date": adj.index[0].date(),
                             "last_date": adj.index[-1].date(), "n_days": len(adj),
                             "note": f"yahoo name: {yahoo_name}"})

        frame = pd.DataFrame({"adjclose": adj})
        frame["ret"] = frame["adjclose"].pct_change()
        frame = frame.join(rf, how="inner").dropna(subset=["ret"])
        frame["exret"] = prepare_returns(frame["ret"].to_numpy() - frame["rf"].to_numpy(), name=row.ticker)
        frame["ticker"] = row.ticker
        frames.append(frame)
        prices_end.append(adj.index[-1])

        if adj.index[0] > min_first:
            problems.append({**base, "reason": "short_history", "first_date": adj.index[0].date(),
                             "last_date": adj.index[-1].date(), "n_days": len(adj), "note": "; ".join(note)})
        elif note:
            problems.append({**base, "reason": "data_note", "first_date": adj.index[0].date(),
                             "last_date": adj.index[-1].date(), "n_days": len(adj), "note": "; ".join(note)})

    panel = pd.concat(frames).rename_axis("date").reset_index()
    # Eval window ends at the last date that has both RF and (for most stocks) prices.
    window_end = min(rf.index[-1], pd.Series(prices_end).median())
    panel = panel[panel["date"] <= window_end]

    # Stocks whose data stop before the window end (delisted / acquired after 2023-12-31, if Yahoo kept them).
    last = panel.groupby("ticker")["date"].max()
    for ticker in last[last < window_end - pd.Timedelta(days=7)].index:
        sub = panel[panel["ticker"] == ticker]
        r = universe.set_index("ticker").loc[ticker]
        problems.append({"ticker": ticker, "yahoo_symbol": r.yahoo_symbol, "wiki_name": r.wiki_name,
                         "reason": "stops_before_end", "first_date": sub["date"].min().date(),
                         "last_date": sub["date"].max().date(), "n_days": len(sub), "note": ""})

    PROCESSED.mkdir(parents=True, exist_ok=True)
    columns = ["date", "ticker", "adjclose", "ret", "rf", "exret"]
    panel[columns].to_parquet(PROCESSED / "panel.parquet", index=False)
    problems_df = pd.DataFrame(problems).sort_values(["reason", "ticker"])
    problems_df.to_csv(RAW / "missing_tickers.csv", index=False)

    n_universe = len(universe)
    unusable = problems_df[problems_df["reason"].isin(
        ["http_404", "yahoo_error", "yahoo_truncated", "excluded_data_error"])]
    eval_rows = panel[panel["date"] >= eval_start]
    summary = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "universe_included": n_universe,
        "tickers_with_data": int(panel["ticker"].nunique()),
        "unusable_no_data": int(len(unusable)),
        "unusable_pct": round(100 * len(unusable) / n_universe, 2),
        "reason_counts": problems_df["reason"].value_counts().to_dict(),
        "rf_first": str(rf.index[0].date()), "rf_last": str(rf.index[-1].date()),
        "panel_first": str(panel["date"].min().date()), "window_end": str(window_end.date()),
        "eval_start": CONFIG["eval_start"],
        "eval_trading_days": int(eval_rows["date"].nunique()),
        "eval_stock_days": int(len(eval_rows)),
        "rf_daily_mean_eval": float(eval_rows.groupby("date")["rf"].first().mean()),
        "exret_median_abs": float(panel["exret"].abs().median()),
        "exret_std": float(panel["exret"].std()),
        "exret_min": float(panel["exret"].min()), "exret_max": float(panel["exret"].max()),
        "n_clipped": int((panel["ret"] - panel["rf"]).abs().gt(1).sum()),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "data_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print("\nProblems:\n" + problems_df.to_string(index=False))


if __name__ == "__main__":
    build()
