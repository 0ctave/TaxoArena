#!/usr/bin/env bash
# K-SELECTION sweep (registered 2026-09-19 before any code or call, commit 8fde7fa;
# docs/judge_v2_program.md "Registered 2026-09-19 (before any code or call) - K-SELECTION", L8224-L8390;
# plan docs/agents/plans/2026-09-18_reframing_and_next.md S2 R2 / S5; engine flag merged 967a936).
#
# Four arms, STRICTLY SERIAL, in the registered order I2, R1', R2', R3'; ALL FOUR RUN REGARDLESS of
# intermediate results (no early stopping: I2's verdict is LOGGED, never used to skip a primed arm; the
# registration's "nothing primed is read" is a READING rule the readout applies, not a build rule).
#   I2   af_clean_s42_inert  build only (key ABSENT), then the inertness check: leaf membership of the new
#        tree vs REDRAW R1 (experiment_results/anchorfree/redraw/af_clean_s42/seed_42, snapshot
#        20260917_201353): same leaf count and the same multiset of leaf member sets (queryIds per leaf;
#        node ids may permute) -> INERT / NOT INERT (tools/analysis/k_selection_inert.py). No site null
#        (the certified 14 of 69 are read from the EXISTING site_null_af_clean_s42.csv).
#   R1'  af_clean_s42_k105   build -> 300-rep site null (256 / dropTop 0 / whiten false) -> readout
#   R2'  af_s137_k105        idem            R3'  af_s2048_k105   idem
# Each primed config = its REDRAW base + EXACTLY ONE added active key line proposalAcceptMultiplier = 1.05
# (verified by comment-stripped diff before this chain was written: outputDir + that line, nothing else).
# At the end: tools/analysis/k_selection_readout.py --run if it exists (the registration's readout over the
# primed arms vs the record and vs their unprimed REDRAW arms; anchor_free_redraw.py has no --arms/--unprimed
# flag and its min-pair regex does not read the primed arms' `bar_eff=` reason field); if absent, logged.
#
# Resumable: every step is skipped when its output exists, so a killed session re-runs this script unchanged.
# A build is never retried once $R/<arm>.build.out exists (a failed build is the arm's result: UNDETERMINED).
# A site null leaves $R/<arm>.sitenull.started before it runs; marker without CSV on resume = "interrupted;
# restarting" (logged; sitenull_<arm>.out appended, nothing overwritten). Zero judge calls (every config is
# label-free, runBenchmark = false). Every tree produced here is STRUCTURAL EVIDENCE ONLY; nothing is promoted;
# no arm is authorised for judging.
#
# Hygiene (CONTEXT.md S4 rules 6, 7): one construction per process, one at a time, never concurrent with a
# site null or with anything reading the pool (the chain REFUSES to start while a non-daemon java.exe or a
# python.exe running this repo's tools/analysis is alive, and WAITS on either between steps); own
# -Dranking.db.path per arm; reserved_test_queries.json is rewritten by EVERY build (one more reason the arms
# are serial); new snapshots go to the untracked snapshots.db, never snapshots_frozen.db;
# frozen_triples_*_MAIN.json is restored from HEAD after every build if a build touched it.
#
# Usage (from the repo root, Git Bash):   bash tools/chains/k_selection.sh [--dry-run]
#   --dry-run  prints every command the chain would run (with the skip decisions it would take) and exits 0.
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8

DRY=0
for a in "$@"; do case "$a" in --dry-run) DRY=1 ;; *) echo "unknown argument: $a" >&2; exit 2 ;; esac; done

POOL=p2dca21ab5f4ef3ae
MERGE_COMMIT=967a936               # the K-SELECTION flag merge; must be an ancestor of HEAD
A=experiment_results/anchorfree
REDRAW=$A/redraw                   # the unprimed arms (R1, R2, R3) and their nulls
R=$REDRAW/kselect                  # this sweep's outputs
CFG=experiment_configs/anchorfree/redraw/kselect
CTRL_DIR=$A/af/seed_42             # the record (anchor_free_readout.py control)
CTRL_CSV=$A/site_null_af_s42.csv
R1_DIR=$REDRAW/af_clean_s42/seed_42
R1_CSV=$REDRAW/site_null_af_clean_s42.csv
CHAIN_LOG=$R/chain.log
SLICE_DIM=256; DROP_TOP=0; WHITEN=false; REPS=300

