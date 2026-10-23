"""e00 step 3a: download raw data (cached; safe to re-run).

Usage (from repo root):
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/fetch_data.py constituents
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/fetch_data.py rf
  ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/fetch_data.py prices
"""

import json
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from http_cache import fetch_cached  # noqa: E402

EXP = Path(__file__).resolve().parent
CONFIG = json.loads((EXP / "config.json").read_text())
RAW = REPO / "data" / "raw" / "e00"


def fja_path() -> Path:
    commit = CONFIG["constituents"]["primary"]["commit"]
    return RAW / "constituents" / f"fja05680_{commit[:8]}.csv"


def wiki_path() -> Path:
    revid = CONFIG["constituents"]["crosscheck"]["revid"]
    return RAW / "constituents" / f"wikipedia_rev{revid}.json"


def rf_path() -> Path:
    return RAW / "ff" / "F-F_Research_Data_Factors_daily_CSV.zip"


def yahoo_path(symbol: str) -> Path:
    return RAW / "yahoo" / f"{symbol}.json"


def fetch_constituents() -> None:
    primary = CONFIG["constituents"]["primary"]
    file_url = urllib.parse.quote(primary["file"])
    url = f"https://raw.githubusercontent.com/fja05680/sp500/{primary['commit']}/{file_url}"
    print(fetch_cached(url, fja_path()))

    revid = CONFIG["constituents"]["crosscheck"]["revid"]
    url = ("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content|timestamp"
           f"&rvslots=main&revids={revid}&format=json&formatversion=2")
    print(fetch_cached(url, wiki_path()))


def fetch_rf() -> None:
    print(fetch_cached(CONFIG["risk_free"]["url"], rf_path()))


def fetch_prices(symbols: list[str]) -> None:
    """One Yahoo request per symbol, >= 1 s apart; 404s are cached and logged later."""
    start = datetime.fromisoformat(CONFIG["prices"]["start"]).replace(tzinfo=timezone.utc)
    period1 = int(start.timestamp())
    period2 = int(datetime.now(timezone.utc).timestamp())
    interval = CONFIG["prices"]["min_interval_s"]
    n_404 = 0
    for i, symbol in enumerate(symbols, 1):
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}"
               f"?period1={period1}&period2={period2}&interval=1d&events=div%2Csplit")
        status, _ = fetch_cached(url, yahoo_path(symbol), min_interval_s=interval)
        n_404 += status == 404
        if i % 50 == 0:
            print(f"{i}/{len(symbols)} done, {n_404} not found so far", flush=True)
    print(f"prices: {len(symbols)} symbols, {n_404} not found (HTTP 404)")


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "constituents":
        fetch_constituents()
    elif stage == "rf":
        fetch_rf()
    elif stage == "prices":
        from universe import load_universe  # needs constituents parsed first
        fetch_prices(sorted(load_universe()["yahoo_symbol"]))
    else:
        raise SystemExit(f"unknown stage {stage!r}")
