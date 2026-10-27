#!/usr/bin/env bash
# ANCHOR-FREE-REDRAW sweep (registered 2026-09-17 before any config or code, commit d61f2cf;
# docs/judge_v2_program.md "Registered 2026-09-17 (before running) - ANCHOR-FREE-REDRAW";
# plan docs/agents/plans/2026-09-17_anchor_free_redraw.md, steps 2 and 6).
#
# Five arms, STRICTLY SERIAL, in the registered order R1, R1c, R2, R3, R4; ALL FIVE RUN REGARDLESS of
# intermediate results (the registration's stopping rule forbids early stopping: a re-draw test that
# stops early selects its draws). Per arm: build -> 300-rep site null at the build's slice (256, dropTop 0,
# whiten false) -> anchor_free_readout.py vs the record (af/seed_42, site_null_af_s42.csv as control).
# At the end: tools/analysis/anchor_free_redraw.py --run (the registration's new readout; written by the
# engine-coder in parallel; if absent, "redraw readout absent" is logged and the chain exits 0).
#
# Resumable: every step is skipped when its output exists, so a killed session re-runs this script
# unchanged. A build is never retried once $R/<arm>.build.out exists (a failed build is the arm's result).
# A site null leaves $R/<arm>.sitenull.started before it runs; on resume, marker without CSV = "interrupted;
# restarting" (logged, sitenull_<arm>.out appended, nothing overwritten). Zero judge calls (every config is label-free, runBenchmark = false). Every tree produced
# here is STRUCTURAL EVIDENCE ONLY; nothing is promoted; R1 is not authorised for judging.
#
# Hygiene: one construction per process, one at a time, never concurrent with a site null or anything
# reading the pool; own -Dranking.db.path per arm (the record's af build wrote the default ratings.db,
# af.build.out L14: not repeated); reserved_test_queries.json is rewritten by EVERY build (one more reason
# the arms are serial); new snapshots go to the untracked snapshots.db, never snapshots_frozen.db.
#
# Usage (from the repo root, Git Bash):   bash tools/chains/anchor_free_redraw.sh [--dry-run]
#   --dry-run  prints every command the chain would run (with the skip decisions it would take) and exits 0.
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8

DRY=0
for a in "$@"; do case "$a" in --dry-run) DRY=1 ;; *) echo "unknown argument: $a" >&2; exit 2 ;; esac; done

POOL=p2dca21ab5f4ef3ae
A=experiment_results/anchorfree
R=$A/redraw
CFG=experiment_configs/anchorfree/redraw
CTRL_DIR=$A/af/seed_42
CTRL_CSV=$A/site_null_af_s42.csv
CHAIN_LOG=$R/chain.log
SLICE_DIM=256; DROP_TOP=0; WHITEN=false; REPS=300

[ "$DRY" = 1 ] || mkdir -p "$R"
log() { local m="[$(date +%H:%M:%S)] $*"; echo "$m"; [ "$DRY" = 1 ] || echo "$m" >> "$CHAIN_LOG"; }
run() {  # run <description> <stdout+stderr file> -- <cmd...>   (prints in --dry-run, executes otherwise)
  local desc=$1 outf=$2; shift 2; [ "$1" = "--" ] && shift
  if [ "$DRY" = 1 ]; then echo "  [would run] $desc  > $outf 2>&1"; echo "      $*"; return 0; fi
  "$@" > "$outf" 2>&1
}
run_append() {  # run_append <description> <stdout+stderr file> -- <cmd...>   (as run, but APPENDS: a restarted step keeps its earlier log)
  local desc=$1 outf=$2; shift 2; [ "$1" = "--" ] && shift
  if [ "$DRY" = 1 ]; then echo "  [would run] $desc  >> $outf 2>&1"; echo "      $*"; return 0; fi
  "$@" >> "$outf" 2>&1
}

# ---- arms: name  config  seed  ------------------------------------------------------------------------
# R1  af_clean_s42  af_s42.toml + reservedPoolFile (clean split, pool of record)
# R1c o0_clean_s42  h9_order/o0_s42.toml + reservedPoolFile (anchored clean-split control)
# R2  af_s137       seed = 137 (own split)        R3 af_s2048  seed = 2048 (own split)
# R4  af_s42_o1     constructionOrderShuffleSeed = 1 (order re-draw at the record's sample)
ARMS="af_clean_s42:42 o0_clean_s42:42 af_s137:137 af_s2048:2048 af_s42_o1:42"