[ "$DRY" = 1 ] || mkdir -p "$R"
log() { local m="[$(date +%H:%M:%S)] $*"; echo "$m"; [ "$DRY" = 1 ] || echo "$m" >> "$CHAIN_LOG"; }
run() {  # run <description> <stdout+stderr file> -- <cmd...>   (prints in --dry-run, executes otherwise)
  local desc=$1 outf=$2; shift 2; [ "$1" = "--" ] && shift
  if [ "$DRY" = 1 ]; then echo "  [would run] $desc  > $outf 2>&1"; echo "      $*"; return 0; fi
  "$@" > "$outf" 2>&1
}
run_append() {  # as run, but APPENDS (a restarted step keeps its earlier log)
  local desc=$1 outf=$2; shift 2; [ "$1" = "--" ] && shift
  if [ "$DRY" = 1 ]; then echo "  [would run] $desc  >> $outf 2>&1"; echo "      $*"; return 0; fi
  "$@" >> "$outf" 2>&1
}

# ---- arms: name:config:seed:kind  (name = output dir under $R; config = $CFG/<config>.toml) ------------------
#   I2  i2               af_clean_s42_inert  42    inert   (build + identity check; no null, no readout)
#   R1' af_clean_s42_k105 af_clean_s42_k105  42    primed  (pool of record by reservedPoolFile; the only clean arm)
#   R2' af_s137_k105      af_s137_k105       137   primed  (own pool pd610c9ad05255f16; identity only, never purity as clean)
#   R3' af_s2048_k105     af_s2048_k105      2048  primed  (own pool p19d9f473b5a610a0; idem)
ARMS="i2:af_clean_s42_inert:42:inert af_clean_s42_k105:af_clean_s42_k105:42:primed af_s137_k105:af_s137_k105:137:primed af_s2048_k105:af_s2048_k105:2048:primed"
PRIMED="af_clean_s42_k105 af_s137_k105 af_s2048_k105"
unprimed_of() { case "$1" in af_clean_s42_k105) echo af_clean_s42 ;; af_s137_k105) echo af_s137 ;; af_s2048_k105) echo af_s2048 ;; *) echo "" ;; esac; }

