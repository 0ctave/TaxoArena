#!/bin/bash
# After one B0 member: B0-2 guard (after), copy outputs worktree -> main, commit by path. Usage: after_member.sh <tag>
set -o pipefail
M=/z/FAC/TUBerlin/THESIS/TaxoArena; R=$M/experiment_results/archv2/rp12/B0_run; WT=$M/.claude/worktrees/rp12-b0-run; t=$1
[ -e $R/$t.COMMITTED ] && { echo "[$t] already committed"; exit 0; }
cd $M
bash $R/guard.sh "after $t" >> $R/run_log.txt 2>&1
grep -q "\[UNION-POOL\] DRY RUN: every check passed" <(tail -25 $R/run_log.txt) || { echo "GUARD FAILED after $t"; exit 3; }
mkdir -p $M/experiment_results/archv2/rp12/B0
rm -rf $M/experiment_results/archv2/rp12/B0/$t
cp -r $WT/experiment_results/archv2/rp12/B0/$t $M/experiment_results/archv2/rp12/B0/$t
echo "[$t] $(grep -h 'end .* rc=' $R/$t.build.txt) ; proof: $(tail -1 $R/$t.proof.txt)" >> $R/run_log.txt
git add -- experiment_results/archv2/rp12/B0/$t experiment_results/archv2/rp12/B0_run
P=$(git diff --cached --name-only -- experiment_results/archv2/rp12/B0/$t experiment_results/archv2/rp12/B0_run)
printf 'RP12 ARCH-V2-E-T B0 member %s built from pinned worktree 6d04e84 (D-8): %s. Zero calls.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01G2eTaTRL4d3ohsmSQnuwsE\n' "$t" "$(tail -1 $R/$t.proof.txt)" > /c/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/msg_$t.txt
git commit -q -F /c/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/msg_$t.txt -- $P $EXTRA && touch $R/$t.COMMITTED && git log -1 --format="[$t] committed %h"
