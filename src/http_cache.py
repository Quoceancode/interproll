"""Download-once file cache for raw data (stdlib only).

Every download is written to disk the first time and read from disk afterwards, so
re-running an experiment never re-downloads (CLAUDE.md: never re-download in a loop).
Downloaded bytes are treated as data: callers parse them with json/csv/zipfile only.
"""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

# Descriptive UA with a contact URL (Wikimedia policy); fine for the other hosts too.
USER_AGENT = "interproll-research/0.1 (https://github.com/Quoceancode/interproll; academic research)"


class RateLimited(RuntimeError):
    """Raised on HTTP 429 so the caller stops instead of retrying in a loop."""


def fetch_cached(url: str, path: Path, min_interval_s: float = 0.0, timeout_s: float = 30.0) -> tuple[int, Path]:
    """Return (http_status, path). Downloads only if `path` doesn't exist yet.

    A 404 is cached as a small marker file `<path>.status.json` so we don't ask again.
    `min_interval_s` sleeps before a real network request (polite rate limiting).
    """
    marker = path.with_name(path.name + ".status.json")
    if path.exists():
        return 200, path
    if marker.exists():
        return int(json.loads(marker.read_text())["http_status"]), path

    path.parent.mkdir(parents=True, exist_ok=True)
    if min_interval_s > 0:
        time.sleep(min_interval_s)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            data = response.read()
    except urllib.error.HTTPError as err:
        if err.code == 429:
            raise RateLimited(f"HTTP 429 from {url}; stopping") from err
        if err.code == 404:
            marker.write_text(json.dumps({"http_status": 404, "url": url}))
            return 404, path
        raise
    # Write to a temp name first so an interrupted download never looks complete.
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(data)
    tmp.replace(path)
    return 200, path
