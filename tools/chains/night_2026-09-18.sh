#!/usr/bin/env bash
# Night 2026-09-18: item26 (running) -> ANCHOR-FREE-REDRAW chain (resumable) -> readout. Zero judge calls.
# Plan: docs/agents/plans/2026-09-18_night_schedule.md §4. Rule 7: the chain starts only when nothing reads the pool
# (item26 has exited) and no non-daemon java.exe is alive. Resumable: re-run after a kill; every step is skip-if-done.
# Launch (Git Bash, repo root):  (bash tools/chains/night_2026-09-18.sh > experiment_results/anchorfree/redraw/night_2026-09-18.out 2>&1 &)
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8
R=experiment_results/anchorfree/redraw
I26=experiment_results/x12_crossdomain/item26_pooled_run.log
I26OUT=experiment_results/x12_crossdomain/item26_pooled_outcome.txt
LOG=$R/night_2026-09-18.log
PIDF=$R/night_2026-09-18.pid
mkdir -p "$R"
log() { local m="[$(date +%H:%M:%S)] $*"; echo "$m"; echo "$m" >> "$LOG"; }
busy_jvm() {
  powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count" 2>/dev/null | tr -d '[:space:]'
}
# single instance
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then log "another night script is alive (pid $(cat "$PIDF")); refusing"; exit 1; fi
echo $$ > "$PIDF"
log "NIGHT start HEAD $(git rev-parse --short HEAD) | item26 log $I26 | chain tools/chains/anchor_free_redraw.sh"

# ---- 1. wait for item26 (its launcher appends 'exit <rc>' to the log when the process ends) --------------------
if [ -f "$I26" ] && grep -q '^exit' "$I26"; then
  log "item26 already ended: $(grep '^exit' "$I26" | tail -1)"
else
  log "waiting for item26: poll '^exit' in $I26 every 60 s (stage 4 ETA ~03:40, then power + LOAO)"
  while ! grep -q '^exit' "$I26" 2>/dev/null; do sleep 60; done
  log "item26 ended: $(grep '^exit' "$I26" | tail -1) | $(grep -c . "$I26") log lines"
fi
# belt and braces: the python process itself must be gone (it held the caches open)
while tasklist //FI "PID eq 20408" //NH 2>/dev/null | grep -qi python.exe; do log "PID 20408 still alive after the exit line; waiting 30 s"; sleep 30; done
if [ -f "$I26OUT" ]; then log "item26 outcome present: $I26OUT ($(wc -l < "$I26OUT") lines); NOT read here; morning: reviewer, then registrar"
else log "item26 outcome ABSENT ($(grep '^exit' "$I26" | tail -1)); morning: read the log; do NOT re-run blindly (write-once)"; fi

# ---- 2. no non-daemon JVM ----------------------------------------------------------------------------------------
n=$(busy_jvm); while [ -n "$n" ] && [ "$n" != "0" ]; do log "$n non-daemon java.exe alive; waiting 60 s"; sleep 60; n=$(busy_jvm); done
log "no non-daemon JVM; no python of record; CHAIN LAUNCH (pool readers are CLOSED from here to NIGHT DONE)"

# ---- 3. the registered chain (resumable; strictly serial; all five arms regardless) -----------------------------
bash tools/chains/anchor_free_redraw.sh >> "$R/chain_stdout.log" 2>&1
rc=$?
log "chain exit $rc"

# ---- 4. summary for the morning (no number of record is read here) ---------------------------------------------
if grep -q 'SWEEP DONE' "$R/chain.log"; then log "SWEEP DONE seen in $R/chain.log"; else log "SWEEP DONE NOT seen: chain interrupted; re-run this script (resumable)"; fi
for a in af_clean_s42 o0_clean_s42 af_s137 af_s2048 af_s42_o1; do
  if [ -f "$R/site_null_$a.csv" ]; then
    ro=ABSENT; [ -f "$R/anchor_free_${a}_readout.txt" ] && ro=present
    log "$a: site null present ($(grep -c . "$R/site_null_$a.csv") lines); readout $ro"
  else log "$a: site null ABSENT (UNDETERMINED unless the morning decides otherwise)"; fi
done
if [ -f "$R/anchor_free_redraw_outcome.txt" ]; then log "REDRAW outcome written: $R/anchor_free_redraw_outcome.txt"
else log "REDRAW outcome ABSENT: the chain's --run was refused or not reached; see $R/anchor_free_redraw.log; the morning declares --failed / --undetermined per arm"; fi
log "tracked changes: $(git status --short | grep -v '^??' | tr '\n' ' ')"
log "snapshots_frozen.db sha256: $(sha256sum snapshots_frozen.db 2>/dev/null | cut -c1-16)"
log "non-daemon JVMs now: $(busy_jvm) | python.exe: $(tasklist //FI 'IMAGENAME eq python.exe' //NH 2>/dev/null | grep -ci python.exe)"
log "NIGHT DONE; pool readers OPEN (W2)"
rm -f "$PIDF"
exit 0
