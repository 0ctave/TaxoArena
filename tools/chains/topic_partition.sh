#!/usr/bin/env bash
# TOPIC-PARTITION-20NG chain (registered 2026-09-22 before any code or call, commit 6aa2a0d;
# docs/judge_v2_program.md "Registered 2026-09-22 (before any code or call) - TOPIC-PARTITION-20NG", L10030-L10390;
# instrument I7; plan Amendment 8). ZERO judge calls; embeddings local (Ollama qwen3-embedding); one construction at
# a time; every tree is STRUCTURAL EVIDENCE ONLY.
#
# Registered order (I7): I0 ingest -> collision check -> I1 smoke build -> readout --selftest on the smoke -> T1 build
# -> pool export + pool_guard --pool -> T1 null -> T1b build -> T1b null -> [T2 build -> T2 null, ONLY if T1 not built]
# -> readout --run over the arms -> pin re-run. Steps here, in that order:
#   PREFLIGHT   no tools/analysis python reader; no non-daemon JVM; src/ clean; registration commit 6aa2a0d an ancestor of
#               HEAD; Ollama reachable at localhost:11434 with "qwen3-embedding" listed (refuse otherwise); the configs'
#               comment-stripped diffs against their bases; the two selftests (ingest, readout).
#   INGEST      tools/ingest/twenty_newsgroups_ingest.py (skipped when twenty_newsgroups_cache_v1.db exists); the I0
#               rules (5) and (6) are ENFORCED, not printed: row count >= 2,000 AND the manifest's
#               sha256_id_question_category equal to the sha recomputed from the DB itself (ingest_pin; also run in
#               PREFLIGHT when the ingest DB already exists, i.e. a resumed chain); the smoke DB
#               ag_news_smoke_cache_v1.db (--smoke-ag-news).
#   COLLISION   the data-steward's read-only SQL: exact and norm-v1 matches of the 20NG texts against embeddings_cache.db
#               (embeddings.query, queries.raw_text), mmlu_pro.question and multicorpus corpus_questions.text must be 0;
#               refuse otherwise; runs ONCE, before the first 20NG build (marker $R/collision_check.out).
#   BACKUPS     snapshots.db and reserved_test_queries.json into experiment_results/_backup/<name>_<date> if absent,
#               only with 0 JVMs; sha256 printed.
#   PIN before  per-table two-view hashes of EVERY table of mmlu_pro_dataset_cache_v2.db (all 12: the registered
#               acceptance rule reads "every mmlu_pro_dataset_cache_v2.db table UNCHANGED in n and sha"; a table that
#               does not exist is printed as absent, not an error) and of embeddings_cache.db (review 2026-09-20
#               section 3 command, both views must agree) -> $R/pin_before.txt (+ per-row key hashes for the acceptance rule).
#   SMOKE       ag_news_smoke_s42 build (I1), then the SMOKE GATE (not a log line): the chain REFUSES to go on to T1
#               unless the smoke log carries "Snapshot ID:", "[POOL] recorded p" and the trickle's "Total Queries:",
#               naming every missing one; a smoke failure stops the chain BEFORE any 20NG embedding work, and the
#               Design-S fallback is then a registrar bracket before T1, never an automatic path (I1). Then
#               topic_partition.py --selftest and --dry-run --arm smoke.
#   T1          ng_af_s42 build -> pool export (pool_guard --export-snapshot) + pool_guard --pool <id> --db <ingest db>
#               --id-file <export> -> site null (300 reps, sliceDim 256, sepBar ABSENT).
#               [TP20-GUARD-REFUSAL-PRECONDITION 2026-09-23, engine-coder; the registrar's check at docs/judge_v2_program.md
#               L14521-L14522: C0 does NOT cover a guard refusal] A pool_guard REFUSAL raised before any comparison (a
#               non-empty -wal or -journal beside the DB, a DB not found, a registry or argument refusal: see
#               guard_refusal_tag) in the export or the verify is a FAILED PRECONDITION: the chain logs "PRECONDITION
#               FAILED (pool guard refused: <tag>)", the arm STOPS (its site null is not run), NO C0 line is written, the
#               write-once READOUT is withheld and the chain exits 3. A guard that compared and found a mismatch keeps the
#               registered path unchanged ("C0 pool clause FAILED" in chain.log; the readout's C0 gate reads the .out).
#   T1b         ng_af_bareq512_s42 build -> null (sliceDim 512, -DsepBar=0.0145). Runs regardless of T1's result.
#   T2          ONLY if T1 is NOT built (vacuity guard fired or leaves <= 7): the bar per I4 from T1's proposals.csv,
#               clipped to [0.010, 0.025], written into ng_af_bar_eq_s42.toml from the template; build; null at that bar.
#   READOUT     topic_partition.py --run (write-once outcome).
#   PIN after   -> $R/pin_after.txt and the acceptance-rule comparison (dataset-cache tables unchanged; embeddings /
#               queries grew only by new keys; old-key hashes unchanged).
# Build relaunch rule: a build is never retried once its .build.out exists EXCEPT when the log shows no construction
# iteration (no "Iteration <n> completed in" / "=== DAG DIAGNOSTICS" / "Snapshot ID:" line; "[SPLIT-CLOSURE]" is NOT
# read as construction: finishSplit logs it BEFORE the embedding phase) AND an embedding-phase error (connectex /
# "Only one usage of each socket address" / an Ollama HTTP error / connection refused); then up to 3 attempts, each
# APPENDED to the same .build.out. Once construction started, a failed build is the arm's result (UNDETERMINED).
# Resumable: every step is skipped when its output exists. Guards copied verbatim from tools/chains/k_selection.sh
# (busy_jvm / busy_python with @(...).Count, wait_idle, preflight shape, restore_frozen_triples). Outputs under
# experiment_results/topic_partition/ (chain.log, <arm>.build.out, site_null_<arm>.csv, sitenull_<arm>.out, pins, pool
# guard outputs); ratings DBs at the repo root (ratings_topic_partition_<arm>.db; `git check-ignore -v` shows *.db).
# Never writes snapshots_frozen.db; snapshots.db gains the arms' snapshots (new ids); reserved_test_queries.json is
# rewritten by every build (backed up first); frozen_triples_*_MAIN.json restored from HEAD after every build.
#
# Usage (from the repo root, Git Bash):   bash tools/chains/topic_partition.sh [--dry-run]
#   --dry-run  prints every command the chain would run (with the skip decisions it would take) and exits 0.
#   TP_ROOT=<checkout> is honoured for --dry-run ONLY (a dry-run transcript against the main checkout's live state
#   from a worktree); a real run always executes in its own checkout root.
set -u
DRY=0
for a in "$@"; do case "$a" in --dry-run) DRY=1 ;; *) echo "unknown argument: $a" >&2; exit 2 ;; esac; done
if [ -n "${TP_ROOT:-}" ]; then
  [ "$DRY" = 1 ] || { echo "TP_ROOT is honoured for --dry-run only" >&2; exit 2; }
  cd "$TP_ROOT" || exit 1
else
  cd "$(dirname "$0")/../.." || exit 1
fi
export PYTHONIOENCODING=utf-8

REG_COMMIT=6aa2a0d                 # the registration commit; must be an ancestor of HEAD
R=experiment_results/topic_partition
CFG=experiment_configs/topic_partition
ING=twenty_newsgroups_cache_v1.db
SMOKE_DB=ag_news_smoke_cache_v1.db
CHAIN_LOG=$R/chain.log
BACKUP=experiment_results/_backup
TODAY=$(date +%Y-%m-%d)
OLLAMA_TAGS=http://localhost:11434/api/tags
EMBED_MODEL=qwen3-embedding
DROP_TOP=0; WHITEN=false; REPS=300
R1_ROOT_SEP=0.042461               # R1 af_clean_s42 root k = 2 separation (site_null_af_clean_s42.csv n00000001)
R1_D1_REFUSED=0.01319              # R1's largest refused depth-1 min-pair (proposals.csv n00000005 k=2, iter 2)
BAR_LO=0.010; BAR_HI=0.025

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

