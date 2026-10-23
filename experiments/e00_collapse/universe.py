"""e00: S&P 500 constituents as of 2023-12-31 from two sources, and their diff.

Primary: fja05680/sp500 point-in-time CSV (one row per change date; take the last row <= the date).
Cross-check: Wikipedia constituents table at revision 1192789360 (2023-12-31T09:32:39Z).
Rule: a ticker is in the universe only if both sources list it; one-source tickers are reported.

Run (from repo root): ~/venvs/tsfm-interp/bin/python experiments/e00_collapse/universe.py
"""

import csv
import json
import re
from pathlib import Path

import pandas as pd

EXP = Path(__file__).resolve().parent
REPO = EXP.parents[1]
CONFIG = json.loads((EXP / "config.json").read_text())
RAW = REPO / "data" / "raw" / "e00"
RESULTS = EXP / "results"

# Wikipedia rows mark the ticker with an exchange template, e.g. {{NyseSymbol|MMM}}, {{NasdaqSymbol|AAPL}},
# or {{BZX link|CBOE}} (Cboe's own exchange).
SYMBOL_TEMPLATE = re.compile(
    r"\{\{\s*(?:(?:Nyse|Nasdaq|Cboe|BZX)Symbol|BZX link)\s*\|\s*([A-Za-z0-9.\-]+)\s*\}\}", re.I)


def fja_tickers(as_of: str) -> tuple[str, set[str]]:
    """Tickers in the last fja05680 row dated <= as_of. Returns (row_date, tickers)."""
    commit = CONFIG["constituents"]["primary"]["commit"]
    path = RAW / "constituents" / f"fja05680_{commit[:8]}.csv"
    best_date, best = "", ""
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if best_date < row["date"] <= as_of:  # ISO dates compare correctly as strings
                best_date, best = row["date"], row["tickers"]
    return best_date, {t.strip() for t in best.split(",") if t.strip()}


def wikipedia_rows() -> list[dict[str, str]]:
    """(ticker, security name) for each row of the FIRST wikitable (the constituents table)."""
    revid = CONFIG["constituents"]["crosscheck"]["revid"]
    page = json.loads((RAW / "constituents" / f"wikipedia_rev{revid}.json").read_text())
    revision = page["query"]["pages"][0]["revisions"][0]
    assert revision["timestamp"] == CONFIG["constituents"]["crosscheck"]["rev_timestamp"]
    text = revision["slots"]["main"]["content"]

    table = text.split("{|", 2)[1]  # first table only; later tables list index changes
    rows = []
    for raw_row in table.split("\n|-")[1:]:
        match = SYMBOL_TEMPLATE.search(raw_row)
        if not match:
            continue
        # Second cell is the security name, usually a wiki link [[Target|Name]] or [[Name]].
        name_match = re.search(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", raw_row[match.end():])
        rows.append({"ticker": match.group(1).upper(), "name": name_match.group(1) if name_match else ""})
    return rows


def yahoo_symbol(ticker: str) -> str:
    """Yahoo writes share classes with a dash: BRK.B -> BRK-B."""
    return ticker.replace(".", "-")


def build_universe() -> pd.DataFrame:
    as_of = CONFIG["universe_date"]
    fja_date, fja = fja_tickers(as_of)
    wiki = {r["ticker"]: r["name"] for r in wikipedia_rows()}
    drop = set(CONFIG["constituents"]["drop_duplicate_share_classes"])

    rows = []
    for ticker in sorted(fja | set(wiki)):
        in_fja, in_wiki = ticker in fja, ticker in wiki
        if ticker in drop:
            status = "dropped_share_class"
        elif in_fja and in_wiki:
            status = "included"
        else:
            status = "one_source_only"
        rows.append({"ticker": ticker, "yahoo_symbol": yahoo_symbol(ticker), "in_fja": in_fja,
                     "in_wikipedia": in_wiki, "wiki_name": wiki.get(ticker, ""), "status": status})
    universe = pd.DataFrame(rows)
    print(f"fja05680 row {fja_date}: {len(fja)} tickers | Wikipedia rev: {len(wiki)} tickers")
    print(universe["status"].value_counts().to_string())
    return universe


def load_universe(include_all: bool = False) -> pd.DataFrame:
    """Universe table written by this script; by default only status == 'included'."""
    universe = pd.read_csv(RAW / "universe.csv")
    return universe if include_all else universe[universe["status"] == "included"]


if __name__ == "__main__":
    universe = build_universe()
    universe.to_csv(RAW / "universe.csv", index=False)
    RESULTS.mkdir(exist_ok=True)
    diff = universe[universe["status"] != "included"]
    diff.to_csv(RESULTS / "universe_diff.csv", index=False)
    print("\nNot included:\n" + diff.to_string(index=False))
