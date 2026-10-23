#!/usr/bin/env bash
# e00: run all 9 pre-registered forecast runs one after another (meant to run inside tmux).
# Each run's full stdout/stderr goes to cache/e00/logs/<run>.log; its forecasts are written to
# cache/e00/forecasts_<arm>_L<context>_s<seed>.parquet as soon as that run finishes.
# Re-running skips runs whose parquet already exists. cache/e00/logs/ALL_DONE is written at the end.
set -u
cd "$(dirname "$0")/../.."
PY=~/venvs/tsfm-interp/bin/python
LOGS=cache/e00/logs
mkdir -p "$LOGS"

# Main context first (seed 0, then seed 1), robustness context last.
RUNS="A:512:0 B:512:0 C:512:0 A:512:1 B:512:1 C:512:1 A:252:0 B:252:0 C:252:0"

for spec in $RUNS; do
  IFS=: read -r arm ctx seed <<<"$spec"
  name="${arm}_L${ctx}_s${seed}"
  if [ -f "cache/e00/forecasts_${name}.parquet" ]; then
    echo "$(date -Is) skip $name (output exists)" | tee -a "$LOGS/run_all.log"
    continue
  fi
  echo "$(date -Is) start $name" | tee -a "$LOGS/run_all.log"
  "$PY" -u experiments/e00_collapse/run_forecasts.py --arm "$arm" --context "$ctx" --seed "$seed" \
    > "$LOGS/$name.log" 2>&1
  status=$?
  echo "$(date -Is) end $name exit=$status" | tee -a "$LOGS/run_all.log"
done

echo "$(date -Is) all runs attempted" | tee -a "$LOGS/run_all.log"
ls cache/e00/forecasts_*.parquet 2>/dev/null | wc -l > "$LOGS/ALL_DONE"  # number of finished runs (of 9)