# ---- guards -----------------------------------------------------------------------------------------------
# Non-daemon java.exe count (a build, a site null, or the gradlew launcher of either). The Gradle daemon
# (GradleDaemon) and the persistent Kotlin compile daemon it spawns (KotlinCompileDaemon; alive between
# builds, never a construction) are excluded; the launcher JVM ("-Dorg.gradle.appname=gradlew") is NOT: it
# means a task is in flight somewhere in this checkout. @(...) is REQUIRED: on PowerShell 5.1 a pipeline
# yielding exactly ONE object has no .Count (the expression prints nothing, which anchor_free_redraw.sh's
# copy of this function read as "idle"; found 2026-09-19 while writing this chain).
busy_jvm() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { (\$_.CommandLine -notmatch 'GradleDaemon') -and (\$_.CommandLine -notmatch 'KotlinCompileDaemon') }).Count" 2>/dev/null | tr -d '[:space:]'
}
busy_jvm_list() {
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { (\$_.CommandLine -notmatch 'GradleDaemon') -and (\$_.CommandLine -notmatch 'KotlinCompileDaemon') } | ForEach-Object { \"pid \$(\$_.ProcessId): \$(\$_.CommandLine.Substring(0, [Math]::Min(200, \$_.CommandLine.Length)))\" }" 2>/dev/null
}
# python.exe processes running this repo's analysis tools (pool readers: STABLE-CELL-SET / UNION-PROFILE-HOME /
# AGREE-ORDER and every other tools/analysis script open the caches). Count + command lines. The chain's own
# python steps (pool_guard, the identity check, the readouts) run synchronously and are finished before any
# call of this function, so they never count themselves.
busy_python() {
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='python3.exe' OR Name='pythonw.exe'\" | Where-Object { (\$_.CommandLine -like '*tools/analysis*') -or (\$_.CommandLine -like '*tools\analysis*') }).Count" 2>/dev/null | tr -d '[:space:]'
}
busy_python_list() {
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='python3.exe' OR Name='pythonw.exe'\" | Where-Object { (\$_.CommandLine -like '*tools/analysis*') -or (\$_.CommandLine -like '*tools\analysis*') } | ForEach-Object { \"pid \$(\$_.ProcessId): \$(\$_.CommandLine)\" }" 2>/dev/null
}
wait_idle() {  # between steps: wait (safety net) rather than refuse; both a JVM and a pool reader block a step
  [ "$DRY" = 1 ] && return 0
  local n p
  n=$(busy_jvm); p=$(busy_python)
  while { [ -n "$n" ] && [ "$n" != "0" ]; } || { [ -n "$p" ] && [ "$p" != "0" ]; }; do
    log "waiting 60 s: ${n:-?} non-daemon JVM(s), ${p:-?} tools/analysis python reader(s) running"
    sleep 60; n=$(busy_jvm); p=$(busy_python)
  done
}

preflight() {
  # (1) no pool reader of this repo may be running (rule 7: nothing reads the pool while an arm builds)
  local p; p=$(busy_python)
  if [ "$DRY" = 1 ]; then echo "  [would check] no python.exe running tools/analysis (now: ${p:-?}); refuse otherwise"; else
    if [ -n "$p" ] && [ "$p" != "0" ]; then
      log "PREFLIGHT $p python.exe process(es) running this repo's tools/analysis (pool readers); refusing to start:"
      busy_python_list | while read -r l; do log "  $l"; done
      exit 1
    fi
    log "PREFLIGHT no tools/analysis python reader running"
  fi
  # (2) no build / site null in flight
  local n; n=$(busy_jvm)
  if [ "$DRY" = 1 ]; then echo "  [would check] no non-daemon java.exe running (now: ${n:-?}); refuse otherwise"; else
    [ -n "$n" ] && [ "$n" != "0" ] && { log "PREFLIGHT $n non-daemon java.exe running (a build or site null is in flight); refusing to start:"; busy_jvm_list | while read -r l; do log "  $l"; done; exit 1; }
    log "PREFLIGHT no non-daemon JVM running"
  fi
  # (3) the flag is merged into the engine this checkout builds
  if git merge-base --is-ancestor "$MERGE_COMMIT" HEAD 2>/dev/null; then log "PREFLIGHT K-SELECTION merge $MERGE_COMMIT is an ancestor of HEAD $(git rev-parse --short HEAD)"; else log "PREFLIGHT $MERGE_COMMIT (the K-SELECTION merge) is NOT an ancestor of HEAD; refusing"; [ "$DRY" = 1 ] || exit 1; fi
  if [ -n "$(git status --porcelain -- src/ 2>/dev/null)" ]; then log "PREFLIGHT src/ is dirty (the manifest would record dirty_src=true); refusing"; [ "$DRY" = 1 ] || exit 1; else log "PREFLIGHT src/ clean"; fi
  # (4) pool guard (a synchronous python step; finished before the next busy_python() call)
  log "PREFLIGHT pool guard: python tools/analysis/pool_guard.py --pool $POOL"
  if [ "$DRY" = 1 ]; then echo "  [would run] python tools/analysis/pool_guard.py --pool $POOL  (refuse on non-zero exit)"; else
    python tools/analysis/pool_guard.py --pool "$POOL" > "$R/pool_guard.out" 2>&1 || { log "PREFLIGHT pool guard FAILED (see $R/pool_guard.out); refusing"; exit 1; }
    log "PREFLIGHT pool guard OK: $(head -1 "$R/pool_guard.out")"
  fi
  # (5) inputs: the record, R1 (I2's reference, registration (d): if lost, I2 is UNDETERMINED), the unprimed nulls, the configs, the checker
  for f in "$CTRL_DIR/dag_snapshots.jsonl" "$CTRL_CSV" experiment_configs/reserved_pool_frozen_p2dca.json \
           "$R1_DIR/dag_snapshots.jsonl" "$R1_DIR/headless_run.log" "$R1_CSV" \
           "$REDRAW/af_s137/seed_137/dag_snapshots.jsonl" "$REDRAW/af_s2048/seed_2048/dag_snapshots.jsonl" \
           "$REDRAW/site_null_af_s137.csv" "$REDRAW/site_null_af_s2048.csv" \
           tools/analysis/k_selection_inert.py tools/analysis/anchor_free_readout.py snapshots.db; do
    [ -f "$f" ] || { log "PREFLIGHT missing $f; refusing"; [ "$DRY" = 1 ] || exit 1; }
  done
  for e in $ARMS; do IFS=: read -r _ cfg _ _ <<< "$e"; [ -f "$CFG/$cfg.toml" ] || { log "PREFLIGHT missing config $CFG/$cfg.toml; refusing"; [ "$DRY" = 1 ] || exit 1; }; done
  # (6) each config differs from its base by outputDir + (primed) the ONE key; the inert one by outputDir only
  local pair b c want got
  for pair in "af_clean_s42:af_clean_s42_inert:0" "af_clean_s42:af_clean_s42_k105:1" "af_s137:af_s137_k105:1" "af_s2048:af_s2048_k105:1"; do
    IFS=: read -r b c want <<< "$pair"
    got=$(diff <(sed -e 's/#.*$//' -e 's/[[:space:]]*$//' "experiment_configs/anchorfree/redraw/$b.toml" | grep -v '^$') \
               <(sed -e 's/#.*$//' -e 's/[[:space:]]*$//' "$CFG/$c.toml" | grep -v '^$') | grep '^[<>]' | grep -v 'outputDir' || true)
    if [ "$want" = 1 ]; then
      [ "$got" = "> proposalAcceptMultiplier = 1.05" ] && log "PREFLIGHT config $c = base $b + outputDir + 'proposalAcceptMultiplier = 1.05' (comment-stripped diff OK)" || { log "PREFLIGHT config $c differs from base $b by more/less than the one key: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
    else
      [ -z "$got" ] && log "PREFLIGHT config $c = base $b + outputDir only (key ABSENT; comment-stripped diff OK)" || { log "PREFLIGHT inert config $c differs from base $b: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
    fi
  done
  # (7) the checker's selftest (R1 vs R1 must be INERT) so a NOT INERT on I2 is the tree's, not the tool's
  if [ "$DRY" = 1 ]; then echo "  [would run] python tools/analysis/k_selection_inert.py --selftest  (refuse unless INERT)"; else
    python tools/analysis/k_selection_inert.py --selftest > "$R/inert_selftest.out" 2>&1 || { log "PREFLIGHT k_selection_inert.py --selftest did not read INERT (see $R/inert_selftest.out); refusing"; exit 1; }
    log "PREFLIGHT inertness checker selftest: $(tail -1 "$R/inert_selftest.out")"
  fi
  log "PREFLIGHT outputs are new dirs under $R (nothing of record is overwritten); ctrl $CTRL_DIR + $CTRL_CSV; I2 reference $R1_DIR (snapshot $(grep -o 'Snapshot ID: [^ ]*' "$R1_DIR/headless_run.log" 2>/dev/null | tail -1 | cut -d' ' -f3))"
}

certified() {  # count certified sites in a site-null CSV: "<certified> <sites> <reps-set>"
  python - "$1" <<'EOF'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
print(sum(1 for r in rows if r.get("cert_site_p95", "").lower() in ("true", "1")), len(rows), "reps=" + ",".join(sorted({r.get("reps", "?") for r in rows})))
EOF
}

restore_frozen_triples() {  # rule 6: restore frozen_triples_*_MAIN.json from HEAD after any build that touched it
  [ "$DRY" = 1 ] && return 0
  local changed; changed=$(git status --porcelain -- 'frozen_triples_*_MAIN.json' 2>/dev/null)
  if [ -n "$changed" ]; then git checkout -- 'frozen_triples_*_MAIN.json' && log "restored frozen_triples_*_MAIN.json from HEAD ($changed)"; fi
}

# ---- steps ------------------------------------------------------------------------------------------------
build() {  # build <arm> <config> <seed>
  local arm=$1 cfgname=$2 seed=$3
  local cfg=$CFG/$cfgname.toml out=$R/$arm.build.out dir=$R/$arm/seed_$seed
  if [ -f "$out" ]; then log "$arm BUILD attempted earlier ($out exists; $( [ -f "$dir/dag_snapshots.jsonl" ] && echo "snapshot present" || echo "no dag_snapshots.jsonl: the arm is UNDETERMINED")); not retried"; return 0; fi
  wait_idle
  log "$arm BUILD start  config $cfg  ratings db $R/ratings_$arm.db  -> $dir"
  run "$arm build" "$out" -- ./gradlew.bat bootRun --console=plain -q --offline "-Dranking.db.path=$R/ratings_$arm.db" --args="--config $cfg"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  log "$arm BUILD exit $rc | $(grep -o 'Snapshot ID: [^ ]*' "$out" | tail -1) | $(grep -o '\[SPLIT-CLOSURE\] [0-9]* train item' "$out" | tail -1) | $(grep -o 'leaves=[0-9]*' "$out" | tail -1) | $(grep -o '\[SLICE\][^|]*' "$out" | head -1)"
  log "$arm BUILD [K-SELECTION] lines: $(grep -c '\[K-SELECTION\]' "$out") | manifest proposal_accept_multiplier: $(grep -o '"proposal_accept_multiplier": *[0-9.]*' "$dir/diagnostics/run_manifest.json" 2>/dev/null | head -1 || echo 'ABSENT') | bar_eff NO-SPLIT lines: $(grep -c 'bar_eff=' "$out")"
  [ -f "$dir/dag_snapshots.jsonl" ] || log "$arm BUILD produced no dag_snapshots.jsonl: recorded as the arm's result (UNDETERMINED), NOT retried"
  restore_frozen_triples
  return 0
}

inertness() {  # I2 vs R1 (build only; no null)
  local dir=$R/i2/seed_42 out=$R/i2_inertness.txt
  if [ -f "$out" ]; then log "I2 INERTNESS present ($out): $(tail -1 "$out")"; return 0; fi
  if [ "$DRY" != 1 ] && [ ! -f "$dir/dag_snapshots.jsonl" ]; then log "I2 INERTNESS skipped: no build (C0 UNDETERMINED)"; return 0; fi
  wait_idle
  log "I2 INERTNESS k_selection_inert.py --i2 $dir --r1 $R1_DIR --r1-null $R1_CSV"
  run "I2 inertness" "$R/inertness.log" -- python tools/analysis/k_selection_inert.py --i2 "$dir" --r1 "$R1_DIR" --r1-null "$R1_CSV" --out "$out"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  case $rc in
    0) log "I2 INERTNESS exit 0 -> INERT | $(grep -m1 'leaf member sets' "$out")" ;;
    3) log "I2 INERTNESS exit 3 -> NOT INERT (C0 FAILED: per the registration nothing primed is READ; the primed arms are still BUILT, all four run regardless) | $(grep -m1 'leaf member sets' "$out")" ;;
    *) log "I2 INERTNESS exit $rc -> input error (see $R/inertness.log); C0 UNDETERMINED" ;;
  esac
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

readout() {  # readout <arm> <seed>   (anchor_free_readout.py vs the record, the REDRAW instrument)
  local arm=$1 seed=$2
  local dir=$R/$arm/seed_$seed out=$R/anchor_free_${arm}_readout.txt csv=$R/site_null_$arm.csv
  if [ -f "$out" ]; then log "$arm READOUT present ($out), skipping"; return 0; fi
  if [ "$DRY" != 1 ] && [ ! -f "$dir/dag_snapshots.jsonl" ]; then log "$arm READOUT skipped: no build"; return 0; fi
  local sn=(); [ -f "$csv" ] && sn=(--site-null "$csv")
  [ "$DRY" = 1 ] && sn=(--site-null "$csv")
  wait_idle
  log "$arm READOUT anchor_free_readout.py $dir vs $CTRL_DIR (unprimed twin: $REDRAW/$(unprimed_of "$arm"))"
  run "$arm readout" "$R/readout_$arm.log" -- python tools/analysis/anchor_free_readout.py "$dir" "$CTRL_DIR" "${sn[@]}" --control-site-null "$CTRL_CSV" --out "$out"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  log "$arm READOUT exit $rc | $(grep -m1 'certified sites' "$out" 2>/dev/null | tr -s ' ' | cut -c1-140)"
  return 0
}

arm() {
  local name=$1 cfg=$2 seed=$3 kind=$4
  log "==== ARM $name (config $cfg, seed dir seed_$seed, $kind) ===="
  build "$name" "$cfg" "$seed"
  if [ "$kind" = inert ]; then inertness; else sitenull "$name"; readout "$name" "$seed"; fi
}

# ---- main -------------------------------------------------------------------------------------------------
[ "$DRY" = 1 ] && echo "DRY RUN: nothing is executed, nothing is logged to $CHAIN_LOG"
log "CHAIN start (dry=$DRY) HEAD $(git rev-parse --short HEAD 2>/dev/null) | order I2 i2 (af_clean_s42_inert), R1' af_clean_s42_k105, R2' af_s137_k105, R3' af_s2048_k105 | all four run regardless"
preflight
for e in $ARMS; do IFS=: read -r n c s k <<< "$e"; arm "$n" "$c" "$s" "$k"; done

log "==== K-SELECTION READOUT ===="
if [ -f tools/analysis/k_selection_readout.py ]; then
  wait_idle
  run "k-selection readout" "$R/k_selection_readout.log" -- python tools/analysis/k_selection_readout.py --run
  rc=$?; [ "$DRY" = 1 ] || log "K-SELECTION READOUT exit $rc (log $R/k_selection_readout.log; outcome $R/k_selection_outcome.txt)"
else
  log "k-selection readout absent (tools/analysis/k_selection_readout.py not found); run it by hand when it lands: python tools/analysis/k_selection_readout.py --run"
fi

log "SWEEP DONE"
if [ "$DRY" != 1 ]; then
  log "---- SUMMARY ----"
  [ -f "$R/i2_inertness.txt" ] && log "I2: $(tail -1 "$R/i2_inertness.txt")" || log "I2: no inertness verdict (C0 UNDETERMINED)"
  for a in $PRIMED; do
    d=$R/$a/seed_$( case $a in af_s137_k105) echo 137;; af_s2048_k105) echo 2048;; *) echo 42;; esac )
    lv=$( [ -f "$R/$a.build.out" ] && grep -o 'leaves=[0-9]*' "$R/$a.build.out" | tail -1 || echo "not built" )
    mp=$( [ -f "$d/diagnostics/run_manifest.json" ] && grep -o '"proposal_accept_multiplier": *[0-9.]*' "$d/diagnostics/run_manifest.json" | head -1 || echo "no manifest" )
    be=$( [ -f "$R/$a.build.out" ] && grep -c 'bar_eff=' "$R/$a.build.out" || echo 0 )
    if [ -f "$R/site_null_$a.csv" ]; then log "$a: $lv | $mp | NO-SPLIT lines carrying bar_eff $be | certified/sites $(certified "$R/site_null_$a.csv") | unprimed $(unprimed_of "$a"): $(certified "$REDRAW/site_null_$(unprimed_of "$a").csv")"; else log "$a: $lv | $mp | NO-SPLIT lines carrying bar_eff $be | no site null (UNDETERMINED)"; fi
  done
  log "tracked files modified (must be only the two standing local edits .gitignore / config/application.yml):"; git status --short | grep -v '^??' | while read -r l; do log "  $l"; done
  log "snapshots_frozen.db sha256: $(sha256sum snapshots_frozen.db 2>/dev/null | cut -c1-16)"
  log "verify: python tools/analysis/pool_guard.py --pool $POOL; python tools/analysis/k_selection_inert.py --i2 $R/i2/seed_42; ls $R"
fi
exit 0
