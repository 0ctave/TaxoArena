#!/usr/bin/env bash
# ANCHOR-FREE-CERT arm 4 (af_bareq512) under the 2026-09-17 amendment (run although arm 1 <= 18). Zero judge calls.
# Reuses the sweep's functions; skips finished steps. Run:  bash tools/chains/anchor_free_cert_arm4.sh
set -u
cd "$(dirname "$0")/../.." || exit 1
export PYTHONIOENCODING=utf-8
R=experiment_results/anchorfree
CTRL_DIR=$R/af/seed_42
CTRL_CSV=$R/site_null_af_s42.csv
log() { echo "[$(date +%H:%M:%S)] $*"; }
busy_jvm() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -notmatch 'GradleDaemon' }).Count" 2>/dev/null | tr -d '\r\n '; }
while [ "$(busy_jvm)" != "0" ] && [ -n "$(busy_jvm)" ]; do log "a build/site-null JVM is still running; waiting"; sleep 60; done
# the sweep's build / sitenull / readout / certified functions, verbatim
eval "$(sed -n '/^certified() {/,/^}/p; /^build() {/,/^}/p; /^sitenull() {/,/^}/p; /^readout() {/,/^}/p' tools/chains/anchor_free_cert.sh)"
build bareq512 && sitenull bareq512 512 0 "" && readout bareq512
log "ARM 4 DONE: $(certified "$R/site_null_af_bareq512_s42.csv")"
