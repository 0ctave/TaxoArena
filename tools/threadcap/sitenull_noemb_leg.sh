#!/bin/sh
# THREAD-CAP C7-1 (READY_w0_delta1 fd6a349): the siteNull leg with NO embeddings_cache.db, the FIRST
# Assumption path. Run WITHOUT -DembeddingCacheFile (post-RP08 default path). Expects, from one run:
#   NOEMB-line    [THREAD-CAP] requested=12 availableProcessors=12 heapEstimate=n/a budget=...
#   NOEMB-guard   [EMB-GUARD] not run: embeddings_cache.db not present (the test is skipped)
#   NOEMB-order   the THREAD-CAP line precedes the EMB-GUARD line (it is printed before the Assumption)
#   NOEMB-skipped the JUnit XML reports skipped="1"
# Kills the reviewer's Y1 (the THREAD-CAP print moved after the first assumeTrue): NOEMB-line MISSING.
# Zero calls, no DB opened. Fail-safe: refuses in the main checkout; if the worktree has an
# embeddings_cache.db it must be a stub < 1 MB (never a DB of record); it is moved aside and restored
# by trap, byte-compared.
# Usage (from a worktree): sh tools/threadcap/sitenull_noemb_leg.sh   -> exit 0 iff 4/4 OK.
W=$(git rev-parse --show-toplevel) || exit 1
cd "$W" || exit 1
[ "$(git rev-parse --git-dir)" = ".git" ] && { echo "REFUSING: main checkout (run in a worktree)"; exit 2; }
ASIDE=""
if [ -e embeddings_cache.db ]; then
  sz=$(wc -c < embeddings_cache.db)
  [ "$sz" -lt 1048576 ] || { echo "REFUSING: embeddings_cache.db is $sz bytes (not a stub)"; exit 2; }
  ASIDE=embeddings_cache.db.noemb_aside; sum0=$(sha256sum embeddings_cache.db | cut -c1-64)
  mv embeddings_cache.db "$ASIDE"
  trap 'mv "$W/$ASIDE" "$W/embeddings_cache.db"; echo "stub restored sha256 $( sha256sum "$W/embeddings_cache.db" | cut -c1-64) (before $sum0)"' EXIT
fi
[ -e embeddings_cache.db ] && { echo "REFUSING: embeddings_cache.db still present"; exit 2; }
O=$(./gradlew --offline --max-workers=2 --no-build-cache siteNull --console=plain -PjvmThreads=12 -PnullReps=0 2>&1)
echo "$O" | grep -a -E 'THREAD-CAP|EMB-GUARD|EMB-CACHE|SKIPPED|BUILD' | head -8
OK=0; BAD=0
chk() { if [ "$2" = 1 ]; then OK=$((OK+1)); echo "EXPECT $1 OK"; else BAD=$((BAD+1)); echo "EXPECT $1 MISSING"; fi; }
lc=$(echo "$O" | grep -a -n -E '^ *\[THREAD-CAP\] requested=12 availableProcessors=12 heapEstimate=n/a budget=' | head -1 | cut -d: -f1)
lg=$(echo "$O" | grep -a -n -F '[EMB-GUARD] not run: embeddings_cache.db not present (the test is skipped)' | head -1 | cut -d: -f1)
chk NOEMB-line "$([ -n "$lc" ] && echo 1)"
chk NOEMB-guard "$([ -n "$lg" ] && echo 1)"
chk NOEMB-order "$([ -n "$lc" ] && [ -n "$lg" ] && [ "$lc" -lt "$lg" ] && echo 1)"
X=build/test-results/siteNull/TEST-taxonomy.SeparationNullBySizeTest.xml
chk NOEMB-skipped "$(grep -a -q 'skipped="1"' "$X" 2>/dev/null && echo 1)"
echo "== NOEMB SUMMARY OK=$OK MISSING=$BAD"
[ "$BAD" = 0 ]