# ---- arms: name:sliceDim:sepBar(absent|value) --------------------------------------------------------------------
#   smoke  ag_news_smoke_s42     256  absent   (I1; discarded evidence; no null)
#   T1     ng_af_s42             256  absent   (the arm of record; bar 0.025 = the harness default, -DsepBar ABSENT)
#   T1b    ng_af_bareq512_s42    512  0.0145   (its own null at its own bar)
#   T2     ng_af_bar_eq_s42      256  <computed by t2_bar, only if T1 not built>

# ---- guards (verbatim from tools/chains/k_selection.sh) -----------------------------------------------------------
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

restore_frozen_triples() {  # rule 6: restore frozen_triples_*_MAIN.json from HEAD after any build that touched it
  [ "$DRY" = 1 ] && return 0
  local changed; changed=$(git status --porcelain -- 'frozen_triples_*_MAIN.json' 2>/dev/null)
  if [ -n "$changed" ]; then git checkout -- 'frozen_triples_*_MAIN.json' && log "restored frozen_triples_*_MAIN.json from HEAD ($changed)"; fi
}

certified() {  # count certified sites in a site-null CSV: "<certified> <sites> <reps-set>"
  python - "$1" <<'EOF'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
print(sum(1 for r in rows if r.get("cert_site_p95", "").lower() in ("true", "1")), len(rows), "reps=" + ",".join(sorted({r.get("reps", "?") for r in rows})))
EOF
}

strip_toml() { sed -e 's/#.*$//' -e 's/[[:space:]]*$//' "$1" | grep -v '^$'; }

ollama_check() {  # 0 = reachable with the embedding model listed; prints the model list
  local body
  body=$(curl -s --max-time 10 "$OLLAMA_TAGS" 2>/dev/null) || body=""
  [ -z "$body" ] && { echo "unreachable"; return 1; }
  echo "$body" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
except Exception as e:
    print('unparseable: %s' % e); sys.exit(1)
names = [m.get('name', '') for m in d.get('models', [])]
print('models: ' + ', '.join(names))
sys.exit(0 if any('$EMBED_MODEL' in n for n in names) else 1)
"
}

ingest_pin() {  # ENFORCED (I0 rules (5) and (6); the chain used to print these and go on): the ingest DB holds
                # >= 2,000 rows AND the manifest's sha256_id_question_category equals the sha recomputed from the DB
                # itself (sha256 over repr((id, question, category)) + LF, ORDER BY id; the ingest's rows_sha).
                # Read-only (mode=ro); called from the PREFLIGHT when the DB already exists (a resumed chain) and
                # from INGEST after the manifest is written.
  local where=$1
  if [ "$DRY" = 1 ]; then
    echo "  [would check] $ING rows >= 2000 AND $ING.manifest.json sha256_id_question_category == the sha recomputed over SELECT id, question, category ORDER BY id (mode=ro); refuse on either ($where)"
    return 0
  fi
  [ -f "$ING" ] || { log "INGEST-PIN ($where) $ING absent; refusing"; exit 1; }
  [ -f "$ING.manifest.json" ] || { log "INGEST-PIN ($where) manifest $ING.manifest.json missing; refusing"; exit 1; }
  local res rc
  res=$(python - "$ING" <<'PYEOF'
import hashlib, json, sqlite3, sys
db = sys.argv[1]
con = sqlite3.connect("file:%s?mode=ro" % db.replace(chr(92), "/"), uri=True)
try:
    rows = con.execute("SELECT id, question, category FROM twenty_newsgroups ORDER BY id").fetchall()
finally:
    con.close()
h = hashlib.sha256()
for row in rows:
    h.update(repr(tuple(row)).encode())
    h.update(b"\n")
m = json.load(open(db + ".manifest.json", encoding="utf-8"))
claimed = (m.get("sha256_id_question_category") or "").split(" ")[0]
kept = (m.get("counts") or {}).get("kept")
problems = []
if len(rows) < 2000:
    problems.append("row count %d < 2000 (I0 rule (5): the engine's HF fallback short-circuit)" % len(rows))
if kept != len(rows):
    problems.append("manifest kept %s != DB rows %d" % (kept, len(rows)))
if claimed != h.hexdigest():
    problems.append("manifest sha %s != the sha recomputed from the DB %s (I0 rule (6))" % (claimed, h.hexdigest()))
print("rows=%d sha=%s %s" % (len(rows), h.hexdigest(), "OK" if not problems else "REFUSED: " + "; ".join(problems)))
sys.exit(0 if not problems else 1)
PYEOF
  ); rc=$?
  log "INGEST-PIN ($where) $ING $res"
  [ $rc = 0 ] || { log "INGEST-PIN ($where) FAILED: the registered ingest rules (5)/(6) are not met; refusing"; exit 1; }
}

