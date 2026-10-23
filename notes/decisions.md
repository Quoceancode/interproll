# Decisions

_One line per decision: date — decision — reason. Revisit, don't silently change._

- 2026-10-23 — WSL2 over native Windows — interp tooling and research repos are Linux-first; matches cloud/MATS setups.
- 2026-10-23 — nnsight over TransformerLens — Chronos's custom tokenizer and experimental T5 support in TL; nnsight wraps any PyTorch model.
- 2026-10-23 — Start with Chronos (T5) family — prior SAE work exists on Chronos-T5-Large (comparable), and FinText released finance-pretrained Chronos variants.
- 2026-10-23 — Free daily data (yfinance/Stooq) — enough for probing; no need for the 94-country research set.
- 2026-10-23 — certifi pinned at 2026.10.19 (not the same-day 2026.10.23) — has the eMudhra CA key-compromise fix (GHSA-6q48-6c7w-9gw2) and passes the release-age rule. Do not go below it.
- 2026-10-23 — python-dateutil held at 2.9.0.post0 (downgraded from 3.0.0) — 3.0.0 has no matching GitHub release, so it's unverified; only pandas needs it (>=2.9.0). Revisit when a verified 3.0.0 exists.
- 2026-10-23 — Keep httpx2 / httpcore2 2.16.0 — verified genuine Pydantic packages (github.com/pydantic/httpx2); required by huggingface_hub 2.3.0.
