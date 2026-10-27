#!/bin/bash
# Resumable B0 member build. Usage: build_member.sh <tag>   (tag = bbh|math|musr|ifeval|gpqa|mmlu_pro_lb)
# Skips if <tag>.DONE exists. Runs from the pinned worktree (D-8), -PjvmThreads=12 (the TOML's registered launch line).
R=/z/FAC/TUBerlin/THESIS/TaxoArena/experiment_results/archv2/rp12/B0_run
WT=/z/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/rp12-b0-run
t=$1
[ -e $R/$t.DONE ] && { echo "[$t] already DONE, skipped"; exit 0; }
cd $WT || exit 9
[ "$(git rev-parse HEAD)" = 6d04e840f1a23af438e48bbae7699ee9ce4f5971 ] || { echo "worktree HEAD moved"; exit 8; }
if [ -d experiment_results/archv2/rp12/B0/$t ]; then mv experiment_results/archv2/rp12/B0/$t experiment_results/archv2/rp12/B0/${t}_partial_$(date +%s); echo "moved partial output aside"; fi
echo "[$t] start $(date -Is) cmd: ./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args=\"--config experiment_configs/rp12/B0/$t.toml\""
s=$(date +%s)
./gradlew.bat bootRun --console=plain --offline -PjvmThreads=12 --args="--config experiment_configs/rp12/B0/$t.toml"
rc=$?
echo "[$t] end $(date -Is) rc=$rc wall_s=$(( $(date +%s)-s ))"
[ $rc = 0 ] && touch $R/$t.DONE
exit $rc