# ---- guards ---------------------------------------------------------------------------------------------
# Non-daemon java.exe count (a build, a site null, or the gradlew launcher of either). The Gradle daemon
# itself is excluded; the launcher JVM ("-Dorg.gradle.appname=gradlew") is NOT, because it means a task
# is in flight somewhere in this checkout.
busy_jvm() {
  powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count" 2>/dev/null | tr -d '[:space:]'
}
wait_idle() {  # between steps: wait (safety net) rather than refuse
  [ "$DRY" = 1 ] && return 0
  local n; n=$(busy_jvm)
  while [ -n "$n" ] && [ "$n" != "0" ]; do log "$n non-daemon JVM(s) running; waiting 60 s"; sleep 60; n=$(busy_jvm); done
}

preflight() {
  log "PREFLIGHT pool guard: python tools/analysis/pool_guard.py --pool $POOL"
  if [ "$DRY" = 1 ]; then echo "  [would run] python tools/analysis/pool_guard.py --pool $POOL  (refuse on non-zero exit)"; else
    python tools/analysis/pool_guard.py --pool "$POOL" > "$R/pool_guard.out" 2>&1 || { log "PREFLIGHT pool guard FAILED (see $R/pool_guard.out); refusing"; exit 1; }
    log "PREFLIGHT pool guard OK: $(head -1 "$R/pool_guard.out")"
  fi
  for f in "$CTRL_DIR/dag_snapshots.jsonl" "$CTRL_CSV" experiment_configs/reserved_pool_frozen_p2dca.json; do
    [ -f "$f" ] || { log "PREFLIGHT missing $f; refusing"; exit 1; }
  done
  for e in $ARMS; do [ -f "$CFG/${e%%:*}.toml" ] || { log "PREFLIGHT missing config $CFG/${e%%:*}.toml; refusing"; exit 1; }; done
  local n; n=$(busy_jvm)
  if [ "$DRY" = 1 ]; then echo "  [would check] no non-daemon java.exe running (now: ${n:-?}); refuse otherwise"; else
    [ -n "$n" ] && [ "$n" != "0" ] && { log "PREFLIGHT $n non-daemon java.exe running (a build or site null is in flight); refusing to start"; exit 1; }
    log "PREFLIGHT no non-daemon JVM running"
  fi
  # Nothing destructive to back up: every output dir below is new (the record's af/ and its site null are read only).
  log "PREFLIGHT outputs are new dirs under $R (nothing of record is overwritten); ctrl $CTRL_DIR + $CTRL_CSV"
}

certified() {  # count certified sites in a site-null CSV: "<certified> <sites> <reps-set>"
  python - "$1" <<'EOF'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
print(sum(1 for r in rows if r.get("cert_site_p95", "").lower() in ("true", "1")), len(rows), "reps=" + ",".join(sorted({r.get("reps", "?") for r in rows})))
EOF
}

# ---- steps --------------------------------------------------------------------------------------------
build() {  # build <arm> <seed>
  local arm=$1 seed=$2
  local cfg=$CFG/$arm.toml out=$R/$arm.build.out dir=$R/$arm/seed_$seed
  if [ -f "$out" ]; then log "$arm BUILD attempted earlier ($out exists; $( [ -f "$dir/dag_snapshots.jsonl" ] && echo "snapshot present" || echo "no dag_snapshots.jsonl: the arm's result, C1 FAIL")); not retried"; return 0; fi
  wait_idle
  log "$arm BUILD start  config $cfg  ratings db $R/ratings_$arm.db"
  run "$arm build" "$out" -- ./gradlew.bat bootRun --console=plain -q --offline "-Dranking.db.path=$R/ratings_$arm.db" --args="--config $cfg"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  log "$arm BUILD exit $rc | $(grep -o 'Snapshot ID: [^ ]*' "$out" | tail -1) | $(grep -o '\[SPLIT-CLOSURE\] [0-9]* train item' "$out" | tail -1) | $(grep -o 'leaves=[0-9]*' "$out" | tail -1) | $(grep -o '\[SLICE\][^|]*' "$out" | head -1)"
  [ -f "$dir/dag_snapshots.jsonl" ] || log "$arm BUILD produced no dag_snapshots.jsonl: recorded as the arm's result (C1 FAIL), NOT retried"
  return 0
}

