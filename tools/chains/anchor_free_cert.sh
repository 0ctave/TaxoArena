#!/usr/bin/env bash
# ANCHOR-FREE-CERT sweep (registered 2026-09-17; plan docs/agents/plans/2026-09-17_anchor_free_cert.md).
# Resumable: every step is skipped when its output exists, so a killed session re-runs this script unchanged.
# One construction at a time; waits for the ANCHOR-FREE-FULL job (its readout is written last) before starting.
# Zero judge calls. Run from the repo root under Git Bash:  bash tools/chains/anchor_free_cert.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8
R=experiment_results/anchorfree
CTRL_DIR=$R/af/seed_42
CTRL_CSV=$R/site_null_af_s42.csv
log() { echo "[$(date +%H:%M:%S)] $*"; }

# 0. wait for the full-corpus job (readout file is its last write)
while [ ! -f "$R/anchor_free_full_readout.txt" ]; do log "waiting for ANCHOR-FREE-FULL readout"; sleep 120; done
busy_jvm() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count" 2>/dev/null | tr -d ''; }
while [ "$(busy_jvm)" != "0" ] && [ -n "$(busy_jvm)" ]; do log "a build/site-null JVM is still running; waiting"; sleep 60; done

certified() {  # count certified sites in a site-null CSV
  python - "$1" <<'EOF'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
print(sum(1 for r in rows if r.get("cert_site_p95", "").lower() in ("true", "1")), len(rows))
EOF
}

build() {  # build <arm>
  local arm=$1
  local cfg=experiment_configs/anchorfree/af_${arm}_s42.toml
  if [ -f "$R/af_$arm/seed_42/dag_snapshots.jsonl" ]; then log "$arm build present, skipping"; return 0; fi
  log "$arm BUILD start"
  ./gradlew.bat bootRun --console=plain -q --offline "-Dranking.db.path=$R/ratings_af_$arm.db" --args="--config $cfg" > "$R/af_$arm.build.out" 2>&1
  log "$arm BUILD exit $? | $(grep -o 'construction ended with [0-9]* emergent depth-1 nodes' "$R/af_$arm.build.out" | tail -1) | $(grep -o 'leaves=[0-9]*' "$R/af_$arm.build.out" | tail -1)"
}

sitenull() {  # sitenull <arm> <dim> <droptop> <suffix>
  local arm=$1 dim=$2 drop=$3 suf=$4
  local csv=$R/site_null_af_${arm}${suf}_s42.csv
  if [ -f "$csv" ]; then log "$arm site null $suf present, skipping"; return 0; fi
  local snap; snap=$(grep -o "Snapshot ID: [^ ]*" "$R/af_$arm.build.out" | tail -1 | cut -d' ' -f3)
  [ -z "$snap" ] && { log "$arm no snapshot id; abort"; return 1; }
  log "$arm SITENULL start (dim $dim dropTop $drop) snapshot $snap"
  ./gradlew.bat siteNull --console=plain -q --offline "-DsnapshotId=$snap" "-DsliceDim=$dim" "-DdropTop=$drop" "-Dwhiten=false" "-DoutCsv=$csv" > "$R/sitenull_${arm}${suf}.out" 2>&1
  log "$arm SITENULL exit $? -> $(certified "$csv")"
}

readout() {  # readout <arm>
  local arm=$1
  local out=$R/anchor_free_${arm}_readout.txt
  python tools/analysis/anchor_free_readout.py "$R/af_$arm/seed_42" "$CTRL_DIR" --site-null "$R/site_null_af_${arm}_s42.csv" --control-site-null "$CTRL_CSV" --out "$out" > "$R/readout_$arm.log" 2>&1
  log "$arm READOUT exit $? | $(grep -m1 'certified sites' "$out" | tr -s ' ' | cut -c1-120)"
}

arm() {  # arm <name> <dim> <droptop> [cross]
  local name=$1 dim=$2 drop=$3 cross=${4:-}
  build "$name" && sitenull "$name" "$dim" "$drop" "" && readout "$name"
  if [ -n "$cross" ]; then sitenull "$name" "$dim" 0 "_rawnull"; fi
}

# 0. PRUNE (zero build) if the script exists
[ -f tools/analysis/anchor_free_prune.py ] && [ ! -f "$R/anchor_free_prune_readout.txt" ] && { log "PRUNE readout"; python tools/analysis/anchor_free_prune.py > "$R/prune.log" 2>&1; log "PRUNE exit $?"; }

# 1-3
arm d512 512 0
arm abt1 256 1 cross
arm abt2 256 2 cross

c1=$(certified "$R/site_null_af_d512_s42.csv" | cut -d' ' -f1)
c3=$(certified "$R/site_null_af_abt2_s42.csv" | cut -d' ' -f1)
log "conditions: d512 certified=$c1 abt2 certified=$c3"

# 4 (only if d512 > 18)
if [ "${c1:-0}" -gt 18 ]; then arm bareq512 512 0; else log "arm 4 bareq512 skipped (d512 <= 18)"; fi
# 5
arm bar030 256 0
# 6 (only if d512 > 16 and abt2 > 16)
if [ "${c1:-0}" -gt 16 ] && [ "${c3:-0}" -gt 16 ]; then arm abt2d512 512 2 cross; else log "arm 6 abt2d512 skipped"; fi

log "SWEEP DONE"; for a in d512 abt1 abt2 bareq512 bar030 abt2d512; do [ -f "$R/site_null_af_${a}_s42.csv" ] && echo "$a: $(certified "$R/site_null_af_${a}_s42.csv") $( [ -f "$R/site_null_af_${a}_rawnull_s42.csv" ] && echo "| rawnull $(certified "$R/site_null_af_${a}_rawnull_s42.csv")")"; done
git status --short | grep -v '^??'
