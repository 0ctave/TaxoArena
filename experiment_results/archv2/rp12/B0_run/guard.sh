#!/bin/bash
# B0-2 pv2 guard (run from main; a pool reader, outside any construction window). Usage: guard.sh <label>
cd /z/FAC/TUBerlin/THESIS/TaxoArena
echo "== B0-2 GUARD [$1] $(date -Is)"
python tools/analysis/v2_union_pool.py --dry-run 2>&1; echo "v2_union_pool --dry-run rc=$?"
echo "pool file sha256 (main, LF): $(sha256sum < experiment_configs/engine_pool_pv2_1575de61bb20e977.json)"
echo "pool file sha256 (worktree, LF rendering): $(tr -d '\r' < .claude/worktrees/rp12-b0-run/experiment_configs/engine_pool_pv2_1575de61bb20e977.json | sha256sum)"
for f in multicorpus_cache_v1.db embeddings_cache.db snapshots.db data_v2/REG_ARCHV2-SPLIT-2_*/corpus_v2_union_mc6.db .claude/worktrees/rp12-b0-run/multicorpus_cache_v1.db .claude/worktrees/rp12-b0-run/embeddings_cache.db .claude/worktrees/rp12-b0-run/snapshots.db; do for s in -wal -journal; do [ -e "$f$s" ] && echo "$f$s $(stat -c %s "$f$s") bytes"; done; done; echo "(no line above = sidecar absent)"