# ---- preflight ------------------------------------------------------------------------------------------------
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
  # (3) the registration is an ancestor of HEAD; src/ clean
  if git merge-base --is-ancestor "$REG_COMMIT" HEAD 2>/dev/null; then log "PREFLIGHT registration $REG_COMMIT is an ancestor of HEAD $(git rev-parse --short HEAD)"; else log "PREFLIGHT $REG_COMMIT (the registration) is NOT an ancestor of HEAD; refusing"; [ "$DRY" = 1 ] || exit 1; fi
  if [ -n "$(git status --porcelain -- src/ 2>/dev/null)" ]; then log "PREFLIGHT src/ is dirty (the manifest would record dirty_src=true); refusing"; [ "$DRY" = 1 ] || exit 1; else log "PREFLIGHT src/ clean"; fi
  # (4) Ollama reachable with the embedding model listed
  local ol; ol=$(ollama_check); local rc=$?
  if [ $rc = 0 ]; then log "PREFLIGHT Ollama $OLLAMA_TAGS reachable, $EMBED_MODEL listed ($ol)"; else log "PREFLIGHT Ollama $OLLAMA_TAGS: $ol ($EMBED_MODEL not listed or unreachable); refusing"; [ "$DRY" = 1 ] || exit 1; fi
  # (5) inputs: configs, template, scripts, the caches of record, snapshots.db
  for f in $CFG/ng_af_s42.toml $CFG/ng_af_bareq512_s42.toml $CFG/ag_news_smoke_s42.toml $CFG/ng_af_bar_eq_s42.toml.template \
           tools/ingest/twenty_newsgroups_ingest.py tools/analysis/topic_partition.py tools/analysis/pool_guard.py \
           experiment_configs/anchorfree/redraw/af_clean_s42.toml mmlu_pro_dataset_cache_v2.db embeddings_cache.db snapshots.db multicorpus_cache_v1.db; do
    [ -f "$f" ] || { log "PREFLIGHT missing $f; refusing"; [ "$DRY" = 1 ] || exit 1; }
  done
  # (6) each config differs from its base by exactly the registered keys (comment-stripped)
  local got
  got=$(diff <(strip_toml experiment_configs/anchorfree/redraw/af_clean_s42.toml) <(strip_toml $CFG/ng_af_s42.toml) | grep '^[<>]' | grep -v 'outputDir\|models\|^< *"\|^< \]' || true)
  local want_t1=$'< datasetType   = "MMLU_PRO"\n> datasetType   = "TWENTY_NEWSGROUPS"\n> corpusDbPath  = "twenty_newsgroups_cache_v1.db"\n< reservedPoolFile = "experiment_configs/reserved_pool_frozen_p2dca.json"\n< pool             = "p2dca21ab5f4ef3ae"'
  [ "$got" = "$want_t1" ] && log "PREFLIGHT config ng_af_s42 = af_clean_s42 + datasetType/corpusDbPath/outputDir/models=[]/no reservedPoolFile+pool (I2; comment-stripped diff OK)" || { log "PREFLIGHT config ng_af_s42 differs from af_clean_s42 by more/less than I2: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
  got=$(diff <(strip_toml $CFG/ng_af_s42.toml) <(strip_toml $CFG/ng_af_bareq512_s42.toml) | grep '^[<>]' | grep -v 'outputDir' || true)
  [ "$got" = $'> embeddingSliceDim = 512\n< proposalSeparationBar = 0.025\n> proposalSeparationBar = 0.0145' ] && log "PREFLIGHT config ng_af_bareq512_s42 = T1 + outputDir + embeddingSliceDim 512 + bar 0.0145 (I3; diff OK)" || { log "PREFLIGHT config ng_af_bareq512_s42 differs from T1 by more/less than I3: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
  got=$(diff <(strip_toml $CFG/ng_af_s42.toml) <(strip_toml $CFG/ag_news_smoke_s42.toml) | grep '^[<>]' | grep -v 'outputDir' || true)
  [ "$got" = $'< datasetType   = "TWENTY_NEWSGROUPS"\n< corpusDbPath  = "twenty_newsgroups_cache_v1.db"\n> datasetType   = "AG_NEWS"\n> corpusDbPath  = "ag_news_smoke_cache_v1.db"' ] && log "PREFLIGHT config ag_news_smoke_s42 = T1 + outputDir + AG_NEWS + its DB (I1; diff OK)" || { log "PREFLIGHT config ag_news_smoke_s42 differs from T1 by more/less than I1: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
  got=$(diff <(strip_toml $CFG/ng_af_s42.toml) <(strip_toml $CFG/ng_af_bar_eq_s42.toml.template) | grep '^[<>]' | grep -v 'outputDir' || true)
  [ "$got" = $'< proposalSeparationBar = 0.025\n> proposalSeparationBar = @T2_BAR@' ] && log "PREFLIGHT template ng_af_bar_eq_s42 = T1 + outputDir + the placeholder bar (I4; diff OK)" || { log "PREFLIGHT template differs from T1 by more/less than the bar line: [$got]; refusing"; [ "$DRY" = 1 ] || exit 1; }
  # (7) ratings DBs at the root are ignored
  for a in ag_news_smoke_s42 ng_af_s42 ng_af_bareq512_s42 ng_af_bar_eq_s42; do
    git check-ignore -q "ratings_topic_partition_$a.db" && log "PREFLIGHT ratings_topic_partition_$a.db ignored ($(git check-ignore -v "ratings_topic_partition_$a.db" | cut -f1))" || { log "PREFLIGHT ratings_topic_partition_$a.db is NOT ignored; refusing"; [ "$DRY" = 1 ] || exit 1; }
  done
  git check-ignore -q "$ING" && git check-ignore -q "$SMOKE_DB" && log "PREFLIGHT $ING and $SMOKE_DB ignored" || { log "PREFLIGHT the ingest DBs are not ignored; refusing"; [ "$DRY" = 1 ] || exit 1; }
  # (8) selftests (synchronous python steps; finished before the next busy_python() call)
  if [ "$DRY" = 1 ]; then echo "  [would run] python tools/ingest/twenty_newsgroups_ingest.py --selftest  (refuse on non-zero exit)"; echo "  [would run] python tools/analysis/topic_partition.py --selftest  (refuse on non-zero exit)"; else
    python tools/ingest/twenty_newsgroups_ingest.py --selftest > "$R/ingest_selftest.out" 2>&1 || { log "PREFLIGHT ingest selftest FAILED (see $R/ingest_selftest.out); refusing"; exit 1; }
    log "PREFLIGHT ingest selftest: $(tail -1 "$R/ingest_selftest.out")"
    python tools/analysis/topic_partition.py --selftest > "$R/readout_selftest.out" 2>&1 || { log "PREFLIGHT readout selftest FAILED (see $R/readout_selftest.out); refusing"; exit 1; }
    log "PREFLIGHT readout selftest: $(tail -1 "$R/readout_selftest.out")"
  fi
  # (9) the ingest DB, when it already exists (a resumed chain), must satisfy the registered rules BEFORE anything else
  if [ -f "$ING" ]; then ingest_pin preflight; else
    if [ "$DRY" = 1 ]; then echo "  [would check] (after the ingest step; $ING absent now) $ING rows >= 2000 and the manifest sha == the sha recomputed from the DB"; else log "PREFLIGHT $ING absent; the ingest step creates it and ingest_pin runs there"; fi
  fi
  log "PREFLIGHT outputs are new files under $R; nothing of record is overwritten; snapshots_frozen.db never opened for write"
}

# ---- I0 ingest ------------------------------------------------------------------------------------------------
ingest() {
  if [ -f "$ING" ]; then log "INGEST $ING present ($(stat -c %s "$ING") bytes); not re-ingested (write-once)"; else
    wait_idle
    log "INGEST python tools/ingest/twenty_newsgroups_ingest.py --out $ING (sklearn cache in the data home; --fetch NOT passed: the declared fetch was performed once by the engine-coder)"
    run "20NG ingest" "$R/ingest.out" -- python tools/ingest/twenty_newsgroups_ingest.py --out "$ING"
    local rc=$?; [ "$DRY" = 1 ] || { [ $rc = 0 ] || { log "INGEST exit $rc (see $R/ingest.out); refusing"; exit 1; }; }
  fi
  if [ "$DRY" = 1 ]; then echo "  [would check] $ING rows >= 2000; manifest $ING.manifest.json sha printed; copied to $R/ingest_manifest.json"; else
    local n; n=$(python -c "import sqlite3; print(sqlite3.connect('file:$ING?mode=ro', uri=True).execute('select count(*) from twenty_newsgroups').fetchone()[0])")
    [ "$n" -ge 2000 ] || { log "INGEST $ING holds $n rows (< 2000); refusing"; exit 1; }
    [ -f "$ING.manifest.json" ] || { log "INGEST manifest $ING.manifest.json missing; refusing"; exit 1; }
    cp "$ING.manifest.json" "$R/ingest_manifest.json"
    log "INGEST $ING rows=$n; manifest sha $(python -c "import json; m=json.load(open('$ING.manifest.json')); print(m['sha256_id_question_category'], 'kept', m['counts']['kept'], 'short', m['counts']['dropped_short'], 'dup', m['counts']['dropped_duplicate'], 'leak', m['counts']['leak_count'])")"
  fi
  ingest_pin ingest
  if [ -f "$SMOKE_DB" ]; then log "INGEST smoke DB $SMOKE_DB present; not re-copied"; else
    log "INGEST smoke DB: python tools/ingest/twenty_newsgroups_ingest.py --smoke-ag-news (2,000 ag_news rows of record, mode=ro, verbatim)"
    run "smoke DB" "$R/ingest_smoke.out" -- python tools/ingest/twenty_newsgroups_ingest.py --smoke-ag-news
    local rc=$?; [ "$DRY" = 1 ] || { [ $rc = 0 ] || { log "INGEST smoke DB exit $rc (see $R/ingest_smoke.out); refusing"; exit 1; }; }
  fi
}

# ---- zero-collision check (read-only; once, before the first 20NG build) --------------------------------------
collision_check() {
  local out=$R/collision_check.out
  if [ -f "$out" ] && grep -q "COLLISION-CHECK OK" "$out"; then log "COLLISION check done earlier ($out): $(grep 'COLLISION-CHECK OK' "$out")"; return 0; fi
  if [ "$DRY" = 1 ]; then echo "  [would run] zero-collision check: exact + norm-v1 matches of $ING texts vs embeddings_cache.db (embeddings.query, queries.raw_text), mmlu_pro_dataset_cache_v2.db mmlu_pro.question, multicorpus_cache_v1.db corpus_questions.text; refuse if any > 0  > $out"; return 0; fi
  wait_idle
  python - "$ING" > "$out" 2>&1 <<'EOF'
import sqlite3, sys, os
sys.path.insert(0, os.path.join("tools", "analysis"))
from split_side import norm
ing = sys.argv[1]
c = sqlite3.connect("file:%s?mode=ro" % ing, uri=True)
texts = [t for (t,) in c.execute("SELECT question FROM twenty_newsgroups")]
c.close()
exact = set(texts); norms = {norm(t) for t in texts}
print("20NG texts: %d (distinct %d; norm-v1 distinct %d)" % (len(texts), len(exact), len(norms)))
total = 0
for db, table, col in (("embeddings_cache.db", "embeddings", "query"), ("embeddings_cache.db", "queries", "raw_text"),
                       ("mmlu_pro_dataset_cache_v2.db", "mmlu_pro", "question"), ("multicorpus_cache_v1.db", "corpus_questions", "text")):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    n = e = m = 0
    for (t,) in con.execute("SELECT %s FROM %s" % (col, table)):
        n += 1
        if t is None:
            continue
        if t in exact:
            e += 1
        if norm(t) in norms:
            m += 1
    con.close()
    print("%-30s %-18s %-9s rows=%7d exact=%d norm-v1=%d" % (db, table, col, n, e, m))
    total += e + m
print("COLLISION-CHECK %s (total collisions %d)" % ("OK" if total == 0 else "FAILED", total))
sys.exit(0 if total == 0 else 1)
EOF
  local rc=$?
  cat "$out" | while read -r l; do log "  $l"; done
  [ $rc = 0 ] || { log "COLLISION check FAILED (see $out); refusing"; exit 1; }
}

# ---- backups + pins -------------------------------------------------------------------------------------------
backups() {
  local n; n=$(busy_jvm)
  if [ "$DRY" = 1 ]; then echo "  [would check] 0 non-daemon JVMs (now: ${n:-?}), then copy snapshots.db -> $BACKUP/snapshots_$TODAY.db and reserved_test_queries.json -> $BACKUP/reserved_test_queries_$TODAY.json if absent; sha256 printed"; return 0; fi
  [ -n "$n" ] && [ "$n" != "0" ] && { log "BACKUP refused: $n non-daemon JVM(s) running"; exit 1; }
  mkdir -p "$BACKUP"
  for pair in "snapshots.db:$BACKUP/snapshots_$TODAY.db" "reserved_test_queries.json:$BACKUP/reserved_test_queries_$TODAY.json"; do
    IFS=: read -r src dst <<< "$pair"
    if [ -f "$dst" ]; then log "BACKUP $dst present; not overwritten (sha $(sha256sum "$dst" | cut -c1-16))"; else
      cp "$src" "$dst" && log "BACKUP $src -> $dst (sha $(sha256sum "$dst" | cut -c1-16); live $(sha256sum "$src" | cut -c1-16))"
    fi
  done
  [ -s snapshots.db-wal ] && log "BACKUP NOTE snapshots.db-wal is $(stat -c %s snapshots.db-wal) bytes (a writer has not checkpointed)"
  return 0
}

pin() {  # pin <before|after>: the review 2026-09-20 section 3 two-view command + per-row key hashes for the acceptance rule
  local when=$1
  local out=$R/pin_$when.txt rows=$R/pin_${when}_rows.tsv
  if [ -f "$out" ]; then log "PIN $when present ($out); not recomputed"; return 0; fi
  if [ "$DRY" = 1 ]; then echo "  [would run] per-table two-view pin (mode=ro&immutable=1 and mode=ro must agree) of ALL 12 tables of mmlu_pro_dataset_cache_v2.db (reserved_pool, reserved_pool_meta, eval_results, eval_question_link, mmlu_pro, corpus_registry, ag_news, twenty_newsgroups, arc, mmlu_original, active_reserved_pool, sqlite_sequence; an absent table is printed as absent) and of embeddings_cache.db (embeddings, queries, gmm_vectors)  > $out ; per-row hashes of embeddings(query -> sha(vector)) and queries(id -> sha(row))  > $rows"; return 0; fi
  wait_idle
  python - "$out" "$rows" <<'EOF'
import sqlite3, hashlib, sys
out, rows_path = sys.argv[1], sys.argv[2]
PIN = {  # (table, order-by): rows ordered by primary key, sha256 over repr(row). EVERY table of the dataset cache
         # (the registered acceptance rule: "every mmlu_pro_dataset_cache_v2.db table UNCHANGED in n and sha"), all
         # 12 of them today; twenty_newsgroups is the one a corpusDbPath failure would fill (data-steward H1). A
         # table that does not exist is PRINTED AS ABSENT (n=ABSENT sha256=-), never an error; absent-then-present
         # is read back as CHANGED by the acceptance rule.
  "mmlu_pro_dataset_cache_v2.db": [("reserved_pool","pool_id, question_id"), ("reserved_pool_meta","pool_id"),
      ("eval_results","question_id, model_name"), ("eval_question_link","question_id"), ("mmlu_pro","id"),
      ("corpus_registry","source"), ("ag_news","id"), ("twenty_newsgroups","id"), ("arc","id"),
      ("mmlu_original","id"), ("active_reserved_pool","only_row"), ("sqlite_sequence","name")],
  "embeddings_cache.db": [("embeddings","query"), ("queries","id"), ("gmm_vectors","id")],
}
lines = []; agree = True; seen = {}
for db, tabs in PIN.items():
    for view in ("mode=ro&immutable=1", "mode=ro"):
        c = sqlite3.connect(f"file:{db}?{view}", uri=True)
        for t, order in tabs:
            if not c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()[0]:
                n, digest = -1, "-"          # absent: printed, not an error; the acceptance rule reads it back
                line = f"{db:32s} {view:20s} {t:20s} n={'ABSENT':>8} sha256=-"
            else:
                h = hashlib.sha256(); n = 0
                for row in c.execute(f'SELECT * FROM "{t}" ORDER BY {order}'):
                    h.update(repr(row).encode()); h.update(b"\n"); n += 1
                digest = h.hexdigest()
                line = f"{db:32s} {view:20s} {t:20s} n={n:>8} sha256={digest}"
            lines.append(line); print(line)
            key = (db, t)
            if key in seen and seen[key] != (n, digest):
                agree = False
            seen[key] = (n, digest)
        c.close()
lines.append("VIEWS %s" % ("AGREE" if agree else "DISAGREE (a live WAL tail; refuse)"))
print(lines[-1])
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
c = sqlite3.connect("file:embeddings_cache.db?mode=ro", uri=True)
with open(rows_path, "w", encoding="utf-8", newline="\n") as f:
    for q, v in c.execute("SELECT query, vector FROM embeddings ORDER BY query"):
        f.write("embeddings\t%s\t%s\n" % (hashlib.sha256(q.encode("utf-8")).hexdigest(), hashlib.sha256(v if isinstance(v, bytes) else repr(v).encode()).hexdigest()))
    for row in c.execute("SELECT * FROM queries ORDER BY id"):
        f.write("queries\t%s\t%s\n" % (hashlib.sha256(str(row[0]).encode("utf-8")).hexdigest(), hashlib.sha256(repr(row).encode()).hexdigest()))
c.close()
sys.exit(0 if agree else 1)
EOF
  local rc=$?
  [ $rc = 0 ] && log "PIN $when written ($out; $(grep -c . "$rows") row hashes in $rows)" || { log "PIN $when: the two views DISAGREE (live WAL tail); refusing"; exit 1; }
}

acceptance() {  # after the chain: dataset-cache tables unchanged; embeddings/queries grew only by new keys; old-key hashes unchanged
  local out=$R/acceptance.txt
  if [ "$DRY" = 1 ]; then echo "  [would run] acceptance comparison pin_before vs pin_after (+ row hashes)  > $out"; return 0; fi
  python - "$R" "$ING" > "$out" 2>&1 <<'EOF'
import sys, re, json, sqlite3
R, ing = sys.argv[1], sys.argv[2]
def table_pins(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+n=\s*(\d+|ABSENT) sha256=(\S+)", line)
        if m and m.group(2) == "mode=ro":
            d[(m.group(1), m.group(3))] = (-1 if m.group(4) == "ABSENT" else int(m.group(4)), m.group(5))
    return d
def nfmt(n):
    return "ABSENT" if n is None or n < 0 else str(n)
def row_hashes(path):
    d = {}
    for line in open(path, encoding="utf-8"):
        t, k, h = line.rstrip("\n").split("\t")
        d[(t, k)] = h
    return d
b, a = table_pins(R + "/pin_before.txt"), table_pins(R + "/pin_after.txt")
rb, ra = row_hashes(R + "/pin_before_rows.tsv"), row_hashes(R + "/pin_after_rows.tsv")
ok = True
for key in sorted(set(b) | set(a)):
    db, t = key
    bv, av = b.get(key), a.get(key)
    if db.startswith("mmlu_pro_dataset_cache_v2"):
        same = bv is not None and av is not None and bv == av
        ok &= same
        print("%-32s %-20s before n=%s sha=%s after n=%s sha=%s -> %s"
              % (db, t, nfmt(bv[0]) if bv else "NOT PINNED", bv[1][:12] if bv else "-",
                 nfmt(av[0]) if av else "NOT PINNED", av[1][:12] if av else "-",
                 "UNCHANGED" if same else "CHANGED (refuse)"))
    elif bv is not None and av is not None:
        print("%-32s %-20s before n=%s after n=%s (delta %+d)" % (db, t, nfmt(bv[0]), nfmt(av[0]), av[0] - bv[0]))
    else:
        print("%-32s %-20s before n=%s after n=%s (pinned on one side only)" % (db, t, nfmt(bv[0]) if bv else "NOT PINNED", nfmt(av[0]) if av else "NOT PINNED"))
for t in ("embeddings", "queries"):
    old = {k: h for (tt, k), h in rb.items() if tt == t}
    new = {k: h for (tt, k), h in ra.items() if tt == t}
    changed = sum(1 for k, h in old.items() if new.get(k) != h)
    removed = sum(1 for k in old if k not in new)
    added = sum(1 for k in new if k not in old)
    okt = changed == 0 and removed == 0
    ok &= okt
    print("%s: old keys %d, changed %d, removed %d, added %d -> %s" % (t, len(old), changed, removed, added, "old keys UNCHANGED" if okt else "old keys MOVED (refuse)"))
kept = json.load(open(ing + ".manifest.json"))["counts"]["kept"]
c = sqlite3.connect("file:embeddings_cache.db?mode=ro", uri=True)
n_emb = c.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
c.close()
print("embeddings expected n = before (%d) + kept 20NG (%d) + 2,000 ag_news (smoke; fewer if already cached) = %d; actual %d" % (b[("embeddings_cache.db", "embeddings")][0], kept, b[("embeddings_cache.db", "embeddings")][0] + kept + 2000, n_emb))
print("ACCEPTANCE %s" % ("OK" if ok else "FAILED"))
sys.exit(0 if ok else 1)
EOF
  local rc=$?
  cat "$out" | while read -r l; do log "  $l"; done
  [ $rc = 0 ] && log "ACCEPTANCE OK" || log "ACCEPTANCE FAILED (see $out): the READY's pin rule is violated; report before anything of record is written"
}

smoke_gate() {  # I1 is a GATE, not a log line (READY defect 1): Design N must be PROVEN on the 2,000-row ag_news
                # smoke before any 20NG embedding work. A smoke failure stops the chain here; the registration's
                # Design-S fallback is a registrar bracket taken BEFORE T1, never an automatic path of this chain.
  local sb=$R/ag_news_smoke_s42.build.out
  if [ "$DRY" = 1 ]; then
    echo "  [would check] GATE: $sb must carry ALL of 'Snapshot ID:', '[POOL] recorded p' and 'Total Queries:'; otherwise the chain names every missing one and EXITS 1 before the T1 build (no 20NG document is embedded)"
    return 0
  fi
  [ -f "$sb" ] || { log "SMOKE GATE FAILED (Design N unproven): the smoke build log $sb is absent; refusing to start T1 (no 20NG document is embedded); the registrar decides Design S before T1 (I1)"; exit 1; }
  local missing=""
  grep -q 'Snapshot ID:' "$sb" || missing="$missing 'Snapshot ID:' (no snapshot saved);"
  grep -q '\[POOL\] recorded p' "$sb" || missing="$missing '[POOL] recorded p<id>' (no pool recorded);"
  grep -q 'Total Queries:' "$sb" || missing="$missing 'Total Queries:' (the trickle did not run);"
  if [ -n "$missing" ]; then
    log "SMOKE GATE FAILED (Design N unproven): missing in $sb:$missing"
    log "SMOKE GATE refusing to start T1: no 20NG document is embedded; the study falls back to Design S only by a registrar bracket BEFORE T1 (I1), never automatically"
    exit 1
  fi
  log "SMOKE GATE OK: Design N proven on ag_news ('Snapshot ID:', '[POOL] recorded p' and 'Total Queries:' all present in $sb)"
}

# ---- builds ---------------------------------------------------------------------------------------------------
# Construction PROPER has started: a completed iteration, the per-iteration DAG diagnostics, or the saved snapshot.
# "[SPLIT-CLOSURE]" is deliberately NOT read: TaxonomySplitter.finishSplit logs it while the split is computed, BEFORE
# TaxonomyEngine's "Phase 1: Precomputing Embeddings", so reading it would class an embedding-phase failure as
# "construction started" and make the 3-attempt relaunch rule vacuous for exactly the runs it exists for.
construction_started() { grep -qE 'Iteration [0-9]+ completed in|=== DAG DIAGNOSTICS|Snapshot ID:' "$1" 2>/dev/null; }
embedding_error() { grep -qi 'connectex\|Only one usage of each socket address\|Connection refused\|ollama.*\(error\|exception\|refused\|timeout\)\|HTTP [45][0-9][0-9]\|EmbeddingException\|Failed to embed' "$1" 2>/dev/null; }
attempts_of() { grep -c '^=== BUILD ATTEMPT' "$1" 2>/dev/null || echo 0; }

build() {  # build <arm> [config path]   (default $CFG/<arm>.toml)
  local arm=$1
  local cfg=${2:-$CFG/$arm.toml} out=$R/$arm.build.out dir=$R/$arm/seed_42
  if [ -f "$out" ]; then
    if construction_started "$out"; then log "$arm BUILD attempted earlier ($out exists, construction started; $( [ -f "$dir/dag_snapshots.jsonl" ] && echo "snapshot present" || echo "no dag_snapshots.jsonl: the arm is UNDETERMINED")); not retried"; return 0; fi
    local n; n=$(attempts_of "$out")
    if embedding_error "$out" && [ "$n" -lt 3 ]; then log "$arm BUILD earlier attempt(s) $n ended in the embedding phase (no construction iteration; embedding-phase error in the log); relaunching (attempt $((n + 1)) of 3, appended)"; else log "$arm BUILD attempted earlier ($out exists; no construction iteration, $( embedding_error "$out" && echo "embedding error but 3 attempts used" || echo "no embedding-phase error pattern")); not retried (UNDETERMINED)"; return 0; fi
  fi
  wait_idle
  local n; n=$(attempts_of "$out")
  log "$arm BUILD start  config $cfg  ratings db ratings_topic_partition_$arm.db  -> $dir (attempt $((n + 1)))"
  [ "$DRY" = 1 ] || echo "=== BUILD ATTEMPT $((n + 1)) $(date +%Y-%m-%dT%H:%M:%S)" >> "$out"
  run_append "$arm build" "$out" -- ./gradlew.bat bootRun --console=plain -q --offline "-Dranking.db.path=ratings_topic_partition_$arm.db" --args="--config $cfg"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  log "$arm BUILD exit $rc | $(grep -o 'Snapshot ID: [^ ]*' "$out" | tail -1) | $(grep -o '\[POOL\] recorded [^ ]*' "$out" | tail -1) | $(grep -o '\[SPLIT-CLOSURE\] [0-9]* train item' "$out" | tail -1) | $(grep -o 'leaves=[0-9]*' "$out" | tail -1) | $(grep -o '\[SLICE\][^|]*' "$out" | head -1) | $(grep -o 'Fetched [0-9]* [A-Za-z0-9 ]* queries across [0-9]* categories' "$out" | head -1) | trickle $(grep -o 'Total Queries: [0-9]*' "$out" | tail -1)"
  log "$arm BUILD manifest: anchor_free $(grep -o '"anchor_free": *[a-z]*' "$dir/diagnostics/run_manifest.json" 2>/dev/null | head -1 || echo ABSENT) | proposal_accept_multiplier $(grep -o '"proposal_accept_multiplier": *[0-9.]*' "$dir/diagnostics/run_manifest.json" 2>/dev/null | head -1 || echo ABSENT) | embedding_model $(grep -o '"embedding_model": *"[^"]*"' "$dir/diagnostics/run_manifest.json" 2>/dev/null | head -1 || echo ABSENT) | vacuity guard: $(grep -q 'construction ended with the root as a single leaf' "$out" && echo FIRED || echo 'not fired') | $(grep -o '\[ANCHOR-FREE\] construction ended with [0-9]* emergent depth-1 nodes' "$out" | tail -1)"
  [ -f "$dir/dag_snapshots.jsonl" ] || log "$arm BUILD produced no dag_snapshots.jsonl: recorded as the arm's result (UNDETERMINED), NOT retried unless the relaunch rule applies"
  restore_frozen_triples
  return 0
}

# TP20-GUARD-REFUSAL-PRECONDITION: pool_guard.py (d30c19e) exits 1 with a "[POOL-GUARD] ..." line both when it REFUSES
# to read (before any comparison) and when it compares and finds a MISMATCH, so the two are told apart by the refusal
# text, never by the exit code alone. Only the pre-comparison refusals of pool_guard.py are listed (open_ro: the -wal /
# -journal sidecar and the missing DB; resolve_sources / registry_entry: the registry; main / _flag_value: the
# arguments). Every other non-zero exit (hash mismatch, row mismatch, pool not recorded, a traceback) is NOT a refusal
# and takes the existing path. The pattern is anchored at the line start and on the refusal's own wording.
guard_refusal_tag() {  # guard_refusal_tag <pool_guard output file>: prints the tag and returns 0 iff it holds a refusal
  local f=$1
  [ -f "$f" ] || return 1
  if grep -qE '^\[POOL-GUARD\] .*-wal is non-empty \(' "$f"; then echo "non-empty -wal"; return 0; fi
  if grep -qE '^\[POOL-GUARD\] .*-journal is non-empty \(' "$f"; then echo "non-empty -journal"; return 0; fi
  if grep -qE '^\[POOL-GUARD\] database not found: ' "$f"; then echo "database not found"; return 0; fi
  if grep -qE '^\[POOL-GUARD\] pool [^ ]+ is not in the registry ' "$f"; then echo "registry refusal"; return 0; fi
  if grep -qE '^\[POOL-GUARD\] (--db / --id-file apply to --pool <id> only|--[a-z-]+ needs a value)' "$f"; then echo "argument refusal"; return 0; fi
  return 1
}
PRECOND_FAILED=""   # arms stopped on a failed precondition (space-separated); non-empty withholds the READOUT
precondition_failed() {  # precondition_failed <arm> <step> <tag> <output file>
  PRECOND_FAILED="${PRECOND_FAILED:+$PRECOND_FAILED }$1"
  log "$1 POOL PRECONDITION FAILED (pool guard refused: $3) in the $2 step (see $4): the guard compared nothing, so this is NOT an outcome and nothing is recorded for the pool clause; the arm STOPS. Remedy (back up the DB with its sidecars, the data-steward checkpoints it by a read-write open and close, re-verify), then re-run the chain (resumable). Guard said: $(grep -m1 '^\[POOL-GUARD\]' "$4" | tr -d '\r' | cut -c1-400)"
}

pool_export() {  # pool_export <arm>: export the snapshot's reserved_queries and verify the pool against the ingest DB
                 # returns 3 on a FAILED PRECONDITION (a pool_guard refusal), 0 otherwise (TP20-GUARD-REFUSAL-PRECONDITION)
  local arm=$1
  local bout=$R/$arm.build.out out=$R/pool_guard_$arm.out
  if [ -f "$out" ] && grep -q ' OK:' "$out"; then log "$arm POOL verified earlier ($out): $(head -1 "$out")"; return 0; fi
  local snap pool
  if [ "$DRY" = 1 ]; then snap='<Snapshot ID from '"$bout"'>'; pool='<pool id from '"$bout"'>'; else
    snap=$(grep -o 'Snapshot ID: [^ ]*' "$bout" 2>/dev/null | tail -1 | cut -d' ' -f3); pool=$(grep -o '\[POOL\] recorded [^ ]*' "$bout" 2>/dev/null | tail -1 | cut -d' ' -f3)
    [ -z "$snap" ] || [ -z "$pool" ] && { log "$arm POOL no 'Snapshot ID:' / '[POOL] recorded' in $bout (build failed or absent); C0 pool clause UNDETERMINED"; return 0; }
    [ "$pool" = "<none>" ] && { log "$arm POOL the build recorded no pool (<none>); C0 pool clause FAILED"; return 0; }
  fi
  local idf=experiment_configs/reserved_pool_frozen_${pool}_20ng.json
  wait_idle
  log "$arm POOL export: python tools/analysis/pool_guard.py --export-snapshot snapshots.db $snap --out $idf"
  if [ ! -f "$idf" ] || [ "$DRY" = 1 ]; then
    run "$arm pool export" "$R/pool_export_$arm.out" -- python tools/analysis/pool_guard.py --export-snapshot snapshots.db "$snap" --out "$idf"
    local erc=$? etag
    [ "$DRY" = 1 ] || log "$arm POOL export: $(tail -1 "$R/pool_export_$arm.out")"
    if [ "$DRY" != 1 ] && [ $erc != 0 ] && etag=$(guard_refusal_tag "$R/pool_export_$arm.out"); then precondition_failed "$arm" export "$etag" "$R/pool_export_$arm.out"; return 3; fi
  else log "$arm POOL id file $idf present (same split as an earlier arm); reused"; fi
  log "$arm POOL verify: python tools/analysis/pool_guard.py --pool $pool --db $ING --id-file $idf"
  run "$arm pool guard" "$out" -- python tools/analysis/pool_guard.py --pool "$pool" --db "$ING" --id-file "$idf"
  local rc=$? tag
  [ "$DRY" = 1 ] && return 0
  if [ $rc != 0 ] && tag=$(guard_refusal_tag "$out"); then precondition_failed "$arm" verify "$tag" "$out"; return 3; fi
  [ $rc = 0 ] && log "$arm POOL OK: $(head -1 "$out")" || log "$arm POOL guard FAILED (exit $rc; see $out): C0 pool clause FAILED"
  return 0
}

sitenull() {  # sitenull <arm> <sliceDim> <sepBar|absent>
  local arm=$1 slice=$2 bar=$3
  local csv=$R/site_null_$arm.csv bout=$R/$arm.build.out marker=$R/$arm.sitenull.started
  if [ -f "$csv" ]; then log "$arm SITENULL present ($csv): $(certified "$csv"), skipping"; return 0; fi
  if [ -f "$marker" ]; then log "$arm SITENULL was interrupted (marker $marker exists, no $csv); restarting (unattended; sitenull_$arm.out is appended, nothing overwritten)"; fi
  local snap
  if [ "$DRY" = 1 ]; then snap=$( [ -f "$bout" ] && grep -o 'Snapshot ID: [^ ]*' "$bout" | tail -1 | cut -d' ' -f3 ); snap=${snap:-'<Snapshot ID parsed from '"$bout"'>'}; else
    snap=$(grep -o 'Snapshot ID: [^ ]*' "$bout" 2>/dev/null | tail -1 | cut -d' ' -f3)
    [ -z "$snap" ] && { log "$arm SITENULL no 'Snapshot ID:' in $bout (build failed or absent); arm UNDETERMINED for certification, continuing"; return 0; }
  fi
  local barargs=()
  [ "$bar" = absent ] || barargs=("-DsepBar=$bar")
  wait_idle
  log "$arm SITENULL start snapshot $snap (sliceDim $slice dropTop $DROP_TOP whiten $WHITEN reps $REPS sepBar $bar) -> $csv (gradle WITHOUT -q so the harness's [SEPBAR] line and site table land in sitenull_$arm.out)"
  [ "$DRY" = 1 ] || { echo "$(date +%Y-%m-%dT%H:%M:%S) snapshot $snap sepBar $bar" >> "$marker"; }
  run_append "$arm site null" "$R/sitenull_$arm.out" -- ./gradlew.bat siteNull --console=plain --offline "-DsnapshotId=$snap" "-DsliceDim=$slice" "-DdropTop=$DROP_TOP" "-Dwhiten=$WHITEN" "-PnullReps=$REPS" "-DoutCsv=$csv" "${barargs[@]}"
  local rc=$?
  [ "$DRY" = 1 ] && return 0
  if [ -f "$csv" ]; then log "$arm SITENULL exit $rc -> $(certified "$csv") | $(grep -o '\[SEPBAR\][^|]*' "$R/sitenull_$arm.out" | tail -1)"; else log "$arm SITENULL exit $rc, no CSV written: arm UNDETERMINED (no partial null is read)"; fi
  return 0
}

pool_then_null() {  # pool_then_null <arm> <sliceDim> <sepBar|absent>: the arm's pool step, then its null unless it STOPPED
  if pool_export "$1"; then sitenull "$@"; else log "$1 SITENULL NOT RUN: the arm STOPPED on a FAILED PRECONDITION (pool guard refusal; TP20-GUARD-REFUSAL-PRECONDITION)"; fi
}

readout() {  # the write-once READOUT, withheld while any arm is stopped on a failed precondition
  if [ -n "$PRECOND_FAILED" ]; then log "READOUT WITHHELD: PRECONDITION FAILED on arm(s) $PRECOND_FAILED (pool guard refused before comparing); no outcome file is written and nothing is recorded for the pool clause; remedy and re-run the chain"; return 0; fi
  if [ -f "$R/topic_partition_outcome.txt" ]; then log "READOUT outcome present ($R/topic_partition_outcome.txt); not recomputed (write-once)"; else
    wait_idle
    run "topic partition readout" "$R/readout_run.log" -- python tools/analysis/topic_partition.py --run
    local rc=$?; [ "$DRY" = 1 ] || log "READOUT exit $rc (log $R/readout_run.log; outcome $R/topic_partition_outcome.txt)"
  fi
}

# ---- T2 contingency (I4) --------------------------------------------------------------------------------------
t1_not_built() {  # trigger: the vacuity guard fired, no snapshot, or leaves <= 7
  local bout=$R/ng_af_s42.build.out
  [ -f "$bout" ] || return 0
  grep -q 'construction ended with the root as a single leaf' "$bout" && return 0
  grep -q 'Snapshot ID:' "$bout" || return 0
  local lv; lv=$(grep -o 'leaves=[0-9]*' "$bout" | tail -1 | cut -d= -f2)
  [ -n "$lv" ] && [ "$lv" -le 7 ] && return 0
  return 1
}

t2_bar() {  # prints the I4 bar from T1's proposals.csv (clipped to [BAR_LO, BAR_HI]); the mechanism on stderr
  python - "$R/ng_af_s42/seed_42" "$R1_ROOT_SEP" "$R1_D1_REFUSED" "$BAR_LO" "$BAR_HI" <<'EOF'
import csv, re, json, os, sys
run, r1_root, r1_d1, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
RE = re.compile(r"min_pair_sep_below_bar\(sep=([0-9.]+),bar=([0-9.]+)(?:,bar_eff=([0-9.]+))?,k=(\d+),emK=(\d+)\)")
pp = os.path.join(run, "diagnostics", "proposals.csv")
if not os.path.exists(pp):
    print("no proposals.csv at %s" % pp, file=sys.stderr); sys.exit(1)
rows = list(csv.DictReader(open(pp, encoding="utf-8")))
root = rows[0]["site_id"]                      # anchor-free: the root is the only site at iteration 1
d1 = set()
sp = os.path.join(run, "dag_snapshots.jsonl")
if os.path.exists(sp):
    last = json.loads(open(sp, encoding="utf-8").readlines()[-1])
    d1 = {n["id"] for n in last["nodes"] if n["depth"] == 1}
def refused(site, k=None):
    out = []
    for r in rows:
        if r["site_id"] != site or r["decision"] != "NO_PROPOSAL":
            continue
        m = RE.search(r["reason"] or "")
        if m and (k is None or int(m.group(4)) == k):
            out.append((float(m.group(1)), int(m.group(4)), int(m.group(5)), r["iter"]))
    return out
root_k2 = refused(root, 2)
root_acc = any(r["site_id"] == root and r["decision"] == "ACCEPTED" for r in rows)
if root_k2 and not root_acc:
    sep = max(s for s, _, _, _ in root_k2)
    raw = 0.025 * sep / r1_root
    how = "root refused k=2 min-pair %.5f (rows %s) / R1 root %.6f" % (sep, root_k2, r1_root)
else:
    d1r = [x for s in d1 for x in refused(s)]
    if not d1r:
        print("root ACCEPTED (%s) but no refused depth-1 min-pair row among %s: the I4 rule has no input" % (root_acc, sorted(d1)), file=sys.stderr); sys.exit(1)
    sep = max(s for s, _, _, _ in d1r)
    raw = 0.025 * sep / r1_d1
    how = "root ACCEPTED, collapse below it: largest refused depth-1 min-pair %.5f (rows %s) / R1's largest refused depth-1 min-pair %.5f" % (sep, d1r, r1_d1)
bar = min(hi, max(lo, raw))
print("T2 bar: 0.025 x (%s) = %.6f raw -> clipped to [%.3f, %.3f] = %.4f" % (how, raw, lo, hi, bar), file=sys.stderr)
print("%.4f" % bar)
EOF
}

t2() {
  local cfg=$CFG/ng_af_bar_eq_s42.toml
  if [ "$DRY" = 1 ] && [ ! -f "$R/ng_af_s42.build.out" ]; then
    echo "  [would decide] T2 trigger from $R/ng_af_s42.build.out (absent now): T2 runs ONLY if the vacuity guard fired, no snapshot was saved, or leaves <= 7; otherwise the template is NOT instantiated. The conditional steps would be:"
    echo "  [would compute] the I4 bar from $R/ng_af_s42/seed_42/diagnostics/proposals.csv (t2_bar: root refused k=2 min-pair / $R1_ROOT_SEP, else largest refused depth-1 min-pair / $R1_D1_REFUSED; x 0.025; clipped to [$BAR_LO, $BAR_HI]) and write $cfg from $cfg.template"
    build ng_af_bar_eq_s42 "$cfg"; sitenull ng_af_bar_eq_s42 256 '<T2 bar>'; return 0
  fi
  if t1_not_built; then
    log "T2 TRIGGER holds: T1 is NOT built (vacuity guard fired, no snapshot, or leaves <= 7); the contingency runs (I4)"
  else
    log "T2 not run: T1 built with $(grep -o 'leaves=[0-9]*' "$R/ng_af_s42.build.out" 2>/dev/null | tail -1 || echo 'leaves=?') (> 7); the template is NOT instantiated"
    [ -f "$cfg" ] && log "T2 WARNING: $cfg exists although the trigger does not hold; it is NOT used (the readout refuses a T2 build log when T1 built)"
    return 0
  fi
  if [ "$DRY" = 1 ]; then echo "  [would compute] the I4 bar from $R/ng_af_s42/seed_42/diagnostics/proposals.csv (t2_bar) and write $cfg from $cfg.template"; build ng_af_bar_eq_s42 "$cfg"; sitenull ng_af_bar_eq_s42 256 '<T2 bar>'; return 0; fi
  if [ ! -f "$cfg" ]; then
    local bar; bar=$(t2_bar 2> "$R/t2_bar.out"); local rc=$?
    cat "$R/t2_bar.out" | while read -r l; do log "  $l"; done
    [ $rc = 0 ] && [ -n "$bar" ] || { log "T2 bar could not be computed (see $R/t2_bar.out); T2 not run (C3 FAILED stands; F3)"; return 0; }
    sed "s/^proposalSeparationBar = @T2_BAR@.*$/proposalSeparationBar = $bar   # T2 (I4): computed by tools\/chains\/topic_partition.sh t2_bar, see $R\/t2_bar.out/" "$cfg.template" > "$cfg"
    grep -q '@T2_BAR@' "$cfg" && { log "T2 placeholder survived in $cfg; refusing"; rm -f "$cfg"; exit 1; }
    log "T2 config written: $cfg with proposalSeparationBar = $bar"
  else log "T2 config $cfg present (bar $(grep -o '^proposalSeparationBar = [0-9.]*' "$cfg" | cut -d' ' -f3)); reused"; fi
  local bar; bar=$(grep -o '^proposalSeparationBar = [0-9.]*' "$cfg" | cut -d' ' -f3)
  build ng_af_bar_eq_s42 "$cfg"
  sitenull ng_af_bar_eq_s42 256 "$bar"
}

# ---- main -----------------------------------------------------------------------------------------------------
[ "$DRY" = 1 ] && echo "DRY RUN: nothing is executed, nothing is logged to $CHAIN_LOG (root $(pwd))"
log "CHAIN start (dry=$DRY) HEAD $(git rev-parse --short HEAD 2>/dev/null) | order: preflight, ingest, collision check, backups, pin before, smoke, readout selftest+dry-run, T1 build, pool, T1 null, T1b build, T1b null, [T2], readout --run, pin after + acceptance"
preflight
log "==== I0 INGEST ===="
ingest
log "==== COLLISION CHECK ===="
collision_check
log "==== BACKUPS ===="
backups
log "==== PIN BEFORE ===="
pin before
log "==== I1 SMOKE ag_news_smoke_s42 ===="
build ag_news_smoke_s42
if [ "$DRY" != 1 ]; then
  sb=$R/ag_news_smoke_s42.build.out
  log "SMOKE readouts: built $(grep -q 'Snapshot ID:' "$sb" && echo yes || echo NO) / pool recorded $(grep -o '\[POOL\] recorded [^ ]*' "$sb" | tail -1 | cut -d' ' -f3) / snapshot saved $(grep -o 'Snapshot ID: [^ ]*' "$sb" | tail -1 | cut -d' ' -f3) / closure $(grep -o '\[SPLIT-CLOSURE\] [0-9]* train item' "$sb" | tail -1) / trickle ran $(grep -o 'Total Queries: [0-9]*' "$sb" | tail -1)"
fi
smoke_gate
wait_idle
log "SMOKE readout selftest + dry-run: python tools/analysis/topic_partition.py --selftest; --dry-run --arm smoke"
run "readout selftest (smoke stage)" "$R/readout_selftest_smoke.out" -- python tools/analysis/topic_partition.py --selftest
run "readout dry-run smoke" "$R/readout_dryrun_smoke.out" -- python tools/analysis/topic_partition.py --dry-run --arm smoke
[ "$DRY" = 1 ] || log "SMOKE readout: selftest $(tail -1 "$R/readout_selftest_smoke.out") | dry-run: $(grep -m1 'smoke readouts' "$R/readout_dryrun_smoke.out")"
log "==== T1 ng_af_s42 ===="
build ng_af_s42
pool_then_null ng_af_s42 256 absent
log "==== T1b ng_af_bareq512_s42 ===="
build ng_af_bareq512_s42
pool_then_null ng_af_bareq512_s42 512 0.0145
log "==== T2 CONTINGENCY ng_af_bar_eq_s42 ===="
t2
log "==== READOUT ===="
readout
log "==== PIN AFTER + ACCEPTANCE ===="
pin after
acceptance
log "CHAIN DONE"
if [ "$DRY" != 1 ]; then
  log "---- SUMMARY ----"
  for a in ag_news_smoke_s42 ng_af_s42 ng_af_bareq512_s42 ng_af_bar_eq_s42; do
    [ -f "$R/$a.build.out" ] || { log "$a: not run"; continue; }
    lv=$(grep -o 'leaves=[0-9]*' "$R/$a.build.out" | tail -1 || echo "not built")
    sn=$(grep -o 'Snapshot ID: [^ ]*' "$R/$a.build.out" | tail -1 | cut -d' ' -f3)
    if [ -f "$R/site_null_$a.csv" ]; then log "$a: ${lv:-not built} | snapshot ${sn:-none} | certified/sites $(certified "$R/site_null_$a.csv") | $(grep -o '\[SEPBAR\][^|]*' "$R/sitenull_$a.out" 2>/dev/null | tail -1)"; else log "$a: ${lv:-not built} | snapshot ${sn:-none} | no site null"; fi
  done
  log "verdict lines: $(grep -A4 '^VERDICT' "$R/topic_partition_outcome.txt" 2>/dev/null | tail -n +2 | tr '\n' ' ' | cut -c1-400)"
  log "tracked files modified (must be only the two standing local edits .gitignore / config/application.yml plus the pool id file(s) under experiment_configs/):"; git status --short | grep -v '^??' | while read -r l; do log "  $l"; done
  log "snapshots_frozen.db sha256: $(sha256sum snapshots_frozen.db 2>/dev/null | cut -c1-16)"
fi
if [ -n "$PRECOND_FAILED" ]; then log "CHAIN EXIT 3: PRECONDITION FAILED on arm(s) $PRECOND_FAILED (pool guard refusal); not an outcome"; exit 3; fi
exit 0
