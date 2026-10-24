#!/usr/bin/env bash
# e00 EXPLORATORY exact-distribution forecasts: arms A and B at L=512, then analysis (meant to run inside tmux).
# Full logs in cache/e00/logs/; cache/e00/logs/EXACT_DONE is written at the end.
set -u
cd "$(dirname "$0")/../.."
PY=~/venvs/tsfm-interp/bin/python
LOGS=cache/e00/logs
for arm in A B; do
  echo "$(date -Is) start exact_$arm" | tee -a "$LOGS/run_exact.log"
  "$PY" -u experiments/e00_collapse/exact_forecasts.py --arm "$arm" > "$LOGS/exact_$arm.log" 2>&1
  echo "$(date -Is) end exact_$arm exit=$?" | tee -a "$LOGS/run_exact.log"
done
"$PY" -u experiments/e00_collapse/exact_forecasts.py --analyze > "$LOGS/exact_analyze.log" 2>&1
echo "$(date -Is) analyze exit=$?" | tee -a "$LOGS/run_exact.log"
date -Is > "$LOGS/EXACT_DONE.tmp" && mv "$LOGS/EXACT_DONE.tmp" "$LOGS/EXACT_DONE"