sitenull() {  # sitenull <arm>
  local arm=$1
  local csv=$R/site_null_$arm.csv bout=$R/$arm.build.out marker=$R/$arm.sitenull.started
  if [ -f "$csv" ]; then log "$arm SITENULL present ($csv): $(certified "$csv"), skipping"; return 0; fi
  if [ -f "$marker" ]; then log "$arm SITENULL was interrupted (marker $marker exists, no $csv); restarting (unattended: no operator decision available; sitenull_$arm.out is appended, nothing overwritten)"; fi
  local snap
  if [ "$DRY" = 1 ]; then snap=$( [ -f "$bout" ] && grep -o 'Snapshot ID: [^ ]*' "$bout" | tail -1 | cut -d' ' -f3 ); snap=${snap:-'<Snapshot ID parsed from '"$bout"'>'}; else
    snap=$(grep -o 'Snapshot ID: [^ ]*' "$bout" 2>/dev/null | tail -1 | cut -d' ' -f3)
    [ -z "$snap" ] && { log "$arm SITENULL no 'Snapshot ID:' in $bout (build failed or absent); arm UNDETERMINED for certification, continuing"; return 0; }
  fi
  wait_idle
  log "$arm SITENULL start snapshot $snap (sliceDim $SLICE_DIM dropTop $DROP_TOP whiten $WHITEN reps $REPS) -> $csv"
  [ "$DRY" = 1 ] || { echo "$(date +%Y-%m-%dT%H:%M:%S) snapshot $snap" >> "$marker"; }
  run_append "$arm site null" "$R/sitenull_$arm.out" -- ./gradlew.bat siteNull --console=plain -q --offline "-DsnapshotId=$snap" "-DsliceDim=$SLICE_DIM" "-DdropTop=$DROP_TOP" "-Dwhiten=$WHITEN" "-PnullReps=$REPS" "-DoutCsv=$csv"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  if [ -f "$csv" ]; then log "$arm SITENULL exit $rc -> $(certified "$csv")"; else log "$arm SITENULL exit $rc, no CSV written: arm UNDETERMINED (no partial null is read)"; fi
  return 0
}

readout() {  # readout <arm> <seed>
  local arm=$1 seed=$2
  local dir=$R/$arm/seed_$seed out=$R/anchor_free_${arm}_readout.txt csv=$R/site_null_$arm.csv
  if [ -f "$out" ]; then log "$arm READOUT present ($out), skipping"; return 0; fi
  if [ "$DRY" != 1 ] && [ ! -f "$dir/dag_snapshots.jsonl" ]; then log "$arm READOUT skipped: no build"; return 0; fi
  local sn=(); [ -f "$csv" ] && sn=(--site-null "$csv")
  [ "$DRY" = 1 ] && sn=(--site-null "$csv")
  log "$arm READOUT anchor_free_readout.py $dir vs $CTRL_DIR"
  run "$arm readout" "$R/readout_$arm.log" -- python tools/analysis/anchor_free_readout.py "$dir" "$CTRL_DIR" "${sn[@]}" --control-site-null "$CTRL_CSV" --out "$out"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  log "$arm READOUT exit $rc | $(grep -m1 'certified sites' "$out" 2>/dev/null | tr -s ' ' | cut -c1-140)"
  return 0
}

arm() { local name=$1 seed=$2; log "==== ARM $name (seed dir seed_$seed) ===="; build "$name" "$seed"; sitenull "$name"; readout "$name" "$seed"; }

# ---- main ---------------------------------------------------------------------------------------------
[ "$DRY" = 1 ] && echo "DRY RUN: nothing is executed, nothing is logged to $CHAIN_LOG"
log "CHAIN start (dry=$DRY) HEAD $(git rev-parse --short HEAD 2>/dev/null) | order R1 af_clean_s42, R1c o0_clean_s42, R2 af_s137, R3 af_s2048, R4 af_s42_o1 | all five run regardless"
preflight
for e in $ARMS; do arm "${e%%:*}" "${e#*:}"; done

log "==== REDRAW READOUT ===="
if [ -f tools/analysis/anchor_free_redraw.py ]; then
  wait_idle
  run "redraw readout" "$R/anchor_free_redraw.log" -- python tools/analysis/anchor_free_redraw.py --run
  rc=$?; [ "$DRY" = 1 ] || log "REDRAW READOUT exit $rc (log $R/anchor_free_redraw.log)"
else
  log "redraw readout absent (tools/analysis/anchor_free_redraw.py not found); run it by hand when it lands: python tools/analysis/anchor_free_redraw.py --run"
fi

log "SWEEP DONE"
if [ "$DRY" != 1 ]; then
  for e in $ARMS; do a=${e%%:*}; [ -f "$R/site_null_$a.csv" ] && log "$a: certified/sites $(certified "$R/site_null_$a.csv")" || log "$a: no site null"; done
  log "tracked files modified (must be only the two standing local edits .gitignore / config/application.yml):"; git status --short | grep -v '^??' | while read -r l; do log "  $l"; done
  log "snapshots_frozen.db sha256: $(sha256sum snapshots_frozen.db 2>/dev/null | cut -c1-16)"
fi
exit 0
