#!/bin/bash
# Resumable chain of the remaining B0 members; stops at the first failed build, proof or guard.
R=/z/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/archv2/rp12/B0_run
for t in "$@"; do
  if [ ! -e $R/$t.DONE ]; then bash $R/build_member.sh $t > $R/$t.build.txt 2>&1 || { echo "BUILD FAILED $t"; exit 1; }; fi
  (cd $R && PYTHONIOENCODING=utf-8 python verify_member.py $t > $t.proof.txt 2>&1) || { echo "PROOF FAILED $t"; tail -3 $R/$t.proof.txt; exit 2; }
  bash $R/after_member.sh $t 2>/dev/null || { echo "AFTER FAILED $t"; exit 3; }
done
echo CHAIN DONE
