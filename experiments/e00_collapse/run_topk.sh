#!/usr/bin/env bash
# e00 EXPLORATORY top_k sensitivity: arms A and B, L=512, seed 0, top_k disabled (meant to run inside tmux).
# Same logging as run_all.sh; outputs cache/e00/forecasts_{A,B}_L512_s0_topkoff.parquet, then calibration +
# analysis (explore_topk.py). cache/e00/logs/TOPK_DONE is written at the end.
set -u
cd "$(dirname "$0")/../.."
PY=~/venvs/tsfm-interp/bin/python
LOGS=cache/e00/logs
mkdir -p "$LOGS"

for arm in A B; do
  name="${arm}_L512_s0_topkoff"
  if [ -f "cache/e00/forecasts_${name}.parquet" ]; then
    echo "$(date -Is) skip $name (output exists)" | tee -a "$LOGS/run_topk.log"
    continue
  fi
  echo "$(date -Is) start $name" | tee -a "$LOGS/run_topk.log"
  "$PY" -u experiments/e00_collapse/run_forecasts.py --arm "$arm" --context 512 --seed 0 --top-k-off \
    > "$LOGS/$name.log" 2>&1
  echo "$(date -Is) end $name exit=$?" | tee -a "$LOGS/run_topk.log"
done

"$PY" -u experiments/e00_collapse/calibration.py A_L512_s0_topkoff B_L512_s0_topkoff > "$LOGS/calibration_topk.log" 2>&1
echo "$(date -Is) calibration exit=$?" | tee -a "$LOGS/run_topk.log"
"$PY" -u experiments/e00_collapse/explore_topk.py > "$LOGS/explore_topk.log" 2>&1
echo "$(date -Is) explore_topk exit=$?" | tee -a "$LOGS/run_topk.log"
date -Is > "$LOGS/TOPK_DONE.tmp" && mv "$LOGS/TOPK_DONE.tmp" "$LOGS/TOPK_DONE"  # atomic: watchers never see it empty
