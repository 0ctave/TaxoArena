#!/bin/bash
# INTENT-TRANSFER-S1: nine builds, one at a time, from the detached worktree at f6485dee. Stops on any refusal / rc!=0 / WAL tail.
W=/z/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/intent-s1-run
M=/z/FAC/TUBerlin/THESIS/TaxoArena
O=$M/experiment_results/intent_s1/ops_20261003
cd $W; export TAXOARENA_DATA_ROOT=$W
declare -A EMB=( [qwen3]=intent_emb_qwen3.db [gemma]=intent_emb_gemma.db )
declare -A PIN=( [qwen3]=9e100e04fc91b137a075b8abedbc87d2b29a6dc2244c5f242b1c587004a4ee74 [gemma]=b187b82f90ce98376ba3ffac100157493fd8c5ee52dfa88f707738dde2acf512 )
declare -A TAG=( [qwen3]=qwen3-embedding:latest [gemma]=embeddinggemma:latest )
T0=$(date +%s)
for spec in m_af:qwen3 m_af_replay:qwen3 m_o1:qwen3 m_o2:qwen3 m_af_s2:qwen3 m_an:qwen3 c_af:qwen3 c_an:qwen3 m_af_g:gemma; do
  slug=${spec%%:*}; e=${spec##*:}; out=experiment_results/intent_transfer/s1/$slug
  echo "== $slug start $(date -Iseconds)"; tasklist | grep -i -E "java|python" || echo "no java/python"
  [ -e $out ] && { echo "== STOP: $out exists"; exit 1; }
  mkdir -p $out; rid=${slug}_$(date +%Y%m%d_%H%M%S); wd=$W/intent_s1_work/$rid; mkdir -p $wd
  cp $W/${EMB[$e]} $wd/; s=$(sha256sum $wd/${EMB[$e]} | cut -d' ' -f1); echo "copy $wd/${EMB[$e]} sha256 $s"
  [ "$s" = "${PIN[$e]}" ] || { echo "== STOP: copy sha != pin"; exit 1; }
  st=$(date +%s)
  powershell -NoProfile -Command "cmd /c '.\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 \"-Dtaxoarena.embeddingCacheFile=$(cygpath -w $wd/${EMB[$e]})\" \"-Dtaxoarena.embeddingCacheSourceSha256=${PIN[$e]}\" \"-Dtaxoadapt.llm.embedding-model=${TAG[$e]}\" \"-Dranking.db.path=$out/ratings_intent_s1.db\" --args=\"--config experiment_configs/intent_s1/$slug.toml\" > $out/build.log 2>&1'; exit \$LASTEXITCODE"
  rc=$?; echo "== $slug jvm rc=$rc wall=$(( $(date +%s)-st ))s"
  cp $out/build.log $O/build_$slug.log
  grep -a -m3 -E "\[INTENT\] fetched|REFUS|Snapshot ID" $out/build.log
  echo "leaves (last dag_snapshots line): $(tail -1 $out/seed_42/dag_snapshots.jsonl 2>/dev/null | python -c "import sys,json;d=json.loads(sys.stdin.read());print({k:v for k,v in d.items() if 'leaf' in k.lower() or k in ('nodes','numLeaves','leaves')} if isinstance(d,dict) else '?')" 2>&1 | cut -c1-200)"
  echo "copy after: $(sha256sum $wd/${EMB[$e]} | cut -c1-16)"
  for d in $W/embeddings_cache.db $W/mmlu_pro_dataset_cache_v2.db $W/snapshots.db $M/embeddings_cache.db $M/mmlu_pro_dataset_cache_v2.db $M/snapshots.db; do
    for x in -wal -journal; do [ -s $d$x ] && { echo "== STOP: WAL/journal tail $d$x $(stat -c %s $d$x) bytes (checkpoint is the author's)"; exit 2; }; done
  done; echo "no WAL tail on shared DBs"
  python $O/tablehash.py $W/embeddings_cache.db $W/mmlu_pro_dataset_cache_v2.db $W/snapshots.db
  [ $rc -ne 0 ] && { echo "== STOP at $slug rc=$rc"; exit 1; }
done
echo "== all done total=$(( $(date +%s)-T0 ))s $(date -Iseconds)"
