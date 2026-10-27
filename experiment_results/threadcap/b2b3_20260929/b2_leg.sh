#!/usr/bin/env bash
# THREAD-CAP B2 leg runner (run-operator, 2026-09-29). usage: b2_leg.sh <label> <N> <stage root>
# One worktree (.claude/worktrees/threadcap-b2 at 32c4c72) for all three legs: before each leg the worktree's
# leg-written paths are removed and the two input DBs are re-copied BYTE-IDENTICAL from main (main is only copied,
# never opened); after the leg its outputs are MOVED to <stage>/<label>/ in the layout d9b_compare.py reads.
set -u
L=$1; N=$2; ST=$3
MAIN=/z/FAC/TUBerlin/THESIS/TaxoArena; WT=$MAIN/.claude/worktrees/threadcap-b2
OUT=experiment_results/topic_partition/ag_news_smoke_s42
LD=$ST/$L; [ -e "$LD" ] && { echo "[B2] refusing: $LD exists"; exit 2; }
mkdir -p "$LD/root/experiment_results/topic_partition"
cd "$WT" || exit 2
rm -rf "$OUT" ag_news_smoke_cache_v1.db ag_news_smoke_cache_v1.db-wal ag_news_smoke_cache_v1.db-shm embeddings_cache.db embeddings_cache.db-wal embeddings_cache.db-shm ratings_tc_*.db* snapshots.db snapshots.db-wal snapshots.db-shm reserved_test_queries.json
cp "$MAIN/ag_news_smoke_cache_v1.db" "$MAIN/ag_news_smoke_cache_v1.db.manifest.json" "$MAIN/embeddings_cache.db" .
sha256sum ag_news_smoke_cache_v1.db embeddings_cache.db > "$LD/inputs.sha256"
echo "[B2] leg $L N=$N start $(date -Iseconds)" | tee "$LD/leg.txt"
T0=$(date +%s)
./gradlew.bat bootRun --console=plain --offline --no-daemon --no-build-cache -PjvmThreads=$N "-Dranking.db.path=ratings_tc_$L.db" --args="--config experiment_configs/topic_partition/ag_news_smoke_s42.toml" > "$LD/bootrun.log" 2>&1
RC=$?
T1=$(date +%s)
echo "[B2] leg $L N=$N end $(date -Iseconds) EXIT $RC wall_s $((T1-T0))" | tee -a "$LD/leg.txt"
grep -a "\[THREAD-CAP\]" "$LD/bootrun.log" | tee -a "$LD/leg.txt"
git status --short --untracked-files=all | sed 's/^/[B2] wt-status /' >> "$LD/leg.txt"
mv "$OUT" "$LD/root/experiment_results/topic_partition/"
for f in ag_news_smoke_cache_v1.db ag_news_smoke_cache_v1.db-wal ag_news_smoke_cache_v1.db-shm; do [ -e "$f" ] && mv "$f" "$LD/root/"; done
exit $RC
