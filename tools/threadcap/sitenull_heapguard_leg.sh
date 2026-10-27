#!/bin/sh
# THREAD-CAP C7-3 (READY_w0_delta2 b2ad5ef): the siteNull HEAP-GUARD refusal leg on the MERGED code (THREAD-CAP + EMBEDDER-
# PLUMBING), on its OWN stub cache. Since w0-delta3 the heap guard runs BEFORE the embedder guard (it needs only the frozen
# snapshot's site sizes and siteConfig; it opens no DB), so a 128m heap refuses before the stub cache is ever opened.
# Expects, from one run (-PjvmThreads=12 -PnullReps=24 -DsiteNullHeap=128m, the frozen snapshot of the worktree's tracked
# snapshots_frozen.db, read-only):
#   HEAP-line     [THREAD-CAP] requested=12 availableProcessors=12 heapEstimate=<x.xx>GB budget=0.1<x>GB (the guard-site line)
#   HEAP-refused  [SITENULL-HEAP] REFUSING before the first replicate
#   HEAP-first    NO [EMB-GUARD] line at all: the embedder guard never ran (the execution discriminator of the new order; on
#                 481b613 the embedder guard refused the stub first: "raw vector dimensions {} != {4096}")
#   HEAP-nocsv    the -DoutCsv file was not created
#   HEAP-stub     the stub's sha256 is unchanged
# Zero calls; no DB of record is opened or written. Fail-safe: refuses in the main checkout; an existing embeddings_cache.db
# must be a stub < 1 MB (moved aside, restored by trap, byte-compared); the leg's own stub is an EMPTY SQLite file with the
# embeddings / queries tables (created with python's sqlite3, deleted by trap).
# Usage (from a worktree): sh tools/threadcap/sitenull_heapguard_leg.sh   -> exit 0 iff 5/5 OK.
W=$(git rev-parse --show-toplevel) || exit 1
cd "$W" || exit 1
[ "$(git rev-parse --git-dir)" = ".git" ] && { echo "REFUSING: main checkout (run in a worktree)"; exit 2; }
T=$(mktemp -d) || exit 1
ASIDE=""
if [ -e embeddings_cache.db ]; then
  sz=$(wc -c < embeddings_cache.db)
  [ "$sz" -lt 1048576 ] || { echo "REFUSING: embeddings_cache.db is $sz bytes (not a stub)"; exit 2; }
  ASIDE=embeddings_cache.db.heapleg_aside; sum0=$(sha256sum embeddings_cache.db | cut -c1-64)
  mv embeddings_cache.db "$ASIDE"
fi
cleanup() {
  rm -f "$W/embeddings_cache.db"
  if [ -n "$ASIDE" ]; then mv "$W/$ASIDE" "$W/embeddings_cache.db"; echo "prior stub restored sha256 $(sha256sum "$W/embeddings_cache.db" | cut -c1-64) (before $sum0)"; fi
  rm -rf "$T"
}
trap cleanup EXIT
python -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute('CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)'); c.execute('CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, ground_truth_category TEXT, query_id INTEGER)'); c.commit(); c.close()" embeddings_cache.db || exit 1
st0=$(sha256sum embeddings_cache.db | cut -c1-64)
echo "own stub embeddings_cache.db $(wc -c < embeddings_cache.db) bytes sha256 $st0"
O=$(./gradlew --offline --max-workers=2 --no-build-cache siteNull --console=plain -PjvmThreads=12 -PnullReps=24 -DsiteNullHeap=128m -DoutCsv="$T/guard_should_not_exist.csv" 2>&1)
echo "$O" | grep -a -E 'THREAD-CAP|EMB-GUARD|EMB-CACHE|SITENULL-HEAP\] (REFUSING|sliceDim)|BUILD' | head -10
OK=0; BAD=0
chk() { if [ "$2" = 1 ]; then OK=$((OK+1)); echo "EXPECT $1 OK"; else BAD=$((BAD+1)); echo "EXPECT $1 MISSING"; fi; }
chk HEAP-line "$(echo "$O" | grep -a -q -E '^ *\[THREAD-CAP\] requested=12 availableProcessors=12 heapEstimate=[0-9]+\.[0-9]{2}GB budget=0\.1[0-9]GB' && echo 1)"
chk HEAP-refused "$(echo "$O" | grep -a -q -F '[SITENULL-HEAP] REFUSING before the first replicate' && echo 1)"
chk HEAP-first "$(echo "$O" | grep -a -q -F '[EMB-GUARD]' || echo 1)"
chk HEAP-nocsv "$([ ! -e "$T/guard_should_not_exist.csv" ] && echo 1)"
chk HEAP-stub "$([ "$(sha256sum embeddings_cache.db | cut -c1-64)" = "$st0" ] && echo 1)"
echo "== HEAP-GUARD LEG SUMMARY OK=$OK MISSING=$BAD"
[ "$BAD" = 0 ]
