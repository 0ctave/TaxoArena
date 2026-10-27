#!/bin/bash
W=/z/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/rp13-afu-run2
cd $W
T0=$(date +%s)
for m in ifeval gpqa musr math bbh mmlu_pro_lb; do
  D=experiment_results/archv2/union_af_route/AF-U/$m; mkdir -p $D
  s=$(date +%s); echo "== $m start $(date -Iseconds)"; tasklist | grep -i java || echo "no java"
  powershell -NoProfile -Command ".\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args='--config experiment_configs/union_af_route/AF-U/$m.toml'; exit \$LASTEXITCODE" 2>&1 | tee $D/build.log > /dev/null
  echo "== $m jvm rc=${PIPESTATUS[0]} wall=$(( $(date +%s)-s ))s"
  python tools/analysis/union_af_route_ops.py --member $m; r=$?; echo "== $m ops rc=$r"
  if [ $r -ne 0 ] && [ $r -ne 3 ]; then echo "== STOP at $m"; exit 1; fi
done
echo "== members done total=$(( $(date +%s)-T0 ))s"
python tools/analysis/union_af_route_ops.py --fill; r=$?; echo "== fill rc=$r"; [ $r -ne 0 ] && exit 1
D=experiment_results/archv2/union_af_route/AF-U/graft_flatleaf; mkdir -p $D; s=$(date +%s)
powershell -NoProfile -Command ".\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args='--config experiment_configs/union_af_route/AF-U/graft_flatleaf.toml'; exit \$LASTEXITCODE" 2>&1 | tee $D/build.log > /dev/null
echo "== graft rc=${PIPESTATUS[0]} wall=$(( $(date +%s)-s ))s total=$(( $(date +%s)-T0 ))s"
