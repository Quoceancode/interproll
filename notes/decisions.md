# Decisions

_One line per decision: date — decision — reason. Revisit, don't silently change._

- 2026-10-23 — WSL2 over native Windows — interp tooling and research repos are Linux-first; matches cloud/MATS setups.
- 2026-10-23 — nnsight over TransformerLens — Chronos's custom tokenizer and experimental T5 support in TL; nnsight wraps any PyTorch model.
- 2026-10-23 — Start with Chronos (T5) family — prior SAE work exists on Chronos-T5-Large (comparable), and FinText released finance-pretrained Chronos variants.
- 2026-10-23 — Free daily data (yfinance/Stooq) — enough for probing; no need for the 94-country research set.
