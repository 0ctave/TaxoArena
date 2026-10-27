#!/bin/bash
# Resumable lane-r2 build chain, one build at a time from the pinned worktree (D-8). Per build: W1-W5, B0-2 guard before,
# build (-PjvmThreads=12, --no-daemon), counted proof, guard after, copy worktree -> main (rp12_r2 only), commit by path.
# Usage: chain.sh B0 | chain.sh arms     Stops at the first failure.
M=/z/FAC/TUBerlin/THESIS/TaxoArena; R=$M/experiment_results/archv2/rp12_r2/B0_run; WT=$M/.claude/worktrees/rp12-r2-run
PIN=2703f2c25807393605f863345c3dc0c8bd132849
SP=/c/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad
MEM="bbh math musr ifeval gpqa mmlu_pro_lb"
build() { # arm tag
  local A=$1 t=$2
  [ -e $R/$A.$t.DONE ] && { echo "[$A/$t] already DONE, skipped"; return 0; }
  cd $WT || return 9
  [ "$(git rev-parse HEAD)" = $PIN ] || { echo "worktree HEAD moved"; return 8; }
  [ -d experiment_results/archv2/rp12_r2/$A/$t ] && { mv experiment_results/archv2/rp12_r2/$A/$t experiment_results/archv2/rp12_r2/$A/${t}_partial_$(date +%s); echo "moved partial output aside"; }
  echo "[$A/$t] start $(date -Is) cmd: ./gradlew.bat bootRun --console=plain --offline --no-daemon -PjvmThreads=12 --args=\"--config experiment_configs/rp12_r2/$A/$t.toml\""
  local s=$(date +%s)
  ./gradlew.bat bootRun --console=plain --offline --no-daemon -PjvmThreads=12 --args="--config experiment_configs/rp12_r2/$A/$t.toml"
  local rc=$?
  echo "[$A/$t] end $(date -Is) rc=$rc wall_s=$(( $(date +%s)-s ))"
  [ $rc = 0 ] && touch $R/$A.$t.DONE
  return $rc
}
g() { tail -16 $R/run_log.txt | grep -q "\[UNION-POOL\] DRY RUN: every check passed"; }
one() { # arm tag
  local A=$1 t=$2
  [ -e $R/$A.$t.COMMITTED ] && return 0
  bash $R/w15.sh >> $R/run_log.txt 2>&1 || { echo "W1-W5 BREACH before $A/$t"; return 5; }
  bash $R/guard.sh "before $A/$t" >> $R/run_log.txt 2>&1; g || { echo "GUARD FAILED before $A/$t"; return 3; }
  if [ ! -e $R/$A.$t.DONE ]; then (build $A $t) > $R/$A.$t.build.txt 2>&1 || { echo "BUILD FAILED $A/$t"; return 1; }; fi
  (cd $R && PYTHONIOENCODING=utf-8 python verify.py $A $t > $A.$t.proof.txt 2>&1) || { echo "PROOF FAILED $A/$t"; tail -3 $R/$A.$t.proof.txt; return 2; }
  bash $R/guard.sh "after $A/$t" >> $R/run_log.txt 2>&1; g || { echo "GUARD FAILED after $A/$t"; return 3; }
  cd $M; mkdir -p experiment_results/archv2/rp12_r2/$A; rm -rf experiment_results/archv2/rp12_r2/$A/$t
  cp -r $WT/experiment_results/archv2/rp12_r2/$A/$t experiment_results/archv2/rp12_r2/$A/$t
  local X=""; if [ -e $WT/experiment_configs/rp12_r2/$A/$t.toml ] && [ ! -e experiment_configs/rp12_r2/$A/$t.toml ]; then cp $WT/experiment_configs/rp12_r2/$A/$t.toml experiment_configs/rp12_r2/$A/; X=experiment_configs/rp12_r2/$A/$t.toml; git add -- $X; fi
  echo "[$A/$t] $(grep -h 'end .* rc=' $R/$A.$t.build.txt) ; proof: $(tail -1 $R/$A.$t.proof.txt)" >> $R/run_log.txt
  git add -- experiment_results/archv2/rp12_r2/$A/$t experiment_results/archv2/rp12_r2/B0_run 2>/dev/null
  printf 'RP12 ARCH-V2-E-T-R2 lane r2 %s/%s built from pinned worktree M 2703f2c2 (D-8; C-1): %s. Zero calls.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01G2eTaTRL4d3ohsmSQnuwsE\n' "$A" "$t" "$(tail -1 $R/$A.$t.proof.txt)" > $SP/msg_r2.txt
  git commit -q -F $SP/msg_r2.txt -- experiment_results/archv2/rp12_r2/$A/$t experiment_results/archv2/rp12_r2/B0_run $X && touch $R/$A.$t.COMMITTED && git log -1 --format="[$A/$t] committed %h"
}
fill() { # arm graft
  local A=$1 gt=$2
  [ -e $WT/experiment_configs/rp12_r2/$A/$gt.toml ] && return 0
  local S=""; for t in $MEM; do S="$S $(echo $t | tr a-z A-Z)=$(grep -o 'snapshot [0-9_A-Za-z]*$' $R/$A.$t.proof.txt | awk '{print $2}')"; done
  echo "== FILL $A/$gt $(date -Is):$S" >> $R/run_log.txt
  (cd $WT && python tools/analysis/rp12_build_configs.py --lane r2 --fill experiment_configs/rp12_r2/$A/$gt.toml.tmpl $S) >> $R/run_log.txt 2>&1 || return 4
}
c3() { # C-3: parse the filled graft TOMLs (ConfigParsesTest walks *.toml recursively) before any graft launch
  [ -e $R/C3.$1.DONE ] && return 0
  echo "== C-3 [$1] $(date -Is): ConfigParsesTest in the pinned worktree; filled TOMLs: $(cd $WT && ls experiment_configs/rp12_r2/*/graft_*.toml | tr '\n' ' ')" >> $R/run_log.txt
  (cd $WT && ./gradlew.bat test --offline --no-daemon --console=plain --no-build-cache --rerun-tasks --tests taxonomy.runner.ConfigParsesTest) > $R/C3.$1.txt 2>&1; local rc=$?
  local x=$WT/build/test-results/test/TEST-taxonomy.runner.ConfigParsesTest.xml
  echo "C-3 gradle rc=$rc; $(grep -o '<testsuite [^>]*' $x | grep -o 'tests="[0-9]*"\|failures="[0-9]*"\|errors="[0-9]*"\|timestamp="[^"]*"' | tr '\n' ' ')" >> $R/run_log.txt
  cp $x $R/C3.$1.ConfigParsesTest.xml
  [ $rc = 0 ] && grep -q '^> Task :test$' $R/C3.$1.txt && ! grep -q 'Task :test FROM-CACHE\|Task :test UP-TO-DATE' $R/C3.$1.txt && grep -q 'failures="0"' $x && grep -q 'errors="0"' $x && touch $R/C3.$1.DONE
}
case $1 in
B0)
  for t in $MEM; do one B0 $t || exit 1; done
  fill B0 graft_flatleaf || exit 4; fill B0 graft_descent || exit 4
  c3 B0 || { echo "C-3 FAILED B0"; exit 6; }
  one B0 graft_flatleaf || exit 1; one B0 graft_descent || exit 1
  echo B0 CHAIN DONE;;
arms)
  for t in $MEM; do one B0p $t || exit 1; done
  fill B0p graft_flatleaf || exit 4
  c3 B0p || { echo "C-3 FAILED B0p"; exit 6; }
  one B0p graft_flatleaf || exit 1
  for a in o1 o2; do for t in $MEM; do one $a $t || exit 1; done; done
  echo ARM CHAIN DONE;;
esac
