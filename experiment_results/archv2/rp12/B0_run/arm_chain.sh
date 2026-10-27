#!/bin/bash
# Resumable: B0p (6 members + flatLeaf graft), then o1, then o2 (6 members each), one build at a time from the pinned worktree.
# Per build: B0-2 guard before, build, counted proof, guard after, copy to main, commit by path. Stops at the first failure.
M=/z/FAC/TUBerlin/THESIS/TaxoArena; R=$M/experiment_results/archv2/rp12/B0_run; WT=$M/.claude/worktrees/rp12-b0-run
SP=/c/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad
one() { # arm tag verifier
  local A=$1 t=$2 V=$3
  [ -e $R/$A.$t.COMMITTED ] && return 0
  bash $R/guard.sh "before $A/$t" >> $R/run_log.txt 2>&1; tail -14 $R/run_log.txt | grep -q "every check passed" || { echo "GUARD FAILED before $A/$t"; return 3; }
  if [ ! -e $R/$A.$t.DONE ]; then bash $R/build_arm.sh $A $t > $R/$A.$t.build.txt 2>&1 || { echo "BUILD FAILED $A/$t"; return 1; }; fi
  (cd $R && PYTHONIOENCODING=utf-8 python $V $A $t > $A.$t.proof.txt 2>&1) || { echo "PROOF FAILED $A/$t"; tail -3 $R/$A.$t.proof.txt; return 2; }
  bash $R/guard.sh "after $A/$t" >> $R/run_log.txt 2>&1; tail -14 $R/run_log.txt | grep -q "every check passed" || { echo "GUARD FAILED after $A/$t"; return 3; }
  cd $M; mkdir -p experiment_results/archv2/rp12/$A; rm -rf experiment_results/archv2/rp12/$A/$t
  cp -r $WT/experiment_results/archv2/rp12/$A/$t experiment_results/archv2/rp12/$A/$t
  local X=""; [ -e $WT/experiment_configs/rp12/$A/$t.toml ] && [ ! -e experiment_configs/rp12/$A/$t.toml ] && { cp $WT/experiment_configs/rp12/$A/$t.toml experiment_configs/rp12/$A/; X=experiment_configs/rp12/$A/$t.toml; }
  [ -n "$X" ] && git add -- $X 2>/dev/null
  echo "[$A/$t] $(grep -h 'end .* rc=' $R/$A.$t.build.txt) ; proof: $(tail -1 $R/$A.$t.proof.txt)" >> $R/run_log.txt
  git add -- experiment_results/archv2/rp12/$A/$t experiment_results/archv2/rp12/B0_run 2>/dev/null
  printf 'RP12 ARCH-V2-E-T %s/%s built from pinned worktree 6d04e84 (D-8; C-3): %s. Zero calls.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01G2eTaTRL4d3ohsmSQnuwsE\n' "$A" "$t" "$(tail -1 $R/$A.$t.proof.txt)" > $SP/msg_arm.txt
  git commit -q -F $SP/msg_arm.txt -- experiment_results/archv2/rp12/$A/$t experiment_results/archv2/rp12/B0_run $X 2>/dev/null && touch $R/$A.$t.COMMITTED && git log -1 --format="[$A/$t] committed %h"
}
for t in bbh math musr ifeval gpqa mmlu_pro_lb; do one B0p $t verify_arm_member.py || exit 1; done
if [ ! -e $WT/experiment_configs/rp12/B0p/graft_flatleaf.toml ]; then
  A=""; for t in bbh math musr ifeval gpqa mmlu_pro_lb; do A="$A $(echo $t | tr a-z A-Z)=$(grep -o 'snapshot [0-9_A-Za-z]*$' $R/B0p.$t.proof.txt | awk '{print $2}')"; done
  (cd $WT && python tools/analysis/rp12_build_configs.py --fill experiment_configs/rp12/B0p/graft_flatleaf.toml.tmpl $A) || exit 4
fi
one B0p graft_flatleaf verify_arm_graft.py || exit 1
for a in o1 o2; do for t in bbh math musr ifeval gpqa mmlu_pro_lb; do one $a $t verify_arm_member.py || exit 1; done; done
echo ARM CHAIN DONE
